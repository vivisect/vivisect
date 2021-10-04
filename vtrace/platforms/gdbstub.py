"""
This file contains the GDB stub code for both clients and servers. The generic 
protocol code is contained in GdbStubBase, while the client-specific code is
located in GdbClientStub and the server-specific code is in GdbServerStub. By
client we mean the code sending commands (e.g. GDB) and server we mean the code
driving the execution engine (e.g. QEMU, gdbserver, Vivisect emulator,
etc...).

The protocol itself is relatively simple and is documented here:
    https://sourceware.org/gdb/onlinedocs/gdb/Remote-Protocol.html

Adding support for new architectures requires adding the register ordering for
that architecture to gdb_reg_fmts.py. The order of the register in each list is
very important. If that list does not match between the client and the server,
then interaction with registers will fail. The order of registers seems to be
set by the server, and is not consistent (in my experience). However, it seems
like the order displayed after running 'i r all' is  usually the order you want
to follow.

Consuming the client and server stubs should be done via inheritance.
"""

import time 
import errno
import base64
import struct
import logging
import socket
import binascii
from . import gdb_reg_fmts
import envi.common as e_cmn

from itertools import groupby

logger = logging.getLogger(__name__)

e_cmn.initLogging(logger, level=logging.INFO)

class GdbStubBase:
    def __init__(self, arch, addr_size, le, reg, port):
        """ 
        Base class for consumers of GDB protocol for remote debugging.

        Args:
            arch (str): The architecture of the target being debugged.

            addr_size (int): The addresss size of the target being debugged 
            in bits (e.g. 64 for x86_64)

            le (bool): True if the byte storage used by the debugged target is 
            little-endian, False if big-endian.

            reg (list): The list of registers monitored by the debugger. The 
            order of this list is very important, and must be the same 
            used for both the client and server. If not, parsing of register 
            packets will fail. The list itself contains sets of register names
            (str) and register sizes (int) in bits (e.g. ('rip', 64)).

            port (int): The port the debug target listens on.

        Returns:
            None
        """
        self._gdb_port = port
        self._arch = arch
        self._gdb_reg_fmt = reg

        # socket overwhich the client talks to the server
        self._gdb_sock = None

        # The list of supported features for a given client-server session
        #TODO: complete the list, but for now the only thing we care about is
        # PacketSize
        self._supported_features = {
                b'Supported': None,
                b'PacketSize': None,
                b'QPassSignals': None,
                b'qXfer:memory-map:read': None,
                b'qXfer:features:read': None,
                b'QStartNoAckMode': None,
                }

        self._le = le
        self._addr_size = addr_size

    def _decodeGDBVal(self, val):
        """
        Decodes a value from a GDB string into an int.

        Args:
            val (str): A value in GDB string format.

        Returns:
            int: The equivalent int value of the supplied string.
        """
        val_str = val
        if self._le:
            val_str = self._swapEndianness(val)
        return self._atoi(val_str)

    def _encodeGDBVal(self, val, size=None):
        """
        Encodes an int to its GDB compliant format.

        Args:
            val (int): A int value to convert.

            size (int): The size of the integer in bits (e.g. uint64 -> 64) 
            for padding purposes. If the val does not need to be padded, 
            then no size needs to be provided.

        Returns:
            str: The int value as a GDB encoded string.
        """
        val_str = self._itoa(val)
        
        if size is not None:
            val_str = self._padHexString(val_str, size)
       
        if self._le:
            val_str = self._swapEndianness(val_str)
        
        return val_str

    def _gdbCSum(self, cmd):
        """
        Generates a GDB-compliant checksum for a command
        
        Args:
            cmd (str): command to be checksum-ed

        Returns:
            int: the GDB-compliant checksum of the provided command
        """
        sum = 0
        for b in cmd:
            sum += b
        return sum & 0xff

    def _buildPkt(self, cmd):
        """
        Builds a GDB command packet from a raw command.

        Args:
            cmd (str): command to be checksum-ed
        
        Returns:
            str: a GDB command packet        
        """
        return b'$%s#%.2x' % (cmd, self._gdbCSum(cmd))

    def _transPkt(self, pkt):
        """
        Transmits a packet over a socket connection

        Args:
            pkt (str): packet to send to target

        Returns:
            None
        """
        if self._gdb_sock is None:
            raise Exception('No socket available for transmission')

        logger.debug('Transmitting packet: %s' % (pkt))
        self._gdb_sock.sendall(pkt)
    
    def _recvResponse(self):
        """
        Handles receiving data over the server-client socket.

        Args:
            None

        Returns:
            None
        """
        res = self._gdb_sock.recv(1)
        status = None

        if len(res) == 0:
            raise Exception('Socket not responding')

        # If this is an acknowledgment packet, return early
        if (res == b'+') or (res == b'-'):
            return res
        elif res == b'$':
            pass
        else:
            res = res + self._gdb_sock.recv(10)
            raise Exception('Received unexpected packet: %s' % res)

        pkt = b'$%s' % self._recvUntil(b'#')
        logger.debug('_recvMessage: pkt=%r' % pkt)
        msg_data = self._parseMsg(pkt)

        expected_csum = int(self._gdb_sock.recv(2), 16)
        actual_csum = self._gdbCSum(msg_data)

        if expected_csum != actual_csum:
            raise Exception('Invalid packet data checksum')

        decoded = self._lengthDecode(msg_data)
        logger.info('_recvMessage: decoded=%r' % decoded)
        return decoded

    def _parseMsg(self, pkt):
        """
        Removes the protocol delimiters from a given packet.
        
        Args:
            pkt (str): A GDB protocol packet.

        Returns:
            str: The contents of the packet
        """
        cmd_data = pkt
        if b'#' in pkt:
            cmd_data = cmd_data.split(b'#')[0]
        cmd_data = cmd_data[1:]

        return cmd_data

    def _recvUntil(self, c):
        """
        Recieve data from the socket until the specified character is reached.

        Args:
            c (str): the character to read until.

        Returns:
            str: The characters read up until and including the delimiting
            character.
        """
        ret = []
        while not c in ret:
            x = self._gdb_sock.recv(1)
            if len(x) == 0:
                raise Exception('Socket closed unexpectedly')
            ret.append(x)
            
        #logger.debug('_recvUntil(%r):  %r', c, ret)
        return b''.join(ret)

    def _msgExchange(self, msg, expect_res= True):
        """
        Handles a message transaction (sending a message and receiving a 
        response).

        Args:
            msg (str): The msg to send to the target.

            expect_res (bool): True if the sender expects both an ack and a response, 
            False if the sender only expects an ack.

        Returns:
            str: the response from the target.
        """
        #logger.debug('_msgExchange: %r %r', msg, expect_res)
        retry_count = 0
        retry_max = 10
        status = None
        res = None

        # Send the command until its receipt is acknowledged
        while (status != b'+') and (retry_count < retry_max):
            self._sendMsg(msg)
            status = self._recvResponse()
            retry_count += 1    

        # Return the response
        if expect_res:
            res = self._recvResponse()
            # Acknowledge receipt of the packet
            self._sendAck()
        else:
            res = status
        
        return res

    def _sendAck(self):
        """
        Sends an acknowledgment packet.

        Args:
            None

        Returns:
            None
        """
        self._transPkt(b'+')

    def _sendRetrans(self):
        """
        Sends a re-transmit request packet.

        Args:
            None

        Returns:
            None
        """
        self._transPkt(b'-')

    def _disconnectSocket(self):
        """
        Closes the socket connection between the client and the server.
        
        Args:
            None

        Returns:
            None
        """
        if self._gdb_sock is not None:
            self._gdb_sock.shutdown(2)
            self._gdb_sock.close()
            self._gdb_sock = None

            
    def _buildRegPkt(self, reg_state):
        """
        Constructs a register packet from the current register state.

        Args:
            reg_state (dict): Dict of register name (str) and value (int) 
            pairs.

        Returns:
            str: The body of a GDB register packet.
        """
        reg_pkt = b''
        reg_cnt = len(reg_state)
        reg_updated = 0
        for r in self._gdb_reg_fmt:
            reg_name = r[0]

            # Only updated the registers supported by the server
            if reg_updated >= reg_cnt:
                break

            # size in bytes
            reg_size = r[1] // 8
            reg_val = reg_state[reg_name]
           
            reg_val = self._encodeGDBVal(reg_val, r[1])

            # two ascii characters per byte
            write_size = reg_size * 2
            if reg_size != len(reg_val) // 2:
                raise Exception('Attempt to store %d byte value in %d byte register' 
                        % (len(reg_val) // 2, reg_size))
            
            reg_pkt += reg_val
            reg_updated += 1

        return reg_pkt

    def _parseRegPacket(self, pkt):
        """
        Parses the body of a GDB register data packet.

        Args: 
            pkt (str): The register data packet (GDB protocol format) to be
            parsed.

        Returns:
            dict: A dictionary of register names (str) and register value
            (int) pairs.
        """
        regs = {}
        offset = 0
        for r in self._gdb_reg_fmt:
            # GDB server doesn't have to send all registers, so bail if we 
            # run out of data
            if offset >= len(pkt):
                break
            reg_name = r[0]

            # convert bits to bytes
            reg_size = r[1] // 8
            # each byte is a two digit hex number
            read_size = reg_size * 2
            reg_val = pkt[offset:offset + read_size]
            # convert to an int
            reg_val = self._decodeGDBVal(reg_val)

            regs[reg_name] = reg_val
            offset += read_size

        return regs
    
    def _lengthEncode(self, data):
        """
        Encodes data with GDB's length encoding scheme.

        Args:
            data (str): The data to encode.

        Returns:
            str: The encoded data.
        """
        max_rep = 97
        grouped = [b''.join([b'%c' % x for x in g]) for _, g in groupby(data)]
        enc_data = b''
        for g in grouped:
            length = len(g)
            char = g[0:1]
            # Special handling for b'#' (6 + 29)
            if length == 6:
                enc_data += b'%s\"%s' % (char, char)
            # Special handling for b'$' (7 + 29)
            elif length == 7:
                enc_data += b'%s\"%s%s' % (char, char, char)
            # GDB only supports encoded up to 126 repetitions
            elif length > max_rep:
                q, r = divmod(length, max_rep)
                # Split into chunks of 126 repetitions
                chunk = b'%s*%s' % (char, b'%c' % (max_rep + 29))
                enc_data += chunk * q
                # Handle the remainder
                if r == 6:
                    enc_data += b'%s\"%s' % (char, char)
                elif r == 7:
                    enc_data += b'%s\"%s%s' % (char, char, char)
                else:
                    enc_data += b'%s*%s' % (char, b'%c' % (r + 29))
            elif length > 2:
                rep_count = length - 1
                enc_data += b'%s*%s' % (char, b'%c' % (rep_count + 29))
            else:
                enc_data += g

        return enc_data

    def _lengthDecode(self, data):
        """
        Decodes data encoded in GDB's length encoding scheme.

        Args: 
            data (str): The data to decode.

        Returns:
            str: The decoded data.
        """
        dec_data = b''
        i = 0
        while i < len(data):
            char = data[i:i+1]
            if char != b'*':
                dec_data += char
                i += 1
                continue
           
            rep_count = b'%s' % data[i+1:i+2]
            rep_count = ord(rep_count) - 29
            dec_data += data[i-1:i] * rep_count
            i += 2

        return dec_data

    def _itoa(self, val):
        """
        Converts an integer to a string of that integer's hex value (e.g. 
        65 -> '41').
        
        Args:
            val (int): The integer to convert to a string of hex values.

        Returns:
            str: The string of hex characters of the provided integer.
        """
        val_str = b'%x' % val
        if len(val_str) % 2 != 0:
            val_str = b'0%x' % val

        return val_str

    def _atoi(self, val):
        """
        Converts a string containing hex values to an integer of equivalent 
        value (e.g. '41' -> 65).

        Args:
            val (str): The string of hex values to convert to an integer.

        Returns:
            int: The integer value of the provided string.
        """
        return int(val, 16)

    def _padHexString(self, val, size):
        """
        Pads a string of hex values to the provided size with leading zeros.

        Args:
            val (str): String of hex bytes.

            size (int): Number of bits the string should be padded to.

        Returns:
            str: The padded string
        """
        # 2 characters per byte (8 bits)
        cur_len = len(val)
        target_len = (size // 8) * 2
        if cur_len >= target_len:
            return val

        pad_len = target_len - cur_len
        return b'%s%s' % (b'0' * pad_len, val)

    def _swapEndianness(self, byte_str):
        """
        Swaps the endianness of the provided string of hex values.

        Args:
            byte_str (str): An even-length string of hex bytes.

        Returns:
            str: The original hex value with the endianness swapped 
            (little-big or big-little).
        """
        dec = bytes.fromhex(byte_str.decode())
        swapped = dec[::-1]
        enc = swapped.hex().encode()
        return enc

    def _sendMsg(self, msg):
        """
        Sends a GDB remote protocol message.

        Args:
            msg (str): The GDB msg to send.

        Returns:
            None
        """
        logger.info('Sending message: %s' % (msg))
        
        # Build the command packet
        pkt = self._buildPkt(msg)
        
        # Transmit the packet
        self._transPkt(pkt)

class GdbClientStub(GdbStubBase):
    """
    The GDB client stub code. GDB clients should inherit from this class.
    """
    def __init__(self, arch, addr_size, le, reg, host, port, server):
        """ 
        The GDB client stub.

        Args:
            arch (str): The architecture of the target being debugged.

            addr_size (int): The addresss size of the target being debugged 
            in bits (e.g. 64 for x86_64)

            le (bool): True if the byte storage used by the debugged target is 
            little-endian, False if big-endian.

            reg (list): The list of registers monitored by the debugger. The 
            order of this list is very important, and must be the same 
            used for both the client and server. If not, parsing of register 
            packets will fail. The list itself contains sets of register names
            (str) and register sizes (int) in bits (e.g. ('rip', 64)).

            host (str): The hostname of the remote debugging server.

            port (int): The port the debug target listens on.

            server (str): The type of GDB server (qemu, gdbserver, etc...)

        Returns:
            None
        """
        GdbStubBase.__init__(self, arch, addr_size, le, reg, port)

        self._gdb_host = host
        self._gdb_server = server

    def gdbDetach(self):
        """
        Detaches from the GDB server.

        Args:
            None

        Returns:
            None
        """
        res = self._msgExchange(b'D')
        self._disconnectSocket()
 
        if res == b'OK':
            pass
        elif res[0:1] == b'E':
            raise Exception('Error occurred while detaching: %s' % (res[1:3]))
        else:
            raise Exception('Unexpected response when detaching %s' % (res))


    def _connectSocket(self):
        """
        Connects the host to the target via a socket.

        Args:
            None

        Returns:
            None
        """
        if self._gdb_sock is not None:
            self._gdb_sock.shutdown(2)

        self._gdb_sock = socket.socket()
        self._gdb_sock.connect((self._gdb_host, self._gdb_port))
        self._gdb_sock.settimeout(None)

    
    def gdbAttach(self):
        """
        Attaches to the GDB server.

        Args:
            None

        Returns:
            None
        """
        self._connectSocket()
        if self._gdb_server == 'gdbserver':
            self._targetRemote()
        else:
            logger.warning("not 'gdbserver', not initializing handshake")

    def _targetRemote(self):
        """
        Performs the initial handshake with the server (equivalent to the
        'target remote' command in GDB).

        Args:
            None

        Returns:
            None
        """
        f_name = None
        f_val = None
        res = self._msgExchange(b'qSupported')
        features = res.split(b';')
        for f in features:
            if b'=' in f:
                f_name, f_val = f.split(b'=', 1)
            else:
                f_name = f[:-1]
                f_val = f[-1]

            logger.debug("feature processing: f_name: %r\t f_val: %r" % (f_name, f_val))
            if f_name in self._supported_features.keys():
                self._supported_features[f_name] = f_val 
        
        #TODO: Might need this for multithreading support in the future
        res = self._msgExchange(b'?')
        halt_data = self._parseStopReplyPkt(res)
        halt_reason = halt_data[0]
        if halt_reason == b'W':
            raise Exception('Debugged process exited')
        elif halt_reason == b'X':
            raise Exception('Debugged process terminated')
        elif halt_reason in (b'T', b'S'):
            pass
        else:
            raise Exception('Unexpected reply received while attaching: %s' % 
                    halt_reason)

        # TODO: make this more dynamic, which will probably be required for 
        # multithreading support
        self._msgExchange(b'Hc0')
        self._msgExchange(b'qC')
        self._msgExchange(b'qOffsets')
        self._msgExchange(b'Hg0')
        self._msgExchange(b'qSymbol')

    def gdbGetFeatureFile(self, fname=b'target.xml'):
        off = 0
        size = int(self._supported_features.get(b'PacketSize', '1024'))
        out = []
        while True:
            print('gdbGetFeatureFile:  %r' % fname)
            data = self._msgExchange(b'qXfer:features:read:%s:%x,%x' % (fname, off, size))
            if len(data):
                if data[0:1] in (b'm', b'l'):
                    out.append(data[1:])
                    off += len(data) - 1
                else:
                    logger.warning("gdbGetFeatureFile(%s)[off=0x%x]: unexpected response: %r", fname, off, data)

            # go until we get less than we asked for
            if len(data) < size:
                break

        return b''.join(out)


    def gdbGetRegisters(self, reg = []):
        """
        Gathers and returns the contents of the specified registers (all 
        if no registers are specified)

        Args:
            reg (list): list of registers to dump. If no list is provided,
            all registers are dumped.

        Returns:
            dict: A dict of register names (str) and their values (int)
        """
        logger.debug('Requesting register state')
        cmd = b"g"
        res = self._msgExchange(cmd)
        if res[0:1] == b'E':
            raise Exception('Error occurred while dumping register info: %s' 
                % res[1:])
        return self._parseRegPacket(res)

    def gdbSetRegisters(self, updates):
        """
        Updates a selection of registers with new values.

        Args:
            update (dict): a dict of register names (str) and the values to 
            assign to those registers (int).

        Returns:
            None
        """
        cur_reg_vals = self.gdbGetRegisters() 

        for reg_name in updates.keys():
            # Skip registers that GDB is not expecting. Ideally this would 
            # exception, but the way Vivisect passes in registers updates 
            # (one big context object), all updates will include all possible 
            # registers.
            if reg_name not in cur_reg_vals.keys():
                logger.warning('Register %s not recognized by GDB' % reg_name)
                continue
            cur_reg_vals[reg_name] = updates[reg_name]

        # TODO: build the packet
        reg_pkt_data = self._buildRegPkt(cur_reg_vals)
        cmd = b'G%s' % reg_pkt_data
        self._msgExchange(cmd)

    # TODO: add support for setting kinds based on architecture
    def _gdbSetBreakpoint(self, bp_type, addr):
        """
        Generic function for setting breakpoints.

        Args:
            bp_type (str): The type of breakpoint to set.

            addr (int): The address to set the breakpoint on.

        Returns:
            bool: True if breakpoint was set, False if not.
        """
        success = False
        cmd = b"Z"
        if bp_type == "soft":
            cmd += b"0"
        elif bp_type == "hard":
            cmd += b"1"
        else:
            raise Exception('Breakpoint type "%s" is unsupported' % bp_type)

        addr = self._itoa(addr)

        cmd += b',%s' % addr
        #TODO: proper kind selection based on architecture
        cmd += b',0'

        res = self._msgExchange(cmd)
        if res == b'OK':
            success = True
        elif res == b'':
            logger.warning('Setting %s breakpoint is not supported' % bp_type)
        elif res[0:1] == b'E':
            logger.warning('Setting breakpoint failed with error %s' % res[1:3])

        return success

    def gdbSetSWBreakpoint(self, addr):
        """
        Sets a software breakpoint at the provided address.

        Args:
            addr (int): Address to set the software breakpoint on.

        Returns:
            None
        """
        self._gdbSetBreakpoint("soft", addr)

    def gdbSetHWBreakpoint(self, addr):
        """
        Sets a hardware breakpoint at the provided address.

        Args:
            addr (int): Address to set the hardware breakpoint on.

        Returns:
            None
        """
        self._gdbSetBreakpoint("hard", addr)

    def _gdbRemoveBreakpoint(self, bp_type, addr):
        """
        Generic function for removing breakpoints.

        Args:
            bp_type (str): The type of breakpoint to remove.

            addr (int): The address to remove the breakpoint from.

        Returns:
            bool: True if breakpoint was removed, False if not.
        """
        success = False
        cmd = b"z"
        if bp_type == "soft":
            cmd += b"0"
        elif bp_type == "hard":
            cmd += b"1"
        else:
            raise Exception('Breakpoint type "%s" is unsupported' % bp_type)

        addr = self._itoa(addr)

        cmd += b',%s' % addr
        #TODO: proper kind selection based on architecture
        cmd += b',0'

        res = self._msgExchange(cmd)
        if res == b'OK':
            success = True
        elif res == b'':
            logger.warning('Removing %s breakpoint is not supported' % bp_type)
        elif res[0:1] == b'E':
            logger.warning('Removing breakpoint failed with error %s' % res[1:3])
        
        return success

    def gdbRemoveSWBreakpoint(self, addr):
        """
        Removes a software breakpoint at the provided address.

        Args:
            addr (int): Address to remove the software breakpoint from.

        Returns:
            None
        """
        self._gdbRemoveBreakpoint("soft", addr)

    def gdbRemoveHWBreakpoint(self, addr):
        """
        Removes a hardware breakpoint at the provided address.

        Args:
            addr (int): Address to remove the hardware breakpoint from.

        Returns:
            None

        """
        self._gdbRemoveBreakpoint("hard", addr)

    def gdbContinue(self, addr = None):
        """
        Sends the continue command to the target.
        
        Args:
            addr (str): Address to continue from. If omitted, execution 
            resumes at the current address.

        Returns:
            None
        """
        cmd = b'c'
        if addr is not None:
            cmd += b'%s' % addr
        self._msgExchange(cmd)

    def gdbReadMem(self, addr, length):
        """
        Instructs GDB server to read and return memory contents from the target 
        machine.

        Args:
            addr (int): The memory address to read from.

            length (int): Size of the read in the architecture's "Addressable 
            Memory Units" (set by GDB, eight bits in most cases).

        Returns:
            int: Memory contents read from the requested address.
        """
        if length < 1:
            raise Exception('Cannot read negative amount of memory')

        addr_str = self._itoa(addr)

        cmd = b'm%s,%d' % (addr_str, length);
        res = self._msgExchange(cmd)

        if (len(res) == 3) and (res[0:1] == b'E'):
            raise Exception('Error code %s received after attempt to read memory' % 
                (res[1:3]))

        # Decode the value read from memory
        return self._decodeGDBVal(res)

    def gdbWriteMem(self, addr, val):
        """
        Instructs GDB server to write the provided value at the specified 
        memory address on the target machine.

        Args:
            addr (str): The memory address to write to.

            val (int): Value to write to memory.

        Returns:
            None
        """
        #TODO: will this cause problems with archs that don't use 8-bit
        # AMUs?

        addr_str = self._itoa(addr)

        # Convert the value to its GDB protocol format
        val_str = self._encodeGDBVal(val)

        write_length = len(val_str) // 2

        cmd = b'M%s,%d:%s' % (addr_str, write_length, val_str)
        res = self._msgExchange(cmd)

        if res == b'OK':
            pass
        elif res[0:1] == b'E':
            raise Exception('Error code %s received after attempt to write memory' %
                (res[1:3]))
        else:
            raise Exception('Unexpected response to writing memory: %s' % res)
            
    def gdbStepi(self, addr = None):
        """
        Sends the single step (into) command to the target.

        Args:
            addr (str): Address to resume from. If omitted, execution 
            resumes at the current address.

        Returns:
            None
        """
        cmd = b"s"
        if addr is not None:
            cmd += b'%s' % addr
        res = self._msgExchange(cmd)
        res_data = self._parseStopReplyPkt(res)

    def _parseSignalPkt(self, pkt_data):
        """
        Parses signal packets.

        Args:
            pkt_data (str): The data segment from a reply/stop signal packet

        Returns:
            list: A list containing a signal number (str)
        """
        signal = pkt_data[1:3]
        return [signal]

    def _parseThreadPkt(self, pkt_data):
        """
        Parsess thread packets

        Args:
            pkt_data (str): The data segment from a reply/stop thread packet

        Returns:
            list: A list of sets of n, r pairs
        """
        ret = []
        signal = pkt_data[1:3]
        ret.append(signal)
        # split into list of n:r pairs
        pairs = pkt_data[3:].split(b';')
        # messages end with b';'
        pairs.pop()
        for p in pairs:
            vals = p.split(b':')
            n = vals[0]
            r = vals[1]
            ret.append((n, r))

        return ret

    def _parseStopReplyPkt(self, pkt_data):
        """
        Parses stop and reply packets.

        Args:
            pkt_data (str): The reply/stop packet to parse.

        Returns:
            list: The parsed packet data.
        """
        # TODO: we currently don't do much with this, although it will be 
        # useful when adding multithreading support and maybe when plumbing 
        # into vivisect
        cmd = pkt_data[0:1]
        data = [cmd]
        if cmd == b'S':
            data.append(self._parseSignalPkt(pkt_data))
        elif cmd == b'T':
            data.append(self._parseThreadPkt(pkt_data))

        # TODO: T and S are the two big ones, add support for the others at 
        # a later time
        elif cmd == b'W':
            pass
        elif cmd == b'X':
            pass
        elif cmd == b'w':
            pass
        elif cmd == b'N':
            pass
        elif cmd == b'O':
            pass
        elif cmd == b'F':
            pass
        else:
            raise Exception('Client received unexpected reply/stop packet: ' \
                    '%s' % (pkt_data))

        return data

class GdbServerStub(GdbStubBase):
    """
    The GDB server stub code. GDB server implementations should inherit from
    this class. Functions that start with '_server' must be implemented by 
    the code controlling the debugged process (e.g. the vivisect emulator).
    """
    def __init__(self, arch, addr_size, le, reg, port):
        """ 
        The GDB sever stub.

        Args:
            arch (str): The architecture of the target being debugged.

            addr_size (int): The addresss size of the target being debugged 
            in bits (e.g. 64 for x86_64)

            le (bool): True if the byte storage used by the debugged target is 
            little-endian, False if big-endian.

            reg (list): The list of registers monitored by the debugger. The 
            order of this list is very important, and must be the same 
            used for both the client and server. If not, parsing of register 
            packets will fail. The list itself contains sets of register names
            (str) and register sizes (int) in bits (e.g. ('rip', 64)).

            port (int): The port the debug target listens on.

        Returns:
            None
        """
        GdbStubBase.__init__(self, arch, addr_size, le, reg, port)

    def runServer(self):
        """
        Trivial listening server. This should only be used for unit testing.

        Args:
            None

        Returns:
            None
        """
        sock = socket.socket()
        sock.bind(('localhost', self._gdb_port))
        sock.listen(5)
        self._gdb_sock, addr = sock.accept()
        
        while True:
            try:
                data = self._recvUntil(b'#')
            except Exception as e:
                logger.warning('gdbstub.runServer() Exception: %r', e, exc_info=1)
                break

            # TODO: check the checksum
            data = b'%s%s' % (data, self._gdb_sock.recv(2))
            self._cmdHandler(data)  
    
        self._gdb_sock.close()
        sock.close()

    def _cmdHandler(self, data):
        """
        Generic dispatcher for GDB command handling.

        Args:
            data (str): A message from the GDB client.

        Returns:
            None
        """
        res = None
        msg_data = self._parseMsg(data)
        cmd = msg_data[0:1]
        cmd_data = msg_data[1:]
        logger.debug('Server received command: %s' % cmd)
        expect_res = False

        self._transPkt(b'+')
        # TODO: the error codes could be finer-grain
        try:
            if cmd == b'?':
                res = self._handleHaltInfo()
            elif cmd == b'g':
                res = self._handleReadRegs()
            elif cmd == b'G':
                res = self._handleWriteRegs(cmd_data)
            elif cmd == b'c':
                res = self._handleCont()
            elif cmd == b'D':
                res = self._handleDetach()
            elif cmd == b'Z':
                res = self._handleSetBreak(cmd_data)
            elif cmd == b'z':
                res = self._handleRemoveBreak(cmd_data)
            elif cmd == b'm':
                res = self._handleReadMem(cmd_data)
            elif cmd == b'M':
                res = self._handleWriteMem(cmd_data)
            elif cmd == b's':
                res = self._handleStepi()
            else:
                raise Exception(b'Unsupported command %s' % cmd)
        except:
            self._msgExchange(b'E%.2x' % errno.EPERM)
            raise

        enc_res = self._lengthEncode(res)
        self._msgExchange(enc_res, expect_res)

    def _parseBreakPkt(self, pkt_data):
        """
        Parses breakpoint-related GDB packets.

        Args:
            pkt_data (str): The GDB packet containing a breakpoint command.

        Returns:
            str, int: The breakpoint type and corresponding memory address.
        """
        #TODO: add support for break params and kinds
        break_type = pkt_data[0]
        addr = pkt_data.split(b',')[1]
        addr = self._decodeGDBVal(addr)
        
        return break_type, addr

    def _handleSetBreak(self, cmd_data):
        """
        Handles requests to set different types of breakpoints.

        Args:
            cmd_data (str): The client request body.

        Returns:
            str: The GDB status code.
        """
        break_type, addr = self._parseBreakPkt(cmd_data)

        if break_type == b'0':
            self._serverSetSWBreak(addr)
        elif break_type == b'1':
            self._serverSetHWBreak(addr)
        else:
            raise Exception('Unsupported breakpoint type: %s' % break_type)

        return b'OK'

    def _serverSetHWBreak(self, addr):
        """
        Instructs the execution engine to set a hardware breakpoint at the
        specified address.

        Args:
            addr (int): The memory address at which to set the hardware
            breakpoint.

        Returns:
            None
        """
        raise Exception('Server translation layer must implement this function')
   
    def _serverSetSWBreak(self, addr):
        """
        Instructs the execution engine to set a software breakpoint at the
        specified address.

        Args:
            addr (int): The memory address at which to set the software
            breakpoint.

        Returns:
            None
        """
        raise Exception('Server translation layer must implement this function')
 
    def _handleRemoveBreak(self, cmd_data):
        """
        Handles client requests to remove breakpoints.

        Args:
            cmd_data (str): The GDB request packet body.

        Returns:
            str: The GDB status code.
        """
        break_type, addr = self._parseBreakPkt(cmd_data)
    
        if break_type == b'0':
            self._serverRemoveSWBreak(addr)
        elif break_type == b'1':
            self._serverRemoveHWBreak(addr)
        else:
            raise Exception('Unsupported breakpoint type: %s' % break_type)

        return b'OK'

    def _serverRemoveHWBreak(self, addr):
        """
        Instructs the execution engine to remove a hardware breakpoint at the
        given address.

        Args:
            addr (int): The memory address at which to remove the hardware
            breakpoint.

        Returns:
            None
        """
        raise Exception('Server translation layer must implement this function')

    def _serverRemoteSWBreak(self, addr):
        """
        Instructs the execution engine to remove a software breakpoint at the
        given address.

        Args:
            addr (int): The memory address at which to remove the software
            breakpoint.

        Returns:
            None
        """
        raise Exception('Server translation layer must implement this function')

    def _handleHaltInfo(self):
        """
        Requests from the execution engine the reason for the current halt.

        Args:
            None

        Returns:
            str: A GDB response packet containing the halt reason.
        """
        signal = self._serverGetHaltSignal()
        res = b'%s%.2x' % (b'S', signal)
        return res

    def _serverGetHaltSignal(self):
        """
        Returns the signal number responsible for the current halt.

        Args:
            None

        Returns:
            int: The signal number corresponding to the halt.
        """
        raise Exception('Server translation layer must implement this function')

    def _handleReadMem(self, cmd_data):
        """
        Handles client requests for reading memory.

        Args:
            cmd_data (str): The body of the request.

        Returns:
            str: The value read by the execution engine at the specified
            address in GDB encoding.
        """
        addr = cmd_data.split(b',')[0] 
        addr = self._atoi(addr)
        size = cmd_data.split(b',')[1]
        size = self._atoi(size)

        val = self._serverReadMem(addr, size)
        val = self._encodeGDBVal(val)
        
        return val

    def _serverReadMem(self, addr, size):
        """
        Instructions the execution to read virtual memory and return its 
        contents.

        Args:
            addr (int): The virtual address to read from.

            size (int): The size of the read in GDB "Addressible Memory Units"
            (architecture define, but bytes in most cases).

        Returns:
            int: The value read from memory.
        """
        raise Exception('Server translation layer must implement this function')

    def _handleWriteMem(self, cmd_data):
        """
        Handles memory write events.

        Args:
            cmd_data (str): The body of the command from the client.

        Returns:
            str: The GDB status update.
        """
        addr = cmd_data.split(b',')[0]
        addr = self._atoi(addr)

        val = cmd_data.split(b':')[1]
        val = self._decodeGDBVal(val)

        self._serverWriteMem(addr, val)

        return b'OK'

    def _serverWriteMem(self, addr, val):
        """
        Instructs the execution engine to write a new value at the specified
        address.

        Args:
            addr (int): The address at which to perform the write.

            val (int): The value to write.

        Returns:
            None
        """
        raise Exception('Server translation layer must implement this function')

    def _handleWriteRegs(self, reg_data):
        """
        Handles client requests to write to registers.

        Args:
            reg_data (str): The request packet.

        Returns:
            str: GDB status code
        """
        registers = self._parseRegPacket(reg_data)
        for reg_name in registers.keys():
            self._serverWriteRegVal(reg_name, registers[reg_name])

        return b'OK'

    def _serverWriteRegVal(self, reg_name, reg_val):
        """
        Instructs the execution engine to write the provided value into the 
        provided register.

        Args:
            reg_name (str): The name of the register to write to.

            reg_val (int): The value to write into the register.

        Returns:
            None
        """
        raise Exception('Server translation layer must implement this function')

    def _handleReadRegs(self):
        """
        Instructs the execution engine to read the values in all registers.

        Args:
            None

        Returns:
            str: A GDB remote protocol register packet.
        """
        registers = {}
        for reg in self._gdb_reg_fmt:
            reg_name = reg[0]
            reg_val = self._serverReadRegVal(reg_name)
            registers[reg_name] = reg_val

        reg_pkt = self._buildRegPkt(registers)
        return reg_pkt

    def _serverReadRegVal(self, reg_name):
        """
        Returns the value currently stored in a given register.

        Args:
            reg_name (str): The register name.

        Returns:
            int: The value stored in the provided register
        """
        raise Exception('Server translation layer must implement this function')

    def _handleStepi(self):
        """
        Handles requests to single step (into).

        Args:
            None

        Returns:
            None
        """
        signal = self._serverStepi()
        res = b'S%.2x' % (signal)
        return res

    def _serverStepi(self):
        """
        Instructs the execution engine to single step (into) from the current
        instruction address. The function should return when the next halt
        occurs (usually once the single step is complete).

        Args:
            None

        Returns:
            int: The signal corresponding to the next halt after the single
            step.
        """
        raise Exception('Server translation layer must implement this function')

    def _handleDetach(self):
        """
        Informs the execution engine that the debugging client is being
        detached.

        Args:
            None

        Returns:
            str: 'OK' status code
        """
        self._serverDetach()
        return b'OK'

    def _serverDetach(self):
        """
        Instructs the execution engine to continue execution and no longer
        report halts to the server.

        Args:
            None

        Returns:
            str: GDB status code
        """
        raise Exception('Server translation layer must implement this function')

    def _handleCont(self):
        """
        Instructs the execution engine to continue execution at the current
        address.

        Args:
            None

        Returns:
            int: The reason for the next halt.
        """
        signal = self._serverCont()
        res = b'S%.2x' % (signal)
        return res
        
    def _serverCont(self):
        """
        Resumes target execution at the current address. This function should
        block until the execution engine halts (e.g. hits a breakpoint).

        Args:
            None

        Returns:
            int: The reason for the next halt (should always be a signal number
            such as 5 for a TRAP).
        """
        raise Exception('Server translation layer must implement this function')

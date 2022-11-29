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
import xml.etree.ElementTree as xmlET
from binascii import hexlify, unhexlify

from . import gdb_reg_fmts
from .gdb_reg_fmts import ARCH_META

import envi.exc as e_exc
import envi.common as e_cmn
import vtrace.platforms.gdb_exc as gdb_exc

from itertools import groupby
from vtrace.platforms import signals

logger = logging.getLogger(__name__)
#e_cmn.initLogging(logger, level=logging.INFO)

class GdbStubBase:
    def __init__(self, arch, addr_size, bigend, reg, port, find_port=True):
        """ 
        Base class for consumers of GDB protocol for remote debugging.

        Args:
            arch (str): The architecture of the target being debugged.

            addr_size (int): The addresss size of the target being debugged 
            in bits (e.g. 64 for x86_64)

            bigend (bool): False if the byte storage used by the debugged target is 
            little-endian, True if big-endian.   (as per the rest of Vivisect)

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
        self._gdb_find_port = find_port
        self._arch = arch
        self._gdbarch = None    # do a lookup?  sort this out.
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
                b'multiprocess': None
                }

        self._settings = {}

        self._NoAckMode = False
        self._bigend = bigend
        self._addr_size = addr_size
        self._doEncoding = True


    def _getFeat(self, featurename):
        '''
        Returns a given "_supported_feature" entry, or None.
        '''
        return self._supported_features.get(featurename)

    def setGdbArchitecture(self, archname, setMeta=True):
        '''
        This sets the GDB Architecture name, and other architectural settings
        implied by them.

        if setMeta is True and the archname is found in our lookup table, the 
        following metasettings will be updated:
        * self._arch
        * self._bigend
        * self._addr_size
        * self._arch_pcname
        * self._arch_spname

        '''
        self._gdbarch = archname
        if setMeta and archname in ARCH_META:
            self._arch = ARCH_META[archname]['arch']
            self._bigend = ARCH_META[archname]['bigend']
            self._addr_size = ARCH_META[archname]['psize'] * 8
            self._arch_pcname = ARCH_META[archname]['pcname']
            self._arch_spname = ARCH_META[archname]['spname']

    def _decodeGDBVal(self, val):
        """
        Decodes a value from a GDB string into an int.

        Args:
            val (str): A value in GDB string format.

        Returns:
            int: The equivalent int value of the supplied string.
        """
        val_str = val
        if not self._bigend:
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
       
        if not self._bigend:
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

        logger.log(e_cmn.MIRE, 'Transmitting packet: %s' % (pkt))
        self._gdb_sock.sendall(pkt)
    
    def _recvResponse(self):
        """
        Handles receiving data over the server-client socket.
        This includes both Data response as well as Ack/Retrans

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
        if not self._NoAckMode and res in (b'+', b'-'):
            return res

        elif res == b'$':
            pass

        else:
            res = res + self._gdb_sock.recv(10)
            raise Exception('Received unexpected packet: %s' % res)


        pkt = b'$%s' % self._recvUntil((b'#',))
        logger.debug('_recvMessage: pkt=%r' % pkt)
        msg_data = self._parseMsg(pkt)

        expected_csum = int(self._gdb_sock.recv(2), 16)
        actual_csum = self._gdbCSum(msg_data)

        if expected_csum != actual_csum:
            raise Exception('Invalid packet data checksum')

        if not self._NoAckMode:
            # only send Ack if this is *not* an Ack/Retrans and if everything 
            # checks out ok (checksum, $/#/etc)
            self._sendAck()

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

    def _recvUntil(self, clist):
        """
        Recieve data from the socket until the specified character is reached.

        Args:
            c (str): the character to read until.

        Returns:
            str: The characters read up until and including the delimiting
            character.
        """
        logger.log(e_cmn.MIRE, "_recvUntil(%r)", clist)
        ret = []
        x = b''
        while x not in clist:
            x = self._gdb_sock.recv(1)
            if len(x) == 0:
                raise Exception('Socket closed unexpectedly')
            ret.append(x)
            
        logger.log(e_cmn.MIRE, '_recvUntil(%r):  %r', clist, ret)
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

        if self._NoAckMode:
            self._sendMsg(msg)
        else:
            # Send the command until its receipt is acknowledged
            while (status != b'+') and (retry_count < retry_max):
                self._sendMsg(msg)
                status = self._recvResponse()
                retry_count += 1
            if retry_count >= retry_max:
                logger.warning("_msgExchange:  Not received Ack in retry_max (%r) attempts!", retry_max)

        # Return the response
        if expect_res:
            res = self._recvResponse()
            
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
        if not self._NoAckMode:
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
        if not self._doEncoding:
            return data

        max_rep = 97
        grouped = [b''.join([b'%c' % x for x in g]) for _, g in groupby(data)]

        enc_list = []
        for g in grouped:
            length = len(g)
            char = g[0:1]
            # Special handling for b'#' (6 + 29)
            if length == 6:
                enc_list.append(b'%s\"%s' % (char, char))

            # Special handling for b'$' (7 + 29)
            elif length == 7:
                enc_list.append(b'%s\"%s%s' % (char, char, char))

            # GDB only supports encoded up to 126 repetitions
            elif length > max_rep:
                q, r = divmod(length, max_rep)
                # Split into chunks of 126 repetitions
                chunk = b'%s*%s' % (char, b'%c' % (max_rep + 29))
                print("chunk(%d:%d): %r" % (q, r, chunk))
                enc_list.append(chunk * q)

                # Handle the remainder
                if r == 6:
                    enc_list.append(b'%s\"%s' % (char, char))
                elif r == 7:
                    enc_list.append(b'%s\"%s%s' % (char, char, char))
                else:
                    enc_list.append(b'%s*%s' % (char, b'%c' % (r + 29)))

            elif length > 2:
                rep_count = length - 1
                enc_list.append(b'%s*%s' % (char, b'%c' % (rep_count + 29)))

            else:
                enc_list.append(g)

        return b''.join(enc_list)

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
        val_str = b'%.2x' % val

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
        logger.log(e_cmn.MIRE, 'Sending message: %s' % (msg))
        
        # Build the command packet
        pkt = self._buildPkt(msg)
        
        # Transmit the packet
        self._transPkt(pkt)

class GdbClientStub(GdbStubBase):
    """
    The GDB client stub code. GDB clients should inherit from this class.
    """
    # TODO: make a "discovery" mode which pulls target.xml instead of requiring an architecture up front
    def __init__(self, arch, addr_size, bigend, reg, host, port, servertype):
        """ 
        The GDB client stub.

        Args:
            arch (str): The architecture of the target being debugged.

            addr_size (int): The addresss size of the target being debugged 
            in bits (e.g. 64 for x86_64)

            bigend (bool): False if the byte storage used by the debugged target is 
            little-endian, True if big-endian.

            reg (list): The list of registers monitored by the debugger. The 
            order of this list is very important, and must be the same 
            used for both the client and server. If not, parsing of register 
            packets will fail. The list itself contains sets of register names
            (str) and register sizes (int) in bits (e.g. ('rip', 64)).

            host (str): The hostname of the remote debugging server.

            port (int): The port the debug target listens on.

            servertype (str): The type of GDB server (qemu, gdbserver, etc...)

        Returns:
            None
        """
        GdbStubBase.__init__(self, arch, addr_size, bigend, reg, port)

        self._gdb_host = host
        self._gdb_servertype = servertype
        self._offsets = None

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
        if self._gdb_servertype in ('gdbserver', 'serverstub', 'qemu'):
            self._targetRemote()
        else:
            logger.warning("%r is not 'gdbserver' or 'serverstub', not initializing handshake", self._gdb_servertype)

        self._postAttach()

    def _postAttach(self):
        '''
        A hook for subclasses to insert functionality after attaching to a 
        GDB Server
        '''
        pass


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
                # this is a "supported" indicator tagged on the end.
                # + is true, - is false
                f_name = f[:-1]
                f_val = f[-1]

                if f_val == 0x2b:
                    f_val = True
                elif f_val == 0x2d:
                    f_val = False

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
        self._msgExchange(b'Hg0')
        self.gdbGetOffsets()
        self.gdbGetSymbol(b'main')

    def gdbGetSymbol(self, symbol):
        symhex = hexlify(symbol)
        return self._msgExchange(b'qSymbol:' + symhex)

    def gdbGetOffsets(self, cached=True):
        if self._offsets and cached:
            return self._offsets

        out = {}
        res = self._msgExchange(b'qOffsets')
        if not len(res):
            return {}

        for line in res.split(b";"):
            key, val = line.split(b"=")
            out[key] = int(val, 16)

        self._offsets = out

        return out

    def qXfer(self, qtype, cmd=b'read', name=b'', pktsz=None, maxsize=0x100000):
        '''
        qXfer implementation.  Queries form like:
        b'qXfer:<name>:<cmd>:offset:<pktsz>' with offset automatically 
        incrementing until complete.  The whole query response (up to maxsize)
        is returned
        '''
        off = 0
        size = int(self._supported_features.get(b'PacketSize', '1024'))
        out = []
        while True:
            data = self._msgExchange(b'qXfer:%s:%s:%s:%x,%x' % (qtype, cmd, name, off, size))
            res = None
            if len(data):
                res = data[0:1]
                msg = data[1:]
                if res in (b'm', b'l'):
                    out.append(msg)
                    off += len(msg)
                else:
                    logger.warning("qXfer:%s:%s:%s [off=0x%x]: unexpected response: %r", qtype, cmd, name, off, data)

            # go until we get less than we asked for
            if res == b'l' or len(data) < size:
                break

        return b''.join(out)

    def gdbReadMemoryMapInfo(self):
        '''
        Use qXfer:memory-map:read (if supported) to get memory map metadata
        Returns a list of memory maps on success.
        Returns None on failure.
        '''
        mmapbytes = self.qXfer(b'memory-map')
        if not len(mmapbytes):
            return None

        xml = xmlET.fromstring(mmapbytes)
        return xml


    def getMemoryMaps(self, pgsize=4096):
        '''
        Build and return a list of memory map definitions using the best 
        available metadata.

        This will start with a qXfer:memory-map:read, if supported.
        Then it will fall back to qOffsets if possible, with some ugly magic
        fairy-dust.
        '''
        maps = []

        # start off attempting to qXfer:memory-map:read, even if it doesn't list it.
        mmapinfo = self.gdbReadMemoryMapInfo()
        if mmapinfo:
            for mapelem in mmapinfo:
                a = mapelem.attrib
                maps.append((a['start'], a['length'], 7, a['type']))

        # if needs-be, check to see if we have qOffsets
        if not len(maps):
            qOffsets = self.gdbGetOffsets()
            for offname, qoff in list(qOffsets.items()):
                # check if this offset is already covered?
                skip = False
                for va, sz, perm, nm in maps:
                    if va <= qoff < (va+sz):
                        skip = True
                        break

                if skip:
                    continue

                # now, search by page to the end...  guess at 4096/page
                off = 0
                try:
                    while True:
                        # try reading the end of the current page with the start
                        # of the next
                        off += pgsize
                        data = self.gdbReadMem(off + qoff - 5, 10)
                        print("DEBUG: %x:  %r" % (off+qoff-5, data))

                except Exception as e:
                    print("DEBUG: %r" % e)

                maps.append((qoff, off, 7, b'offmap-%s' % offname))
                # TODO: scour large amount of address space looking for maps?

        return maps

            
    def gdbGetFeatureFile(self, fname=b'target.xml'):
        return self.qXfer(b'features', name=fname)


    def gdbGetRegister(self, regidx):
        """
        Gathers and returns the contents of the specified registers (all 
        if no registers are specified)

        Args:
            regidx (int): target-specific register index to dump.

        Returns:
            integer value
        """
        reg = b'%.2x' % regidx
        logger.debug('Requesting register %s', reg)
        cmd = b"p" + reg
        res = self._msgExchange(cmd)
        if res[0:1] == b'E':
            raise Exception('Error occurred while dumping register info: %s' 
                % res[1:])
        return self._decodeGDBVal(res)

    def gdbSetRegister(self, regidx, val):
        """
        Set a register with a new value.

        Args:
            regidx (int): target-specific register index (see target.xml for best answer)
            val (int):  new value for the register

        Returns:
            None
        """
        val_str = self._encodeGDBVal(val)
        cmd = b'P%.2x=%s' % (regidx, val_str)
        self._msgExchange(cmd)

    def gdbGetRegisterByName(self, regname):
        """
        Gathers and returns the contents of the specified registers (all 
        if no registers are specified)

        Args:
            regname (str): register name to dump.

        Returns:
            integer value
        """
        for rn, rsz, ridx in self._gdb_reg_fmt:
            if rn == regname:
                return self.gdbGetRegister(ridx)

        raise e_exc.InvalidRegisterName("Invalid Register Name in gdbGetRegisterByName: %r" % regname)

    def gdbSetRegisterByName(self, regname, val):
        """
        Set a register with a new value.

        Args:
            regname (str): target-specific register name (see target.xml for best answer)
            val (int):  new value for the register

        Returns:
            None
        """
        for rn, rsz, ridx in self._gdb_reg_fmt:
            if rn == regname:
                return self.gdbSetRegister(ridx, val)

        raise e_exc.InvalidRegisterName("Invalid Register Name in gdbSetRegisterByName(%r, %r)" % (regname, val))

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

    getRegisters = gdbGetRegisters

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

    setRegisters = gdbSetRegisters

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
        if self._supported_features.get(b'multiprocess', False):
            cmd = b'vCont;c'
        else:
            cmd = b'c'

            if addr is not None:
                cmd += b'%s' % addr

        # send packet but don't wait for a reply.  It's not coming until the
        # target halts again.
        self._msgExchange(cmd, False)

    def gdbSendBreak(self, wait=True):
        """
        Sends the Halt command to the target.
        If "wait" then it will wait until a response is received indicating
        that the target is stopped with a reason.

        This is defined as a simple character b'\x03' in E.8: Interrupts in
          https://sourceware.org/gdb/current/onlinedocs/gdb/Interrupts.html
        None of the usual packet header/checksum/response are required.

        From experience, the results of the halt may not happen right away.
        """
        #TODO: handle NonStop mode.  In NonStop, a vCont packet is used instead 
        self._gdb_sock.sendall(b'\x03')
        if wait:
            return self._recvResponse()

    def gdbKill(self):
        """
        Kill target process.
        """
        # TODO: vKill for multiprocessing targets
        cmd = b'k'
        res = self._msgExchange(cmd)
        return res

    def gdbGetThreadInfo(self):
        out = []
        # ye olde method
        res = self._msgExchange(b'qL1ff00000000')
        if res.startswith(b'qM'):
            while res[4] != 0x31:
                print("res[4] == %r" % res[4])
                count = int(res[2:4], 16)
                done = res[4]
                argthreadid = res[5:13]
                threads = [int(res[x+13:x+21], 16) for x in range(count)]
                out.extend(threads)

                # get the next volley
                res = self._msgExchange(b'qL0ff00000000')

        # young whippersnapper
        if self._supported_features.get(b'multiprocess', False):
            res = self._msgExchange(b'qfThreadInfo')
            while len(res) and res != b'l' and res[0:1] in (b'l', b'm'):
                for thrstr in res[1:].split(b','):
                    out.append(int(thrstr, 16))
                res = self._msgExchange(b'qsThreadInfo')

        # always give a thread option: default 0
        if not len(out):
            return [0]

        return out

    def gdbSelectThread(self, threadid):
        """
        """
        cmd = b'Hg%x' % threadid
        res = self._msgExchange(cmd)
        return res

    def gdbReadMem(self, addr, length, retInt=False):
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

        cmd = b'm%.2x,%x' % (addr, length);
        res = self._msgExchange(cmd)

        if (len(res) == 3) and (res[0:1] == b'E'):
            raise Exception('Error code %s received after attempt to read memory' % 
                (res[1:3]))

        if retInt:
            # Decode the value read from memory
            return self._decodeGDBVal(res)

        return unhexlify(res)

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
        if isinstance(val, bytes):
            val_str = hexlify(val)

        else:
            val_str = self._encodeGDBVal(val)
            
        write_length = len(val_str) // 2

        cmd = b'M%s,%x:%s' % (addr_str, write_length, val_str)
        res = self._msgExchange(cmd)

        if res == b'OK':
            pass
        elif res[0:1] == b'E':
            raise Exception('Error code %s received after attempt to write memory' %
                (res[1:3]))
        else:
            raise Exception('Unexpected response to writing memory: %s' % res)
            
    def gdbStepi(self, addr = None, processResp=True):
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
        res = self._msgExchange(cmd, processResp)
        if processResp:
            return self._parseStopReplyPkt(res)

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


STATE_STARTUP = 0
STATE_RUNSTART = 1
STATE_RUNNING = 2
STATE_SHUTDOWN = 3


class GdbServerStub(GdbStubBase):
    """
    The GDB server stub code. GDB server implementations should inherit from
    this class. Functions that start with '_server' must be implemented by 
    the code controlling the debugged process (e.g. the vivisect emulator).
    """
    def __init__(self, arch, addr_size, bigend, reg, port, find_port=True):
        """ 
        The GDB sever stub.

        Args:
            arch (str): The architecture of the target being debugged.

            addr_size (int): The addresss size of the target being debugged 
            in bits (e.g. 64 for x86_64)

            bigend (bool): False if the byte storage used by the debugged target is 
            little-endian, True if big-endian.

            reg (list): The list of registers monitored by the debugger. The 
            order of this list is very important, and must be the same 
            used for both the client and server. If not, parsing of register 
            packets will fail. The list itself contains sets of register names
            (str) and register sizes (int) in bits (e.g. ('rip', 64)).

            port (int): The port the debug target listens on.

        Returns:
            None
        """
        GdbStubBase.__init__(self, arch, addr_size, bigend, reg, port, find_port)
        self.state = STATE_STARTUP

        self.curThread = None
        self.threadList = []
        self.threadOps = {'m': 0,
                'M': 0,
                'g': 0,
                'G': 0,
                'c': 0,
                's': 0,
                'vCont': 0,
        }

        self.breakPointsSW = []
        self.breakPointsHW = []

        self._stop_reason = signals.SIG_0     ## @ac0rn this tracks the reason for halt, but 0 is "not stopped". i'll need your help ensuring all the interactions between Emulator and GdbStubBase honor this

    def setGdbHaltReason(self, reason):
        '''
        The Emulator should call this 
        '''
        self._halt_reason = reason

    def isRunning(self):
        '''
        if self._halt_reason is non-zero, we've halted
        '''
        return not self._halt_reason

    def _recvServer(self, maxlen=10000):
        '''
        Receive packets for the server (from a connected client)
        '''
        data = b''
        while not len(data) or data[-1:] != b'#':
            data += self._recvUntil((b'#', b'\x03'))
            logger.log(e_cmn.MIRE, "_recvServer: data=%r", data)
            if data == b'\x03':
                logger.info("Received BREAK!  Raising GdbBreakException")
                raise gdb_exc.GdbBreakException()

            if len(data) > maxlen:
                logger.warning("fail: len(data): %d   maxlen: %d", len(data), maxlen)
                raise gdb_exc.InvalidGdbPacketException("Invalid Packet: %r" % data)


        logger.log(e_cmn.MIRE, "done with read loop:  %r", data)

        # state housekeeping
        if self.state == STATE_RUNSTART:
            self.state = STATE_RUNNING
            if data[0:1] == b'+':
                # meh, housewarming gift.  eat it.
                data = data[1:]

        # now do our packet checks
        if data[0:1] != b'$':
            logger.warning("fail: data doesn't start with '$'")
            raise gdb_exc.InvalidGdbPacketException("Invalid Packet: %r" % data)

        data = data[1:-1]

        # pull the checksum bytes
        csum = self._gdb_sock.recv(2)
        calccsum = self._gdbCSum(data)
        logger.log(e_cmn.MIRE, "DATA: %r     CSUM: %r (calculated: %.2x)", data, csum, calccsum)
        if int(csum, 16) != calccsum:
            raise gdb_exc.InvalidGdbPacketException("Invalid Packet (checksum): %r  %r!=%r" % (data, csum, calccsum))

        return data


    def runServer(self):
        """
        GdbServer stub.
        Starts listening on self._gdb_port and processes incoming connections
        using the GDB Remote Protocol

        Args:
            None

        Returns:
            None
        """
        data = b''
        logger.info("runServer starting...")
        self._server_sock = socket.socket()
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True:
            try:
                self._server_sock.bind(('localhost', self._gdb_port))
                break

            except OSError as e:
                if not self._gdb_find_port:
                    raise e

                self._gdb_port += 1

        self._server_sock.listen(1)
        logger.info("runServer listening on port %d", self._gdb_port)

        self.state = STATE_STARTUP

        while self.state in (STATE_RUNNING, STATE_RUNSTART, STATE_STARTUP):
            try:
                self.state = STATE_RUNSTART
                self._gdb_sock, addr = sock.accept()
                logger.info("runServer: Received Connection from %r", addr)
                self._postClientAttach(addr)
                self.last_reason = self._halt_reason
                
                while True:
                    logger.log(e_cmn.MIRE, "runServer continuing...")
                    try:
                        # Check and handle the processor breaking.
                        if self._halt_reason != 0 and \
                                self._halt_reason != self.last_reason:
                            # send the halt reason to the client (since they should
                            # be waiting for it...
                            self._doServerResponse(self._handleEndCont(), False)

                        self.last_reason = self._halt_reason

                        # check to see if there's any data to process
                        x, y, z = select.select([self._gdb_sock],[],[], .1)
                        if not x:
                            continue

                        # if the client has sent command data, handle it here.
                        data = self._recvServer()
                        #TODO: coalesce with _parseMsg?

                        if self._NoAckMode:
                            logger.debug("received: %r", data)
                        else:
                            # ack receipt
                            logger.debug("received: %r    xmitting '+'", data)
                            self._sendAck()

                    except gdb_exc.InvalidGdbPacketException as e:
                        logger.warning("Invalid Packet Exception!  %r", e)
                        self._sendRetrans()
                        continue

                    except gdb_exc.GdbBreakException as e:
                        logger.info("Received BREAK signal: %r", e)
                        data = b'\x03'

                    except Exception as e:
                        logger.warning('gdbstub.runServer() Exception: %r', e, exc_info=1)
                        break

                    logger.log(e_cmn.MIRE, "runServer: %r" % data)
                    self._cmdHandler(data)  
            
            except Exception as e:
                logger.critical("runServer exception!", exc_info=1)

            finally:
                self._gdb_sock.close()

        sock.close()

    def _postClientAttach(self, addr):
        pass


    def _cmdHandler(self, data):
        """
        Generic dispatcher for GDB command handling.

        Args:
            data (str): A message from the GDB client.

        Returns:
            None
        """
        res = None
        cmd = data[0:1]
        cmd_data = data[1:]
        logger.debug('Server received command: %s' % cmd)
        expect_res = False

        # TODO: the error codes could be finer-grain
        try:
            if cmd == b'?':
                logger.info('_handleHaltInfo(%r)' % cmd_data)
                res = self._handleHaltInfo()
            elif cmd == b'g':
                logger.info('_handleReadRegs(%r)' % cmd_data)
                res = self._handleReadRegs()
            elif cmd == b'G':
                logger.info('_handleWriteRegs(%r)' % (cmd_data))
                res = self._handleWriteRegs(cmd_data)
            elif cmd == b'p':
                logger.info('_handleReadReg(%r)' % cmd_data)
                res = self._handleReadReg(cmd_data)
            elif cmd == b'P':
                logger.info('_handleWriteReg(%r)' % (cmd_data))
                res = self._handleWriteReg(cmd_data)
            elif cmd == b'c':
                logger.info('_handleCont(%r)' % cmd_data)
                self._handleCont()
                res = None
            elif cmd == b'D':
                logger.info('_handleDetach(%r)' % cmd_data)
                res = self._handleDetach()
            elif cmd == b'Z':
                logger.info('_handleSetBreak(%r)' % (cmd_data))
                res = self._handleSetBreak(cmd_data)
            elif cmd == b'z':
                logger.info('_handleRemoveBreak(%r)' % (cmd_data))
                res = self._handleRemoveBreak(cmd_data)
            elif cmd == b'm':
                logger.info('_handleReadMem(%r)' % (cmd_data))
                res = self._handleReadMem(cmd_data)
            elif cmd == b'M':
                logger.info('_handleWriteMem(%r)' % (cmd_data))
                res = self._handleWriteMem(cmd_data)
            elif cmd == b's':
                logger.info('_handleStepi(%r)' % cmd_data)
                res = self._handleStepi()
            elif cmd == b'H':
                logger.info('_handleSetThread(%r)' % (cmd_data))
                res = self._handleSetThread(cmd_data)

            elif cmd == b'q':
                logger.info('_handleQuery(%r)' % (cmd_data))
                res = self._handleQuery(cmd_data)

            elif cmd == b'Q':
                logger.info('_handleQSetting(%r)' % (cmd_data))
                res = self._handleQSetting(cmd_data)

            elif cmd == b'\x03':
                logger.info('_handleBREAK(%r)' % cmd_data)
                res = self._handleBREAK()

            else:
                #raise Exception(b'Unsupported command %s' % cmd)
                logger.warning('Unsupported command %s (%r)' % (cmd, cmd_data))
                #self._msgExchange(b'')
                res = b''

        except Exception as e:
            logger.warning("_cmdHandler(%r): EXCEPTION: %r", data, e)
            self._msgExchange(b'E%.2x' % errno.EPERM)
            raise

        logger.log(e_cmn.MIRE, "Server Response (pre-enc): %r" % res)
        self._doServerResponse(self, res, expect_res)

    def _doServerResponse(self, res, expect_res):
        '''
        Take care of encoding and sending server response messages
        '''
        enc_res = self._lengthEncode(res)


        # if we have a PacketSize set, ship PacketSize-3 (leave room for #cs)
        # is this correct?
        pktsize = self._getFeat(b'PacketSize')
        if pktsize:
            enc_res = enc_res[:pktsize-3]

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
            self.breakPointsSW.append(addr)
            self._serverSetSWBreak(addr)

        elif break_type == b'1':
            self.breakPointsHW.append(addr)
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
            self.breakPointsSW.remove(addr)

        elif break_type == b'1':
            self._serverRemoveHWBreak(addr)
            self.breakPointsHW.remove(addr)

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
        if type(signal) == int:
            res = b'S%.2x' % (signal)

        else:
            #signal better be a (int, dict)
            # regdict should be "regname": <intvalue> pairs
            signal, regdict = signal
            res = b'T%.2x' % (signal)
            res += b';'.join(["%s:%.2x" % (k, v) for k, v in list(regdict.items())])

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
        fields = cmd_data.split(b',')
        addr = fields[0] 
        addr = self._atoi(addr)
        size = fields[1]
        size = self._atoi(size)

        val = self._serverReadMem(addr, size)
        val = hexlify(val)
        
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
        val = unhexlify(val)

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

    def _handleWriteReg(self, cmd_data):
        """
        Handles client requests to write to one register.

        Args:
            reg_data (str): The request packet.

        Returns:
            str: GDB status code
        """
        rpart, vpart = cmd_data.split(b'=')
        ridx = int(rpart, 16)
        rval = self._decodeGDBVal(vpart)
        print("P %r  == %x=%x" % (cmd_data, ridx, rval))

        reg = self._gdb_reg_fmt[ridx]
        reg_name = reg[0]
        self._serverWriteRegValByName(reg_name, rval)

        return b'OK'

    def _serverWriteRegVal(self, ridx, reg_val):
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

    def _serverWriteRegValByName(self, reg_name, reg_val):
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
            reg_val = self._serverReadRegValByName(reg_name)
            registers[reg_name] = reg_val

        reg_pkt = self._buildRegPkt(registers)
        return reg_pkt

    def _handleReadReg(self, cmd_data):
        """
        Instructs the execution engine to read the value of one register.

        Args:
            Register Index

        Returns:
            str: A GDB remote protocol register packet.
        """
        ridx = int(cmd_data, 16)
        reg_val = self._serverReadRegVal(ridx)
        reg_pkt = b"%.2x" % reg_val
        return reg_pkt

    def _serverReadRegVal(self, ridx):
        """
        Returns the value currently stored in a given register.

        Args:
            reg_name (str): The register name.

        Returns:
            int: The value stored in the provided register
        """
        raise Exception('Server translation layer must implement this function')

    def _serverReadRegValByName(self, reg_name):
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
        self._halt_reason = signals.SIG_0
        self._serverCont()

    def _handleEndCont(self):
        '''
        We are no longer running.  Send the response to the client.
        '''
        res = b'S%.2x' % (self._halt_reason)
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

    def _handleBREAK(self):
        """
        Sends a BREAK signal to the execution engine

        Args:
            None

        Returns:
            None
        """
        signal = self._serverCont()
        res = b'S%.2x' % (signal)
        return res
       
    def _serverBREAK(self):
        """
        Halt target execution at the current address.

        Args:
            None

        Returns:
            None
        """
        raise Exception('Server translation layer must implement this function')



    def _handleQuery(self, cmd_data):
        """
        Provides information from the query.  This is a very complex portion 
        of this code.

        Args:
            cmd_data: What type of query, and any other information necessary

        Returns:
            String response with data
        """
        logger.debug("_handleQuery(%r)", cmd_data)
        res = self._serverQuery(cmd_data)
        logger.debug("_handleQuery(%r) => %r", cmd_data, res)
        return res


    def _serverQuery(self, cmd_data):
        """
        Gathers information to respond to a client query.

        Args:
            cmd_data: The query type and context

        Returns:
            String response with appropriate data
        """
        logger.warning("_serverQuery: %r", cmd_data)
        if cmd_data.startswith(b'Supported'):
            logger.debug("QUERY: SUPPORTED STUFF!")
            #TODO: parse what the client asserts it supports and store
            return self._serverQSupported(cmd_data)

        elif cmd_data.startswith(b'Xfer'):
            logger.debug("QUERY: Xfer!")
            return self._serverQXfer(cmd_data)

        elif cmd_data == b'C':
            logger.debug("QUERY: C!")
            return self._serverQC(cmd_data)

        elif cmd_data == b'L':
            logger.debug("QUERY: L!")
            return self._serverQL(cmd_data)

        elif cmd_data == b'TStatus':
            logger.debug("QUERY: TStatus!")
            return self._serverQTStatus(cmd_data)

        elif cmd_data == b'fThreadInfo':
            logger.debug("QUERY: fThreadInfo!")
            return self._serverQfThreadInfo(cmd_data)

        elif cmd_data == b'Attached':
            logger.debug("QUERY: Attached!")
            return self._serverQAttached()


        return b""

    def _handleQSetting(self, cmd_data):
        """
        Provides information from the query.  This is a very complex portion 
        of this code.

        Args:
            cmd_data: What type of query, and any other information necessary

        Returns:
            String response with data
        """
        logger.debug("_handleQSetting(%r)", cmd_data)
        res = self._serverQSetting(cmd_data)
        logger.debug("_handleQSetting(%r) => %r", cmd_data, res)
        return res

    def _serverQSetting(self, cmd_data):
        raise Exception('Server translation layer must implement this function')

    def _handleSetThread(self, cmd_data):
        """
        Provides information from the query.  This is a very complex portion 
        of this code.

        Args:
            cmd_data: What type of query, and any other information necessary

        Returns:
            String response with data
        """
        res = self._serverSetThread(cmd_data)
        return res

    def _serverSetThread(self, cmd_data):
        raise Exception('Server translation layer must implement this function')



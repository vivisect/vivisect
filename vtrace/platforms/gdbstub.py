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

import os
import time
import errno
import base64
import select
import signal
import struct
import socket
import logging
import os.path
import binascii
import itertools
import collections
from lxml import etree
from io import StringIO
from binascii import hexlify, unhexlify

from . import gdb_reg_fmts
from .gdb_reg_fmts import ARCH_META

import envi
import envi.exc as e_exc
import envi.bits as e_bits
import envi.common as e_cmn
import vtrace.platforms.gdb_exc as gdb_exc

from vtrace.platforms import signals

logger = logging.getLogger(__name__)
#e_cmn.initLogging(logger, level=logging.DEBUG)


# Constants for tracking state
STATE_SVR_STARTUP = 0
STATE_SVR_RUNSTART = 1
STATE_SVR_RUNNING = 2
STATE_SVR_SHUTDOWN = 3

STATE_CONN_DISCONNECTED = 0
STATE_CONN_CONNECTED = 1

STATE_TGT_RUNNING = 1
STATE_TGT_PAUSED = 2

SIGNAL_NONE = 0


class GdbDTDResolver(etree.Resolver):
    def resolve(self, url, id, context):
        #logger.debug("Resolving XML URL '%s'", url)
        if url in ('gdb-target.dtd', 'xinclude.dtd'):
            with open(os.path.join(os.path.dirname(__file__), 'dtd', url), 'r') as f:
                return self.resolve_string(f.read(), context)


# constants to make it easier to keep track of which tuple index in the gdb 
# register format is which
REG_FMT_SIZE = 0
REG_FMT_IDX  = 1

# Name and size are first because they are present in both clients and servers, 
# the last two items are only relevant for GDB server stubs.
GDB_TO_ENVI_NAME = 0
GDB_TO_ENVI_SIZE = 1
GDB_TO_ENVI_IDX  = 2
GDB_TO_ENVI_MASK = 3

# Used to track size and number of registers necessary for sending a register 
# packet
REG_PKT_SIZE     = 0
REG_PKT_NUM_REGS = 1

# Generators for encoding register packets
def _pack_8bit(val):
    return val & 0xFF,

def _pack_16bit(val):
    return val & 0xFFFF,

def _pack_32bit(val):
    return val & 0xFFFFFFFF,

def _pack_64bit(val):
    return val & 0xFFFFFFFFFFFFFFFF,

def _pack_le_80bit(val):
    # LSB first
    # 0xAABB_CCDDEEFF (FF EE DD CC BB AA) -> 0xCCDDEEFF, 0xAABB
    return val & 0xFFFFFFFFFFFFFFFF, (val >> 64) & 0xFFFF

def _pack_be_80bit(val):
    # MSB first
    # 0xAABB_CCDDEEFF (AA BB CC DD EE FF) -> 0xAABB, 0xCCDDEEFF
    return (val >> 64) & 0xFFFF, val & 0xFFFFFFFFFFFFFFFF

def _pack_le_128bit(val):
    # LSB first
    # 0xAABBCCDD_EEFFGGHH (HH GG FF EE DD CC BB AA) -> 0xEEFFGGHH, 0xAABBCCDD
    return val & 0xFFFFFFFFFFFFFFFF, (val >> 64) & 0xFFFFFFFFFFFFFFFF

def _pack_be_128bit(val):
    # MSB first
    # 0xAABBCCDD_EEFFGGHH (AA BB CC DD EE FF GG HH) -> 0xAABBCCDD, 0xEEFFGGHH
    return (val >> 64) & 0xFFFFFFFFFFFFFFFF, val & 0xFFFFFFFFFFFFFFFF

def _unpack_simple(values):
    return next(values)

def _unpack_le(values):
    # LSB (lower part) first
    lower = next(values)
    upper = next(values)

    # All split values use a full 64-bit value for the lower component
    return (upper << 64) | lower

def _unpack_be(values):
    # MSB (upper part) first
    upper = next(values)
    lower = next(values)

    # All split values use a full 64-bit value for the lower component
    return (upper << 64) | lower


REG_PKT_CONFIG = (
    # little endian (LSB first)
    {
        8:   ('B',  _pack_8bit,      _unpack_simple),
        16:  ('H',  _pack_16bit,     _unpack_simple),
        32:  ('I',  _pack_32bit,     _unpack_simple),
        64:  ('Q',  _pack_64bit,     _unpack_simple),
        80:  ('QH', _pack_le_80bit,  _unpack_le),
        128: ('QQ', _pack_le_128bit, _unpack_le),
    },

    # big endian (MSB first)
    {
        8:   ('B',  _pack_8bit,      _unpack_simple),
        16:  ('H',  _pack_16bit,     _unpack_simple),
        32:  ('I',  _pack_32bit,     _unpack_simple),
        64:  ('Q',  _pack_64bit,     _unpack_simple),
        80:  ('HQ', _pack_be_80bit,  _unpack_be),
        128: ('QQ', _pack_be_128bit, _unpack_be),
    },
)


class GdbStubBase:
    def __init__(self, arch, psize, bigend, reg, port, find_port=True):
        """
        Base class for consumers of GDB protocol for remote debugging.

        Args:
            arch (str): The architecture of the target being debugged.

            psize (int): The addresss size of the target being debugged
            in bytes (e.g. 8 for x86_64)

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
        self._bigend = bigend
        self._psize = psize

        # Identify the GDB architecture name
        self._gdbarch = self.getGdbArchName()

        # In python 3.7 insertion order for the standard dict type is guaranteed 
        # to maintain insertion order, but to maintain backwards compatibility 
        # we explicitly use the OrderedDict type.
        #
        # If the supplied reg parameter is already a dict we can just pass it as 
        # a parameter, if it is a list or tuple take the first item from each 
        # entry and use that as the key.
        if reg is None:
            self._gdb_reg_fmt = reg

        elif isinstance(reg, (list, tuple)):
            self._gdb_reg_fmt = collections.OrderedDict()
            for entry in reg:
                self._gdb_reg_fmt[entry[0]] = entry[1:]

        elif isinstance(reg, dict):
            self._gdb_reg_fmt = collections.OrderedDict(reg)

        elif isinstance(reg, collections.OrderedDict):
            self._gdb_reg_fmt = reg

        else:
            raise Exception('Bad register format type: %r' % reg)

        # These will get filled in by _genRegPktFmt()
        self._reg_pkt_size = None 
        self._reg_pkt_fmts = {} 
        self._reg_pkt_pack = []
        self._reg_pkt_unpack = []

        if self._gdb_reg_fmt is not None:
            # Statically gather the information necessary to efficiently pack 
            # and unpack register packets.
            self._genRegPktFmt()

            # Now that the gdb register format has been defined when the target XML 
            # was generated, update the index mappings
            self._updateEnviGdbIdxMap()

        # socket overwhich the client talks to the server
        self._gdb_sock = None

        # The list of supported features for a given client-server session
        #TODO: complete the list, but for now the only thing we care about is
        # PacketSize
        self.supported_features = {
            b'PacketSize': None,
            b'QPassSignals': None,
            b'qXfer:memory-map:read': None,
            b'qXfer:features:read': None,
            b'qXfer:exec-file:read': None,
            b'qXfer:threads:read': None,
            b'QStartNoAckMode': None,
            b'multiprocess': None
        }

        self._settings = {}

        self._NoAckMode = False

        # run-length encoding is slow at the moment.
        #self._doEncoding = True
        self._doEncoding = False

    def _getClientFeat(self, featurename, default=False):
        '''
        Like _getFeat() but for the settings the client supports. If the
        feature is not supported (the entry is empty, or '-') then False is
        returned, if the is supported but is just '+' then True is returned,
        otherwise the stored value is returned. 
        '''
        feat = self._settings.get(featurename)
        if feat is None:
            return default
        elif feat == b'-':
            return False
        elif feat == b'+':
            return True
        else:
            return feat

    def _genRegPktFmt(self):
        if self._bigend:
            reg_pkt_fmt = '>'
        else:
            reg_pkt_fmt = '<'

        # keep track of how large of a packet we are building
        size = 0

        self._reg_pkt_fmts = {} 

        self._reg_pkt_pack = []
        self._reg_pkt_unpack = []
        for reg_name, (reg_size, reg_idx) in self._gdb_reg_fmt.items():
            # Get the format and pack/unpack functions
            fmt, packfunc, unpackfunc = REG_PKT_CONFIG[self._bigend][reg_size]
            reg_pkt_fmt += fmt

            # If this object has an emulator attribute get the envi index for 
            # the register (this helps ensure that GdbBaseEmuServer class later 
            # doesn't have to re-define this function).
            # 
            # Otherwise just fill with None because clients won't need to use 
            # that information.
            if hasattr(self, 'emu'):
                envi_idx = self.emu.getRegisterIndex(reg_name)
            else:
                envi_idx = None

            self._reg_pkt_pack.append((packfunc, envi_idx))
            self._reg_pkt_unpack.append((unpackfunc, envi_idx))

            # Size should represent the GDB message length
            size += (reg_size // 8) * 2

            # Save the current register format along with the size of GDB 
            # message (asciified hex) that the format can parse
            self._reg_pkt_fmts[size] = struct.Struct(reg_pkt_fmt)

        # Save the last format as the default packet format if it hasn't been 
        # set yet.
        if self._reg_pkt_size is None:
            self._reg_pkt_size = (size, len(self._gdb_reg_fmt))

    def _updateEnviGdbIdxMap(self):
        self._gdb_to_envi_map = collections.OrderedDict()
        for reg_name, (reg_size, reg_idx) in self._gdb_reg_fmt.items():
            # We only need to save the register name and size in this lookup 
            # table.
            self._gdb_to_envi_map[reg_idx]  = (reg_name, reg_size, None, None)

    def getGdbArchName(self):
        '''
        Returns a GDB-appropriate architecture name for the given architecture/endian/psize
        '''
        return ARCH_META.get((self._arch, self._bigend, self._psize))

    def _getFeat(self, featurename, default=False):
        '''
        If the feature is not supported (the entry is empty, or '-') then False
        is returned, if the is supported but is just '+' then True is returned,
        otherwise the stored value is returned. 
        '''
        feat = self.supported_features.get(featurename)
        if feat is None:
            return default
        elif feat == b'-':
            return False
        elif feat == b'+':
            return True
        else:
            return feat

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
        return sum(cmd) & 0xff

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

        logger.log(e_cmn.MIRE, 'Transmitting packet: %s', pkt)
        self._gdb_sock.sendall(pkt)

    def _recvResponse(self, ack):
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
            raise gdb_exc.GdbClientDetachedException('Socket not responding')

        # If this is an acknowledgment packet, return early
        if ack and res in (b'+', b'-'):
            logger.log(e_cmn.MIRE, '_recvResponse: decoded=%r', res)
            return res

        elif res == b'$':
            pass

        else:
            res = res + self._gdb_sock.recv(10)
            raise Exception('Received unexpected packet: %s' % res)

        # Drop the '#' from the response
        msg_data = self._recvUntil(b'#')[:-1]

        expected_csum = int(self._gdb_sock.recv(2), 16)
        actual_csum = self._gdbCSum(msg_data)
        logger.log(e_cmn.MIRE, "DATA: %r     CSUM: %#.2x (calculated: %#.2x)", msg_data, actual_csum, expected_csum)
        if expected_csum != actual_csum:
            raise gdb_exc.InvalidGdbPacketException("Invalid Packet (checksum): %#.2x != %#.2x (%r)" % (actual_csum, expected_csum, msg_data))

            raise Exception('Invalid packet data checksum')

        if ack:
            # only send Ack if this is *not* an Ack/Retrans and if everything 
            # checks out ok (checksum, $/#/etc)
            self._sendAck()

        decoded = self._lengthDecode(msg_data)
        logger.log(e_cmn.MIRE, '_recvResponse: decoded=%r', decoded)
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

    def _recvUntil(self, *clist):
        """
        Recieve data from the socket until the specified character is reached.

        Args:
            c (str): the character to read until.

        Returns:
            str: The characters read up until and including the delimiting
            character.
        """
        #logger.log(e_cmn.MIRE, "_recvUntil(%r)", clist)
        ret = b''
        x = b''
        while x not in clist:
            x = self._gdb_sock.recv(1)
            if len(x) == 0:
                raise gdb_exc.GdbClientDetachedException('Socket closed unexpectedly')
            ret += x
        #logger.log(e_cmn.MIRE, '_recvUntil(%r):  %r', clist, ret)
        return ret

    def _msgExchange(self, msg, expect_res=True, ack=None):
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
        logger.debug('_msgExchange: %r %r %r(%r)', msg, expect_res, ack, self._NoAckMode)

        if ack is None:
            ack = not self._NoAckMode

        retry_count = 0
        retry_max = 10
        status = None
        res = None

        if not ack:
            logger.debug('sending msg: %r', msg)
            self._sendMsg(msg)
        else:
            # Send the command until its receipt is acknowledged
            while (status != b'+') and (retry_count < retry_max):
                logger.debug('(attempt %d) msg: %r', retry_count, msg)
                self._sendMsg(msg)
                status = self._recvResponse(ack)
                retry_count += 1
            if retry_count >= retry_max:
                err = '_msgExchange: No Ack received in retry_max (%r) attempts!' % retry_max
                logger.warning(err)
                raise Exception(err)

        # Return the response
        if expect_res:
            res = self._recvResponse(ack)
        else:
            res = status

        logger.log(e_cmn.MIRE, '_msgExchange: response = %r', res)

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
            try:
                self._gdb_sock.shutdown(2)
            except OSError as e:
                if e.errno == errno.ENOTCONN:
                    pass
                else:
                    raise e

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
        def _getvalues(num_regs):
            for i, reg_val in enumerate(reg_state.values()):
                if i == num_regs:
                    break
                for val in self._reg_pkt_pack[i][0](reg_val):
                    yield val

        # First generate the binary data (use the default packet size)
        size, num_regs = self._reg_pkt_size
        data = self._reg_pkt_fmts[size].pack(*_getvalues(num_regs))

        # Now convert it to the weird asciified format that GDB uses
        return data.hex().encode()

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
        # Update the default register packet size
        size = len(pkt)

        # First convert the packet from the weird asciified format that GDB uses 
        # and then unpack the values
        values = iter(self._reg_pkt_fmts[size].unpack(bytes.fromhex(pkt.decode())))

        # Save the registers in the packet into an ordered dictionary so they 
        # can be accessed in the correct order.
        regs = collections.OrderedDict()

        try:
            # Now save the results, if we run out of packets then just stop 
            # processing, it means the client didn't supply as many 
            for reg_name, (unpack_func, _) in \
                    zip(self._gdb_reg_fmt, self._reg_pkt_unpack):
                regs[reg_name] = unpack_func(values)

        except StopIteration:
            # If we've run out of values, just stop processing
            logger.debug('Stopped processing register packet @ %s', reg_name)

        # If necessary update the register packet size and number of registers 
        # contained in it.
        if self._reg_pkt_size[REG_PKT_SIZE] != size:
            logger.debug('Updating register packet size from %d/%d to %d/%d',
                         self._reg_pkt_size[REG_PKT_SIZE],
                         self._reg_pkt_size[REG_PKT_NUM_REGS],
                         size, len(regs))
            self._reg_pkt_size = (size, len(regs))

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

        # Run Length encoding (from
        # https://sourceware.org/gdb/onlinedocs/gdb/Overview.html#Overview):
        #
        # Response data can be run-length encoded to save space. Run-length 
        # encoding replaces runs of identical characters with one instance of 
        # the repeated character, followed by a ‘*’ and a repeat count. The 
        # repeat count is itself sent encoded, to avoid binary characters in 
        # data: a value of n is sent as n+29. For a repeat count greater or 
        # equal to 3, this produces a printable ASCII character, e.g. a space 
        # (ASCII code 32) for a repeat count of 3. (This is because run-length 
        # encoding starts to win for counts 3 or more.) Thus, for example, ‘0* ’ 
        # is a run-length encoding of “0000”: the space character after ‘*’ 
        # means repeat the leading 0 32 - 29 = 3 more times.
        #
        # The printable characters ‘#’ and ‘$’ or with a numeric value greater 
        # than 126 must not be used. Runs of six repeats (‘#’) or seven repeats 
        # (‘$’) can be expanded using a repeat count of only five (‘"’). For 
        # example, ‘00000000’ can be encoded as ‘0*"00’. 

        splat = ord('*')
        quote = ord('"')
        tilde = ord('~')

        encoded = bytearray()
        for char, groupiter in itertools.groupby(data):
            group = bytes(groupiter)
            while group:
                # The lengths checked for included the initial character, so 
                # instead of checking for <3, ==6, ==7, and <=97 we need to 
                # check for <4, ==7, ==8, and <=98.
                if len(group) < 4:
                    encoded += group
                    break

                elif len(group) == 7:
                    # 29 + 6 ('#') is not a permitted repeat char
                    encoded.append(char)
                    encoded.append(splat)
                    encoded.append(quote)  # 29 + 5
                    encoded.append(char)
                    break

                elif len(group) == 8:
                    # 29 + 7 ('$') is not a permitted repeat char
                    encoded.append(char)
                    encoded.append(splat)
                    encoded.append(quote)  # 29 + 5
                    encoded.append(char)
                    encoded.append(char)
                    break

                elif len(group) <= 98: 
                    # Max repeat character is 29 + 97 ('~')
                    encoded.append(char)
                    encoded.append(splat)

                    # Subtract 1 for the initial character
                    encoded.append(29 + len(group) - 1)
                    break

                else:
                    # Add the max chunk and let the loop go one more time.
                    encoded.append(char)
                    encoded.append(splat)
                    encoded.append(tilde)

                    # Remove the initial character plus the 97 following 
                    # characters from the "to be encoded" list
                    group = group[98:]

        return encoded

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
        return b'%.2x' % val

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

        logger.log(e_cmn.MIRE, 'Sending message: %s', msg)

        # Build the command packet
        pkt = self._buildPkt(msg)

        # Transmit the packet
        self._transPkt(pkt)


class GdbClientStub(GdbStubBase):
    """
    The GDB client stub code. GDB clients should inherit from this class.
    """
    # TODO: make a "discovery" mode which pulls target.xml instead of requiring an architecture up front
    def __init__(self, arch, psize, bigend, reg, host, port, servertype):
        """
        The GDB client stub.

        Args:
            arch (str): The architecture of the target being debugged.

            psize (int): The addresss size of the target being debugged
            in bytes (e.g. 8 for x86_64)

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
        GdbStubBase.__init__(self, arch, psize, bigend, reg, port)

        self._gdb_host = host
        self._gdb_servertype = servertype
        self._offsets = None

        self._xml = {}
        self._symbols = {}

    def gdbDetach(self):
        """
        Detaches from the GDB server.

        Args:
            None

        Returns:
            None
        """
        try:
            self._sendMsg(b'D')
        except OSError as e:
            # If transmit failed when disconnecting we can just ignore it
            if e.errno == errno.EBADF:
                self._gdb_sock = None
            else:
                raise e
        self._disconnectSocket()

    def __del__(self):
        """
        gracefully disconnect client objects
        """
        if self._gdb_sock is not None:
            self.gdbDetach()

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

        self._gdb_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._gdb_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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
        # Clear any cached XML files
        self._xml = {}

        # Clear any cached symbols
        self._symbols = {}

        self._connectSocket()
        if self._gdb_servertype in ('gdbserver', 'serverstub', 'qemu'):
            self._targetRemote()
        else:
            logger.warning("%r is not 'gdbserver', 'serverstub', or 'qemu', not initializing handshake", self._gdb_servertype)

        self._postAttach()

    def _postAttach(self):
        '''
        A hook for subclasses to insert functionality after attaching to a
        GDB Server
        '''
        pass

    def _targetRemote(self, options=None):
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

        self.qSupported(options=options)

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
        # TODO: support reading extra data with qXfer:auxv:read
        # TODO: Support pulling the target binary with qXfer:exec-file:read and
        # vFile:* commands (example from gdb<->gdbserver exchange):
        #
        #   gdb:        $qXfer:exec-file:read:10311:0,1000#0f
        #   gdbserver:  $l/home/aaron/Documents/GRIMM/EMULATE/vivtestfiles/linux/amd64/static64.llvm.elf#3c
        #   gdb:        $vFile:setfs:0#bf
        #   gdbserver:  $F0#76
        #   gdb:        $vFile:open:6a7573742070726f62696e67,0,1c0#ed
        #   gdbserver:  $F-1,2#02
        #   gdb:        $vFile:setfs:10311#85
        #   gdbserver:  $F0#76
        #   gdb:        $vFile:open:2f686f6d652f6161726f6e2f446f63756d656e74732f4752494d4d2f454d554c4154452f7669767465737466696c65732f6c696e75782f616d6436342f73746174696336342e6c6c766d2e656c66,0,0#bb
        #   gdbserver:  $F5#7b
        #   gdb:        $vFile:pread:5,47ff,0#6a
        #   gdbserver:  $F46bf;.ELF..... <ELF binary>
        #
        # TODO: make these functional and configurable
        self._msgExchange(b'Hc0')
        self._msgExchange(b'qC')
        self._msgExchange(b'Hg0')
        self.gdbGetOffsets()

        # Symbols take a long time to retrieve from the vivisect GDB server, 
        # don't ask for them by default.
        #self.gdbGetSymbol(b'main')

    def qSupported(self, options=None):
        supported_cmd = 'qSupported'

        if options is None:
            options = []

        # native GDB exchanges this supported string when connecting to the
        # target server (spaces added for clarity):
        #
        #   +$ qSupported : multiprocess +;
        #   swbreak +; hwbreak +; qRelocInsn +; fork-events +; vfork-events +;
        #   exec-events +; vContSupported +; QThreadEvents +; no-resumed
        #   +; memory-tagging +; xmlRegisters=i386 #77
        #
        # The default support options
        options += ['swbreak', 'hwbreak', 'vContSupported']

        assert self._gdbarch is not None
        xmlreg_opt = 'xmlRegisters=%s' % self._gdbarch.split(':')[0]
        options.append(xmlreg_opt)

        supported_cmd += ':' + '+;'.join(options)
        res = self._msgExchange(supported_cmd.encode())
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

            logger.debug("feature processing: f_name: %r\t f_val: %r", f_name, f_val)
            if f_name in self.supported_features.keys():
                self.supported_features[f_name] = f_val

        # Normalize the PacketSize supported feature
        #logger.warning("PacketSize: %r", self.supported_features.get(b'PacketSize', '1000'))
        size = int(self._getFeat(b'PacketSize', default=b'1000'), 16)
        self.supported_features[b'PacketSize'] = size

        if self._getFeat(b'QStartNoAckMode'):
            logger.warning('Trying to start NoAck mode')
            res = self._msgExchange(b'QStartNoAckMode')
            if res == b'OK':
                self._NoAckMode = True
            else:
                self._NoAckMode = False

    def gdbGetSymbols(self):
        symbols = {}

        # Send qSymbol:: to start request the next symbol, when the answer is OK 
        # then the target has no more symbols
        res = self._msgExchange(b'qSymbol::')
        while res != b'OK' and not res.startswith(b'E'):
            if not res.startswith(b'qSymbol:'):
                raise Exception('Unexpected response to qSymbol:: %r' % res)
            answer = res[8:]

            # Some gdb servers return names with no addresses
            if b':' not in answer:
                self._symbols[unhexlify(answer)] = None
            else:
                name, addr = answer.split(b':')
                self._symbols[unhexlify(name)] = self._decodeGDBVal(addr)

            # Now ask for the next one
            res = self._msgExchange(b'qSymbol::')

    def gdbGetSymbol(self, symbol):
        # If symbols have have already been retrieved, look up the specific 
        # symbol
        if not self._symbols:
            self.gdbGetSymbols()

        return self._symbols[symbol]

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
        # Ensure that the params are in bytes:
        if isinstance(qtype, str):
            qtype = qtype.encode()
        if isinstance(cmd, str):
            cmd = cmd.encode()
        if isinstance(name, str):
            name = name.encode()

        # Subtract 5 bytes from the max size to account for the start/end bytes
        size = self.supported_features[b'PacketSize'] - 5

        off = 0
        out = []
        while True:
            msg = b'qXfer:' + qtype + b':' + cmd + b':' + name + b':' + \
                    format(off, 'x').encode() + b',' + format(size, 'x').encode()
            data = self._msgExchange(msg)
            res = None
            if len(data):
                res = data[0:1]
                msg = data[1:]
                if res in (b'm', b'l'):
                    out.append(msg)
                    off += len(msg)
                else:
                    logger.warning("qXfer:%s:%s:%s [off=0x%x]: unexpected response: %r", qtype, cmd, name, off, data)
            else:
                # If the response was empty then this type of query is not 
                # supported
                logger.warning('WARNING qXfer not supported: %r', msg)
                return b''

            # Go until the server indicates the response is done
            if res == b'l':
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
                        #logger.debug('%#x-%#x: %r', off+qoff-5, off+qoff+5, data)

                except Exception as e:
                    logger.exception('failed to read %#x-%#x from gdb', off+qoff-5, off+qoff+5)

                maps.append((qoff, off, 7, b'offmap-%s' % offname))
                # TODO: scour large amount of address space looking for maps?

        return maps

    def gdbGetFeatureFile(self, fname=b'target.xml'):
        if isinstance(fname, str):
            fname = fname.encode()
        if fname not in self._xml:
            data = self.qXfer(b'features', name=fname)
            if not data:
                raise Exception('Error occurred while retrieving feature file %s' % fname)

            parser = etree.XMLParser(recover=True, load_dtd=True)
            parser.resolvers.add(GdbDTDResolver())
            self._xml[fname] = etree.parse(StringIO(data.decode()), parser)
        return self._xml[fname]

    def _getRegsInfoFromXml(self, root, index=0):
        regs = []
        for elem in root:
            if not isinstance(elem, etree._Comment):
                if elem.tag == 'feature' and len(elem) > 0:
                    regs.extend(self._getRegsInfoFromXml(elem, index))

                elif elem.tag == 'reg':
                    name = elem.get('name')
                    bitsize = int(elem.get('bitsize'))
                    regnum = elem.get('regnum')

                    if regnum is not None:
                        index = int(regnum)

                    regs.append((index, name, bitsize))

                    index += 1
        return regs

    def _processTargetMeta(self):
        """
        Takes a specific GDB target XML file and turns it into the expected list of
        3-tuple objects contained in this file.

        NOTE: If this function is used to update the internal _gdb_reg_fmt, then
        """
        # The registers will need to be added to the returned register format in 
        # ascending order of the register indexes/numbers
        regs = []

        # First get the "target" XML and then identify the real XML file name
        tgt_xml = self.gdbGetFeatureFile('target.xml')

        # See if there is another XMl file we need to retrieve
        for elem in tgt_xml.getroot():
            if not isinstance(elem, etree._Comment) and \
                    elem.tag in ('xi:include', '{http://www.w3.org/2001/XInclude}include'):
                filename = tgt_xml.getroot().getchildren()[1].get('href')
                tgt_xml = self.gdbGetFeatureFile(filename)
                break

        regs = self._getRegsInfoFromXml(tgt_xml.getroot())

        # sort the collected registers by index and create the necessary GDB 
        # register format
        reg_fmt = collections.OrderedDict((n, (s, i)) for i, n, s in sorted(regs))
        return reg_fmt

    def gdbGetRegister(self, regidx):
        """
        Gathers and returns the contents of the specified registers (all
        if no registers are specified)

        Args:
            regidx (int): target-specific register index to dump.

        Returns:
            integer value
        """
        reg = format(regidx, 'x').encode()
        #logger.debug('Requesting register %s', reg)
        cmd = b"p" + reg
        res = self._msgExchange(cmd)

        if res[0:1] == b'E':
            raise Exception('Error occurred while dumping register info: %s'
                % res[1:])

        elif res == b'':
            # If the response is empty then we have to get the value from the 
            # "read all registers" packet
            all_regs = self.gdbGetRegisters()
            reg_name = self._gdb_to_envi_map[regidx][GDB_TO_ENVI_NAME]
            return all_regs[reg_name]

        else:
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

        reg_name = self._gdb_to_envi_map[regidx][GDB_TO_ENVI_NAME]
        reg_size = self._gdb_to_envi_map[regidx][GDB_TO_ENVI_SIZE]
        val_str = self._encodeGDBVal(val, reg_size)
        cmd = b'P' + self._encodeGDBVal(regidx) + b'=' + val_str
        res = self._msgExchange(cmd)

        if res[0:1] == b'E':
            logger.warning('Setting register %d (%s) failed with error %s',
                           regidx, reg_name, res[1:3])

        elif res == b'':
            # If the response is empty then we have to change the value using 
            # the "set all registers" packet, for some reason GDB servers do 
            # this with "general" registers
            self.gdbSetRegisters({reg_name: val})

    def gdbGetRegisterByName(self, regname):
        """
        Gathers and returns the contents of the specified registers (all
        if no registers are specified)

        Args:
            regname (str): register name to dump.

        Returns:
            integer value
        """
        try:
            reg_idx = self._gdb_reg_fmt[regname][REG_FMT_IDX]
            return self.gdbGetRegister(reg_idx)
        except IndexError:
            raise e_exc.InvalidRegisterName("Invalid Register Name in gdbGetRegisterByName: %r" % regname)

    def gdbSetRegisterByName(self, name, val):
        """
        Set a register with a new value.

        Args:
            regname (str): target-specific register name (see target.xml for best answer)
            val (int):  new value for the register

        Returns:
            None
        """
        try:
            reg_idx = self._gdb_reg_fmt[name][REG_FMT_IDX]
            self.gdbSetRegister(reg_idx, val)
        except IndexError:
            raise e_exc.InvalidRegisterName("Invalid Register Name in gdbSetRegisterByName(%r, %r)" % (name, val))

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
        #logger.debug('Requesting register state')
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
                logger.warning('Register %s not part of general registers', reg_name)
                continue
            cur_reg_vals[reg_name] = updates[reg_name]

        reg_pkt_data = self._buildRegPkt(cur_reg_vals)
        cmd = b'G%s' % reg_pkt_data
        self._msgExchange(cmd)

    setRegisters = gdbSetRegisters

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
            logger.warning('Setting %s breakpoint is not supported', bp_type)
        elif res[0:1] == b'E':
            logger.warning('Setting breakpoint failed with error %s', res[1:3])

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
            logger.warning('Removing %s breakpoint is not supported', bp_type)
        elif res[0:1] == b'E':
            logger.warning('Removing breakpoint failed with error %s', res[1:3])

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
        if self._getFeat(b'multiprocess'):
            cmd = b'vCont;c'
        else:
            cmd = b'c'

            if addr is not None:
                cmd += b'%s' % addr

        # send packet but don't wait for a reply.  It's not coming until the
        # target halts again.
        self._msgExchange(cmd)

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
            return self._recvResponse(ack=not self._NoAckMode)

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
                count = int(res[2:4], 16)
                done = res[4]
                argthreadid = res[5:13]
                threads = [int(res[x+13:x+21], 16) for x in range(count)]
                out.extend(threads)

                # get the next volley
                res = self._msgExchange(b'qL0ff00000000')

        # young whippersnapper
        if self._getFeat(b'multiprocess'):
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

        # Convert the value to its GDB protocol format, address and memory 
        # contents are in readable order so they do not have to be endian 
        # swapped
        cmd = b'm%.2x,%.2x' % (addr, length)
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
        # Convert the value to its GDB protocol format, address and memory 
        # contents are in readable order so they do not have to be endian 
        # swapped
        if isinstance(val, bytes):
            val_str = hexlify(val)
        elif isinstance(val, str):
            val_str = hexlify(val.encode())
        elif isinstance(val, int):
            val_str = self.itoa(val)
        else:
            raise Exception('Unable to convert value %r to writable form' % val)

        write_length = len(val_str) // 2

        # Could also be written with: X addr,length:binary_data
        cmd = b'M%.2x,%.2x:%s' % (addr, write_length, val_str)
        res = self._msgExchange(cmd)

        if res == b'OK':
            pass
        elif res[0:1] == b'E':
            raise Exception('Error code %s received after attempt to write memory' %
                (res[1:3]))
        else:
            raise Exception('Unexpected response to writing memory: %s' % res)

    def gdbStepi(self, addr=None):
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
            ret.append(p.split(b':'))

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
            raise Exception('Client received unexpected reply/stop packet: %s' %
                            pkt_data)

        return data


class GdbServerStub(GdbStubBase):
    """
    The GDB server stub code. GDB server implementations should inherit from
    this class. Functions that start with '_server' must be implemented by
    the code controlling the debugged process (e.g. the vivisect emulator).
    """
    def __init__(self, arch, psize, bigend, reg, port, find_port=True):
        """
        The GDB sever stub.

        Args:
            arch (str): The architecture of the target being debugged.

            psize (int): The addresss size of the target being debugged
            in bytes (e.g. 8 for x86_64)

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
        GdbStubBase.__init__(self, arch, psize, bigend, reg, port, find_port)

        # Set the features supported by this server
        self.supported_features = {
            b'PacketSize': 0x1000,
            b'QPassSignals': None,
            b'qXfer:memory-map:read': b'+',
            b'qXfer:features:read': b'+',
            b'qXfer:exec-file:read': b'+',
            b'qXfer:threads:read': b'+',
            b'QStartNoAckMode': b'+',
            b'multiprocess': b'+',
        }

        self.gdb_server_state = STATE_SVR_STARTUP

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

        self._halt_reason = 0

    def _serverQSupported(self, cmd_data):
        # Build the list of supported features from the configuration dictionary
        features = []
        for feat, val in self.supported_features.items():
            if isinstance(val, int):
                features.append(b'%s=' % feat + self._encodeGDBVal(val))
            elif isinstance(val, bytes):
                # If the value is '+' just append it without '='
                if val == b'+':
                    features.append(feat + val)
                else:
                    features.append(feat + b'=' + val)
            elif isinstance(val, str):
                # the features should always be in bytes no matter what
                # If the value is '+' just append it without '='
                if val == b'+':
                    features.append(feat + val.encode())
                else:
                    features.append(feat + b'=' + val.encode())

        return b';'.join(features)

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
            data += self._recvUntil(b'#', b'\x03')
            #logger.log(e_cmn.MIRE, "_recvServer(%d): data=%r", self.gdb_server_state, data)
            if data == b'\x03':
                #logger.info("Received BREAK!  Raising GdbBreakException")
                raise gdb_exc.GdbBreakException()

            if len(data) > maxlen:
                #logger.warning("fail: len(data): %d   maxlen: %d", len(data), maxlen)
                raise gdb_exc.InvalidGdbPacketException("Invalid Packet: %r" % data)

        #logger.log(e_cmn.MIRE, "done with read loop:  %r", data)

        # state housekeeping
        if self.gdb_server_state == STATE_SVR_RUNSTART:
            self.gdb_server_state = STATE_SVR_RUNNING
            if data[0:1] == b'+':
                # meh, housewarming gift.  eat it.
                data = data[1:]

        # now do our packet checks
        if data[0:1] != b'$':
            #logger.warning("fail: data doesn't start with '$'")
            raise gdb_exc.InvalidGdbPacketException("Invalid Packet: %r" % data)

        # Drop the '$' and '#' delimiters, we don't need them now
        data = data[1:-1]

        # pull the checksum bytes
        csum = int(self._gdb_sock.recv(2), 16)
        calccsum = self._gdbCSum(data)
        logger.log(e_cmn.MIRE, "DATA: %r     CSUM: %#.2x (calculated: %#.2x)", data, csum, calccsum)
        if csum != calccsum:
            raise gdb_exc.InvalidGdbPacketException("Invalid Packet (checksum): %#.2x != %#.2x (%r)" % (csum, calccsum, data))

        # Acknowledge the packet
        if not self._NoAckMode:
            self._sendAck()

        return data


    def runServer(self, oneshot=False):
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
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        while True:
            try:
                self._server_sock.bind(('localhost', self._gdb_port))
                break

            except OSError as e:
                if not self._gdb_find_port:
                    raise e


        self._server_sock.listen(1)
        logger.info("runServer listening on port %d", self._gdb_port)

        self.gdb_server_state = STATE_SVR_STARTUP

        while self.gdb_server_state in (STATE_SVR_RUNNING, STATE_SVR_RUNSTART, STATE_SVR_STARTUP):
            try:
                self.gdb_server_state = STATE_SVR_RUNSTART
                self._gdb_sock, addr = self._server_sock.accept()
                self._gdb_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.connstate = STATE_CONN_CONNECTED
                logger.info("runServer: Received Connection from %r", addr)

                self._postClientAttach(addr)
                self.last_reason = self._halt_reason

                while self.connstate == STATE_CONN_CONNECTED:
                    try:
                        # Check and handle the processor breaking.
                        if self._halt_reason != 0 and \
                                self._halt_reason != self.last_reason:
                            # send the halt reason to the client (since they 
                            # should be waiting for it...
                            self._doServerResponse(self._handleEndCont())

                        self.last_reason = self._halt_reason

                        # check to see if there's any data to process
                        x, y, z = select.select([self._gdb_sock],[],[], .1)
                        if not x:
                            continue

                        # if the client has sent command data, handle it here.
                        data = self._recvServer()
                        self._cmdHandler(data)  

                    except (gdb_exc.GdbClientDetachedException,
                            ConnectionResetError) as e:
                        logger.debug("Client disconnected: %r", e)
                        res = self._handleDetach()
                        break

                    except gdb_exc.InvalidGdbPacketException as e:
                        logger.warning("Invalid Packet Exception!  %r", e)
                        self._sendRetrans()
                        continue

                    except gdb_exc.GdbBreakException as e:
                        logger.info("Received BREAK signal: %r", e)
                        data = b'\x03'

                    except BrokenPipeError:
                        logger.info("BrokenPipeError:  Client disconnected.")
                        self.connstate = STATE_CONN_DISCONNECTED

            except Exception as e:
                logger.critical("runServer exception!", exc_info=1)

            finally:
                if oneshot:
                    logger.info("'oneshot' enabled, shutting down GDB Server")
                    self.gdb_server_state = STATE_SVR_SHUTDOWN

                if self._gdb_sock:
                    self._gdb_sock.close()

        logger.info("GDB Server shutting down server socket")
        self._server_sock.close()
        logger.info("GDB Server Shutdown Complete")

    def _postClientAttach(self, addr):
        # Initialize information about the client connection
        self._NoAckMode = False

        # Clear out the client settings
        self._settings = {}

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
        #logger.debug('Server received command: %s', cmd)
        expect_res = False

        # The client expects the ack/noack mode to remain consistent while 
        # processing a single message so get the current value of 
        # QStartNoAckMode in case it is changed by the current command.
        ack = not self._NoAckMode

        # TODO: the error codes could be finer-grain
        try:
            if cmd == b'?':
                #logger.info('_handleHaltInfo(%r)', cmd_data)
                res = self._handleHaltInfo()
            elif cmd == b'g':
                #logger.info('_handleReadRegs(%r)', cmd_data)
                res = self._handleReadRegs()
            elif cmd == b'G':
                #logger.info('_handleWriteRegs(%r)', cmd_data)
                res = self._handleWriteRegs(cmd_data)
            elif cmd == b'p':
                #logger.info('_handleReadReg(%r)', cmd_data)
                res = self._handleReadReg(cmd_data)
            elif cmd == b'P':
                #logger.info('_handleWriteReg(%r)', cmd_data)
                res = self._handleWriteReg(cmd_data)
            elif cmd == b'c':
                #logger.info('_handleCont(%r)', cmd_data)
                res = self._handleCont()
            elif cmd == b'D':
                #logger.info('_handleDetach(%r)', cmd_data)
                res = self._handleDetach()
            elif cmd == b'Z':
                #logger.info('_handleSetBreak(%r)', cmd_data)
                res = self._handleSetBreak(cmd_data)
            elif cmd == b'z':
                #logger.info('_handleRemoveBreak(%r)', cmd_data)
                res = self._handleRemoveBreak(cmd_data)
            elif cmd == b'm':
                #logger.info('_handleReadMem(%r)', cmd_data)
                res = self._handleReadMem(cmd_data)
            elif cmd == b'M':
                #logger.info('_handleWriteMem(%r)', cmd_data)
                res = self._handleWriteMem(cmd_data)
            elif cmd == b's':
                #logger.info('_handleStepi(%r)', cmd_data)
                res = self._handleStepi()
            elif cmd == b'H':
                #logger.info('_handleSetThread(%r)', cmd_data)
                res = self._handleSetThread(cmd_data)
            elif cmd == b'q':
                #logger.info('_handleQuery(%r)', cmd_data)
                res = self._handleQuery(cmd_data)
            elif cmd == b'Q':
                #logger.info('_handleQSetting(%r)', cmd_data)
                res = self._handleQSetting(cmd_data)
            elif cmd == b'v':
                #logger.info('_handleQSetting(%r)', cmd_data)
                res = self._handleVOperation(cmd_data)
            elif cmd == b'\x03':
                #logger.info('_handleBreak(%r)', cmd_data)
                res = self._handleBreak()

            else:
                #raise Exception(b'Unsupported command %s' % cmd)
                logger.warning('Unsupported command %s (%r)', cmd, cmd_data)
                res = b''

        except Exception as e:
            import sys, traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            traceback.print_exception(exc_value)
            logger.warning("_cmdHandler(%r): EXCEPTION: %r", data, e)
            self._msgExchange(b'E' + self._encodeGDBVal(errno.EPERM))
            raise

        #logger.log(e_cmn.MIRE, "Server Response (pre-enc): %r", res)
        self._doServerResponse(res, expect_res=expect_res, ack=ack)

    def _doServerResponse(self, res, expect_res=False, ack=None):
        '''
        Take care of encoding and sending server response messages
        '''
        enc_res = self._lengthEncode(res)

        # If we have a PacketSize set, ship PacketSize - 5 (leave room for the 
        # start and end of the packet
        pktsize = self._getFeat(b'PacketSize')
        if pktsize and len(enc_res) > pktsize - 5:
            logger.error('encoded response length %d > %d, truncating msg',
                         len(enc_res), pktsize - 5)
            enc_res = enc_res[:pktsize - 5]

        self._msgExchange(enc_res, expect_res=expect_res, ack=ack)

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

    def _handleVOperation(self, cmd_data):
        if cmd_data.startswith(b'File:'):
            #logger.debug("Operation: File!")
            res = self._serverVFile(cmd_data[5:])
        elif cmd_data.startswith(b'Cont'):
            #logger.debug("Operation: Cont!")
            res = self._serverVCont(cmd_data[4:])
        else:
            # Unrecognized 'v' commands should be replied to with an empty 
            # string
            res = b''

        return res

    def _serverVFile(self, cmd_data):
        raise Exception('Server translation layer must implement this function')

    def _parsePID(self, data):
        # PID format: pPID.TID, TID is optional
        if b'.' in data:
            pid, tid = data[1:].split(b'.')
            return self._decodeGDBVal(pid), self._decodeGDBVal(tid)
        else:
            # only the pid has been supplied
            return self._decodeGDBVal(data[1:]), None

    def _serverVCont(self, cmd_data):
        """
        Handles modern vCont packets

        Args:
            cmd_data (str): The client request body.

        Returns:
            str: The GDB status code.
        """
        if cmd_data == b'?':
            # Return the supported functionality
            #   c:              continue
            #   C??:            continue with signal
            #   s:              step
            #   S??:            step with signal
            #   t:              stop (only relevant in non-stop mode)
            #   rstart,end:     run (if start <= addr < end)

            # We only support continue, and step
            return b'vCont;c;C;s;S'

        elif cmd_data.startswith(b';'):
            responses = []

            # Parse the supported commands
            for cmd in cmd_data[1:].split(b';'):
                if cmd.startswith(b'c:'):
                    pid, tid = self._parsePID(cmd[2:])
                    if pid in self.processes and tid != -1:
                        logger.debug('continuing %d.%d (%r)', pid, tid, cmd)
                        responses.append(self._handleCont())

                elif cmd.startswith(b'C'):
                    sig = self._decodeGDB(cmd[1:3])
                    pid, tid = self._parsePID(cmd[4:])
                    if pid in self.processes and tid != -1:
                        logger.debug('continuing %d.%d with signal %d (%r)', pid, tid, sig, cmd)
                        responses.append(self._handleCont(sig))

                elif cmd.startswith(b's:'):
                    pid, tid = self._parsePID(cmd[2:])
                    if pid in self.processes and tid != -1:
                        logger.debug('stepping %d.%d (%r)', pid, tid, cmd)
                        responses.append(self._handleStepi())

                elif cmd.startswith(b'S'):
                    sig = self._decodeGDB(cmd[1:3])
                    pid, tid = self._parsePID(cmd[4:])
                    if pid in self.processes and tid != -1:
                        logger.debug('stepping %d.%d with signal %d (%r)', pid, tid, sig, cmd)
                        responses.append(self._handleStepi(sig))

            # Return the responses joined with ';'
            return b';'.join(responses)

        else:
            # Something we don't support
            logger.warning("Unsupported action for vCont: %r", cmd_data)
            return b''

    def _handleSetBreak(self, cmd_data):
        """
        Handles requests to set different types of breakpoints.

        Args:
            cmd_data (str): The client request body.

        Returns:
            str: The GDB status code.
        """
        break_type, addr = self._parseBreakPkt(cmd_data)

        try:
            if break_type == 48:    # b'0'
                self.breakPointsSW.append(addr)
                return self._serverSetSWBreak(addr)

            elif break_type == 49:  # b'1'
                self.breakPointsHW.append(addr)
                return self._serverSetHWBreak(addr)

            else:
                raise Exception('Unsupported breakpoint type: %s' % break_type)

        except ValueError:
            # address wasn't in the list
            logger.log('Unable to add breakpoint %d %#x', break_type, addr)
            return b'E01'

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

        try:
            if break_type == 48:    # b'0'
                self.breakPointsSW.remove(addr)
                return self._serverRemoveSWBreak(addr)

            elif break_type == 49:  # b'1'
                self.breakPointsHW.remove(addr)
                return self._serverRemoveHWBreak(addr)

            else:
                raise Exception('Unsupported breakpoint type: %s' % break_type)

        except ValueError:
            # address wasn't in the list
            logger.log('Unable to remove breakpoint %d %#x', break_type, addr)
            return b'E01'

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

        # Example msg exchange of halt info
        #   $ ? #3f
        #   $ T05 06:0*, ; 07:a0dcf*"7f0* ; 10:400a40*' ; thread:p10311.10311 ; 
        #   core:9 ; #65

        signal = self._serverGetHaltSignal()
        extrainfo = []
        if isinstance(signal, int):
            res = b'S' + self._encodeGDBVal(signal)

        else:
            #signal better be a (int, dict)
            # regdict should be regidx:regval pairs
            signal, regdict = signal
            res = b'T' + self._encodeGDBVal(signal)
            for regidx, regval in regdict.items():
                extrainfo.append(self._encodeGDBVal(regidx) + b':' + self._encodeGDBVal(regval))

        # TODO: get the thread and core info if both the server and client 
        # support the "multiprocess" feature?
        extrainfo.append(b'thread:' + self._serverGetThread())
        extrainfo.append(b';core:' + self._serverGetCore())

        res += b';'.join(extrainfo)

        # TODO: properly handle the different types of possible response 
        # situations described in:
        # https://sourceware.org/gdb/onlinedocs/gdb/Stop-Reply-Packets.html#Stop-Reply-Packets

        return res

    def _serverGetHaltSignal(self):
        """
        Returns the signal number responsible for the current halt.

        Args:
            None

        Returns:
            int: The signal number corresponding to the halt.
        """
        # Fallback server behavior
        return self._halt_reason

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

        return self._serverWriteMem(addr, val)

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

    def _handleWriteRegs(self, pkt):
        """
        Handles client requests to write to registers.

        Args:
            pkt (str): The request packet.

        Returns:
            str: GDB status code
        """
        # TODO: Handle clients that don't send as many register values as 
        # expected

        # First convert the packet from the weird asciified format that GDB uses 
        # and then unpack the values
        values = iter(self._reg_pkt_fmts[len(pkt)].unpack(bytes.fromhex(pkt.decode())))

        try:
            # Now save the results, if we run out of packets then just stop 
            # processing, it means the client didn't supply as many 
            for unpack_func, envi_idx in self._reg_pkt_unpack:
                self.emu.setRegister(envi_idx, unpack_func(values))

        except StopIteration:
            # If we've run out of values, just stop processing
            logger.debug('Stopped processing register packet @ envi reg %s',
                         self.emu.getRegisterName(envi_idx))

        return b'OK'

    def _handleWriteReg(self, cmd_data):
        """
        Handles client requests to write to one register.

        Args:
            cmd_data (str): The request packet.

        Returns:
            str: GDB status code
        """
        rpart, vpart = cmd_data.split(b'=')
        reg_idx = int(rpart, 16)
        reg_val = self._decodeGDBVal(vpart)
        self._serverWriteRegVal(reg_idx, reg_val)

        return b'OK'

    def _serverWriteRegVal(self, reg_idx, reg_val):
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
        Instructs the execution engine to read the values in all general registers.

        Args:
            None

        Returns:
            str: A GDB remote protocol register packet.
        """
        def _getvalues(num_regs):
            for i, (packfunc, envi_idx) in enumerate(self._reg_pkt_pack):
                if i == num_regs:
                    break
                for val in packfunc(self.emu.getRegister(envi_idx)):
                    yield val

        # First generate the binary data (use the default packet size)
        size, num_regs = self._reg_pkt_size
        data = self._reg_pkt_fmts[size].pack(*_getvalues(num_regs))

        # Now convert it to the weird asciified format that GDB uses
        return data.hex().encode()

    def _handleReadReg(self, cmd_data):
        """
        Instructs the execution engine to read the value of one register.

        Args:
            Register Index

        Returns:
            str: A GDB remote protocol register packet.
        """
        ridx = int(cmd_data, 16)
        reg_val, size = self._serverReadRegVal(ridx)
        reg_pkt = self._encodeGDBVal(reg_val, size)
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

    def _handleStepi(self, sig=signal.SIGTRAP):
        """
        Handles requests to single step (into).

        Args:
            None

        Returns:
            None
        """
        # After every step the current signal information should be provided (it 
        # will likely be SIGTRAP)
        sig = self._serverStepi(sig)
        res = b'S' + self._encodeGDBVal(sig)
        return res

    def _serverStepi(self, sig=signal.SIGTRAP):
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

    def _handleCont(self, sig=0):
        """
        Instructs the execution engine to continue execution at the current
        address.

        Args:
            None

        Returns:
            int: The reason for the next halt.
        """
        sig = self._serverCont(sig)
        res = b'S' + self._encodeGDBVal(sig)
        return res

    def _handleEndCont(self):
        '''
        We are no longer running.  Send the response to the client.
        '''
        res = b'S' + self._encodeGDBVal(self._halt_reason)
        return res

    def _serverCont(self, sig=0):
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

    def _handleBreak(self, sig=signal.SIGTRAP):
        """
        Sends a BREAK signal to the execution engine

        Args:
            None

        Returns:
            None
        """
        signal = self._serverBreak(sig)
        res = b'S' + self._encodeGDBVal(signal)
        return res

    def _serverBreak(self, sig=signal.SIGTRAP):
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
        #logger.debug("_handleQuery(%r)", cmd_data)
        res = self._serverQuery(cmd_data)
        #logger.debug("_handleQuery(%r) => %r", cmd_data, res)
        return res

    def _serverQuery(self, cmd_data):
        """
        Gathers information to respond to a client query.

        Args:
            cmd_data: The query type and context

        Returns:
            String response with appropriate data
        """
        #logger.warning("_serverQuery: %r", cmd_data)
        if cmd_data.startswith(b'Supported'):
            #logger.debug("QUERY: SUPPORTED STUFF!")
            #TODO: parse what the client asserts it supports and store
            return self._serverQSupported(cmd_data[10:])

        elif cmd_data == b'Symbol::':
            #logger.debug("QUERY: Symbol!")
            return self._serverQSymbol(None)

        elif cmd_data.startswith(b'Xfer'):
            #logger.debug("QUERY: Xfer!")
            return self._serverQXfer(cmd_data[5:])

        elif cmd_data == b'C':
            #logger.debug("QUERY: C!")
            return self._serverQC(None)

        elif cmd_data.startswith(b'L'):
            #logger.debug("QUERY: L!")
            if len(cmd_data) > 2:
                return self._serverQL(cmd_data[2:])
            else:
                return self._serverQL(None)

        elif cmd_data == b'TStatus':
            #logger.debug("QUERY: TStatus!")
            return self._serverQTStatus(None)

        elif cmd_data == b'fThreadInfo':
            #logger.debug("QUERY: fThreadInfo!")
            return self._serverQfThreadInfo(None)

        elif cmd_data.startswith(b'Attached'):
            #logger.debug("QUERY: Attached!")
            if len(cmd_data) > 9:
                return self._serverQAttached(cmd_data[10:])
            else:
                return self._serverQAttached(None)

        elif cmd_data.startswith(b'CRC'):
            #logger.debug("QUERY: CRC!")
            return self._serverQCRC(cmd_data[4:])

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
        #logger.debug("_handleQSetting(%r)", cmd_data)
        res = self._serverQSetting(cmd_data)
        #logger.debug("_handleQSetting(%r) => %r", cmd_data, res)
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

    def _serverGetThread(self, cmd_data=None):
        raise Exception('Server translation layer must implement this function')

    def _serverGetCore(self, cmd_data=None):
        raise Exception('Server translation layer must implement this function')

    def _serverQSymbol(self, cmd_data):
        raise Exception('Server translation layer must implement this function')

    def _serverQC(self, cmd_data):
        raise Exception('Server translation layer must implement this function')

    def _serverQL(self, cmd_data):
        raise Exception('Server translation layer must implement this function')

    def _serverQfThreadInfo(self, cmd_data):
        raise Exception('Server translation layer must implement this function')

    def _serverQAttached(self, cmd_data):
        raise Exception('Server translation layer must implement this function')

    def _serverQCRC(self, cmd_data):
        raise Exception('Server translation layer must implement this function')


class GdbBaseEmuServer(GdbServerStub):
    '''
    Emulated hardware debugger/gdb-stub for testing.
    '''
    def __init__(self, emu, port=47001, find_port=True, reggrps=None, haltregs=None):
        self.emu = emu

        big_endian = emu.getEndian()

        # _gdb_reg_fmt will be filled in by getTargetXml()
        GdbServerStub.__init__(self, emu.vw.arch.getArchName(), emu.psize,
                               big_endian, None, port, find_port)

        self._gdb_target_xml = None
        self._gdb_memory_map_xml = None
        self._gdb_reg_fmt = None

        # registers to send to the client automatically whenever a halt occurs
        if haltregs is None:
            self._haltregs = []
        else:
            self._haltregs = haltregs

        self.getTargetXml(reggrps)

        self.runthread = None
        self.connstate = STATE_CONN_DISCONNECTED
        self._halt_reason = SIGNAL_NONE

        self._symbol_iter = None
        self._thread_iter = None

        self.xfer_read_handlers = {
            b'exec-file': self.XferExecFile,
            b'features': {
                b'target.xml': self.XferFeaturesReadTargetXml,
            },
            b'memory-map': self.XferMemoryMap,
            b'threads': self.XferThreads,
        }

        self.vfile_handlers = {
            b'open':        self.vFileOpen,
            b'close':       self.vFileClose,
            b'pread':       self.vFileRead,
            b'setfs':       self.vFileSetFS,

            # Not supported - probably a bad idea to implement though
            b'pwrite':      None,
            b'fstat':       None,
            b'unlink':      None,
            b'readlink':    None,
        }

        # Create the attributes initialized by initProcessInfo()
        self.pid = 1
        self.tid = 1
        self.processes = []
        self.process_filenames = {}
        self.vfile_open_files = {}

        # Apparently GDB expects there to be a thread, so we define one
        self.threads = {
            1: [1],
        }

        self.initProcessInfo()

    def _updateEnviGdbIdxMap(self):
        self._gdb_to_envi_map = collections.OrderedDict()
        for reg_name, (reg_size, reg_idx) in self._gdb_reg_fmt.items():
            # For the GDB server stub we also need to save the envi index and 
            # register size mask
            envi_idx = self.emu.getRegisterIndex(reg_name)
            mask = e_bits.b_masks[reg_size]
            self._gdb_to_envi_map[reg_idx]  = (reg_name, reg_size, envi_idx, mask)

    def initProcessInfo(self):
        self.pid = 1
        self.tid = 1
        # we don't really imitate multiprocessing but this is the basic 
        # structure for it.
        self.processes = [1]

        # Get the filenames and path in use for our process (PID 1)
        self.process_filenames = {1: {}}
        for name in self.emu.vw.getFiles():
            filename = self.emu.vw.getFileMeta(name, 'OrigName')

            # Sanitize the filename so environment information isn't sent to the 
            # client
            key = os.path.split(filename)[1].encode()
            if key in self.process_filenames[1]:
                logger.warning('short filename %r already used in process filename map, not adding %r',
                               key, filename)
            else:
                self.process_filenames[1][key] = filename

        # used in vFile operations, set to the current PID
        self.vfile_pid = 1

        self.vfile_open_files = {
            # Add placeholders for the 3 standard FDs
            1: {0: None, 1: None, 2: None},
        }

    def getTargetXml(self, reggrps=None):
        '''
        Takes in a RegisterContext.
        Saves a XML file as described in the gdb-remote spec
        Also saves the tuple mapping GDB register indexes (which we're handing
        to the client) to RegisterContext-based indexes for each index.
        '''
        if reggrps is None:
            reggrps = [('general', 'org.gnu.gdb.i386.core')]

        # TODO: Support custom register index numbers?
        # TODO: handle custom types such as those used by vector registers

        # Save some register info from the emulator.
        regdefs, metas, pcindex, spindex, _ = self.emu.getRegisterInfo()

        # features defined in https://sourceware.org/gdb/current/onlinedocs/gdb/Standard-Target-Features.html#Standard-Target-Features
        #       PPC - https://sourceware.org/gdb/current/onlinedocs/gdb/PowerPC-Features.html
        #       x86 - https://sourceware.org/gdb/current/onlinedocs/gdb/i386-Features.html#i386-Features
        #       many other archs

        import xml.etree.ElementTree as ET

        # Build up the GdbStub._gdb_reg_fmt dynamically and should be good to 
        # use for that purpose
        #
        # In python 3.7 insertion order for the standard dict type is guaranteed 
        # to maintain insertion order, but to maintain backwards compatibility 
        # we explicitly use the OrderedDict type.
        self._gdb_reg_fmt = collections.OrderedDict()

        target = ET.Element('target')

        arch = ET.SubElement(target, 'architecture')
        arch.text = self._gdbarch

        archmod = self.emu.imem_archs[envi.ARCH_DEFAULT]

        if not reggrps:
            for rgps in archmod.archGetRegisterGroups():
                reggrps.append(rgps)

        # registers to send to the client automatically whenever a halt occurs
        haltregs = []

        # For servers the registers sent in the register packet should be just 
        # the first group of registers, so clear it now.
        self._reg_pkt_size = None

        # Track how many bytes (in asciified gdb format) the register 
        # information could take up
        size = 0

        for groups, feat_name in reggrps:
            # the xml element to populate
            feat = ET.SubElement(target, 'feature', {'name': feat_name})

            if not isinstance(groups, (list, tuple)):
                groups = [groups]

            for group in groups:
                reggrp = archmod.archGetRegisterGroup(group)

                for reg_name in reggrp:
                    # Some registers may be in multiple groups, if it has 
                    # already been added to the register format, it shouldn't be 
                    # added again.
                    if reg_name in self._gdb_reg_fmt:
                        continue

                    # The GDB register index is based on how many registers have 
                    # been added so far.
                    reg_idx = len(self._gdb_reg_fmt)
                    envi_idx = self.emu.getRegisterIndex(reg_name)
                    reg_size = self.emu.getRegisterWidth(envi_idx)

                    size += (reg_size // 8) * 2

                    self._gdb_reg_fmt[reg_name] = (reg_size, reg_idx)

                    # First entry in a feature must have a register number 
                    # defined, it's easiest just to add it to all of entries
                    elem = {
                        'bitsize':str(reg_size),
                        'name': reg_name,
                        'regnum': str(reg_idx),
                    }

                    if not self._haltregs and envi_idx in (pcindex, spindex):
                        # If haltregs have not yet been defined, use the PC and 
                        # SP defined in the architecture.
                        if envi_idx == pcindex:
                            elem['type'] = 'code_ptr'
                        elif envi_idx == spindex:
                            elem['type'] = 'data_ptr'

                        # Also add these to the "haltregs'
                        haltregs.append(reg_idx)

                    elif not self._haltregs and envi_idx in self._haltregs:
                        # Otherwise we make an assumption that the halt 
                        # registers are code pointers (if it is defined as the 
                        # PC), or a data pointer.
                        if envi_idx == pcindex:
                            elem['type'] = 'code_ptr'
                        else:
                            elem['type'] = 'data_ptr'

                    ET.SubElement(feat, 'reg', elem)

            # If the default register packet size has not yet been defined, 
            # define it now to be just the first register group.
            #
            # We have to keep the number of registers in the register packet to 
            # a reasonable size because GDB takes a while to parse large 
            # register packets.
            if self._reg_pkt_size is None:
                self._reg_pkt_size = (size, len(self._gdb_reg_fmt))

        out = b'<?xml version="1.0"?>\n'
        out += b'<!DOCTYPE target SYSTEM "gdb-target.dtd">\n'

        ET.indent(target, space='  ', level=0)
        out+= ET.tostring(target)
        self._gdb_target_xml = out


        # Only set the halt registers if they have not yet been set.
        if not self._haltregs:
            self._haltregs = haltregs

        # Statically gather the information necessary to efficiently pack and 
        # unpack register packets.
        self._genRegPktFmt()

        # Now that the gdb register format has been defined when the target XML 
        # was generated, update the index mappings
        self._updateEnviGdbIdxMap()

    def getMemoryMapXml(self):
        self._gdb_memory_map_xml = b'''<?xml version="1.0"?>
<!DOCTYPE memory-map
          PUBLIC "+//IDN gnu.org//DTD GDB Memory Map V1.0//EN"
                 "http://sourceware.org/gdb/gdb-memory-map.dtd">
<memory-map>
'''
        # Loop through each memory entry and add it
        for va, msize, perms, fname in self.emu.vw.getMemoryMaps():
            # For now consider every memory region to be RAM
            self._gdb_memory_map_xml += b'  <memory type="ram" start="%d" length="%d"/>\n'

        self._gdb_memory_map_xml += b'</memory-map>'

    def setPort(self, port):
        self._gdb_port = port

    # SERVER IMPLEMENTATION FUNCTIONS

    def _serverReadMem(self, addr, size):
        """
        Simulates a debugger reading memory.

        Args:
            addr (int): The memory address to read from.

            size (int): The size of the read.

        Returns:
            None
        """
        return self.emu.readMemory(addr, size)

    def _serverWriteMem(self, addr, val):
        """
        Simulates a debugger writing memory.

        Args:
            addr (int): The memory address to read from.

            val (int): The value to write:

        Returns:
            None
        """
        #logger.log(e_cmn.MIRE, '_serverWriteMem(0x%x, %r)', addr, val)

        with self.emu.getAdminRights():
            self.emu.writeMemory(addr, val)

        return b'OK'

    def _serverWriteRegVal(self, reg_idx, reg_val):
        """
        Simulates a debugger writing to a register.

        Args:
            reg_idx (int): The index of the register to write to.

            reg_val (int): The value to write to the register.

        Returns:
            None

        """
        try:
            envi_idx = self._gdb_to_envi_map[reg_idx][GDB_TO_ENVI_IDX]
        except IndexError:
            logger.warning("Attempted Bad Register Write: %d", reg_idx)
            return 0

        try:
            self.emu.setRegister(envi_idx, reg_val)
        except IndexError:
            logger.warning("Attempted Bad Register Write: %d -> %d", reg_idx, envi_idx)
            return 0


        return b'OK'

    def _serverReadRegVal(self, reg_idx):
        """
        Simulates a debugger reading from a register.

        Args:
            reg_idx (int): The index of the register to read from.

        Returns:
            None
        """
        try:
            _, size, envi_idx, mask = self._gdb_to_envi_map[reg_idx]
        except IndexError:
            logger.warning("Attempted Bad Register Read: %d", reg_idx)
            return 0, None

        try:
            # Sometimes the register format may specify a bit width that is 
            # smaller than the internal register size, ensure the value 
            # returned is the correct size
            return (self.emu.getRegister(envi_idx) & mask), size
        except IndexError:
            logger.warning("Attempted Bad Register Read: %d -> %d", reg_idx, envi_idx)
            return 0, None

    def _serverStepi(self, sig=signal.SIGTRAP):
        """
        Simulates a debugger single stepping (into).

        Args:
            None

        Returns:
            None
        """
        self.emu.stepi()

        # Return the trap signal
        self._halt_reason = sig
        return self._halt_reason

    def _serverDetach(self):
        """
        Simulates the receipt of a detach command.

        Args:
            None

        Returns:
            None
        """
        self.connstate = STATE_CONN_DISCONNECTED
        self._halt_reason = 0
        return b'OK'

    def _serverQXfer(self, cmd_data):
        fields = cmd_data.split(b":")
        logger.warning("qXfer fields:  %r", fields)
        if fields[1] == b'read':
            section = self.xfer_read_handlers.get(fields[0])
            if not section:
                logger.warning("qXfer no section:  %r", fields[0])
                return b'E00'

            if isinstance(section, dict):
                hdlr = section.get(fields[2])
                if not hdlr:
                    logger.warning("qXfer no handler:  %r", fields[2])
                    return b'E00'
            else:
                hdlr = section

            res = hdlr(fields)

            # Determine which chunk of the item being read is being retrieved
            offstr, szstr = fields[-1].split(b',')
            off = int(offstr, 16)
            sz = int(szstr, 16)

            logger.debug("_serverQXfer(%r) => %r", cmd_data, res[off:off+sz+1])
            if (off+sz+1) >= len(res):
                return b'l' + res[off:off+sz+1]
            return b'm' + res[off:off+sz+1]
        else:
            logger.warning("Unsupported action for query: %r", fields)
            return b'E00'

    def _serverVFile(self, cmd_data):
        res = b''
        cmd, cmd_params = cmd_data.split(b":", 1)
        params = cmd_params.split(b',')
        logger.warning('vFile command: %s(%s)', cmd, cmd_params)

        hdlr = self.vfile_handlers.get(cmd)
        if not hdlr:
            logger.warning("vFile no handler: %s", cmd)

            # Empty response indicates the command was not recognized
            return b''

        try:
            retcode, data = hdlr(params)
            if data:
                return b'F' + self._encodeGDBVal(addr) + b';' + data
            else:
                return b'F' + self._encodeGDBVal(addr)

        except OSError as e:
            logger.debug('vFile operation %s(%s) failed: %r', cmd, cmd_params, e)

            # Return the errno to the target
            return b'F-1,' + self._encodeGDBVal(e.errno)

    def vFileOpen(self, params):
        filename = unhexlify(params[0]).decode()

        # Ensure that the filename requested is the filename of the current 
        # process
        if filename not in self.process_filenames[self.vfile_pid]:
            raise FileNotFoundError(errno.ENOENT)

        # Get the FD for the new file
        fd = len(self.vfile_open_files[self.vfile_pid])

        os_filename = self.process_filenames[self.vfile_pid][filename]

        # Only change to r+b if you _want_ to enable writing to the original 
        # file, probably not what we really want to enable.
        #self.vfile_open_files[self.vfile_pid][fd] =  open(os_filename, 'r+b')

        self.vfile_open_files[self.vfile_pid][fd] =  open(os_filename, 'rb')

        return fd, None

    def vFileClose(self, params):
        fd = _decodeGDBVal(params[0])

        if fd not in self.vfile_open_files[self.vfile_pid]:
            raise OSError(errno.EBADF)

        self.vfile_open_files[self.vfile_pid][fd].close()
        del self.vfile_open_files[self.vfile_pid][fd]

        return 0, None

    def vFileRead(self, params):
        fd = _decodeGDBVal(params[0])
        count = _decodeGDBVal(params[1])
        offset = _decodeGDBVal(params[2])

        if fd not in self.vfile_open_files[self.vfile_pid]:
            raise OSError(errno.EBADF)

        self.vfile_open_files[self.vfile_pid][fd].seek(offset)
        data = self.vfile_open_files[self.vfile_pid][fd].read(count)

        return len(data), data

    def vFileSetFS(self, params):
        pid = _decodeGDBVal(params[0])

        if pid == 0:
            # Use the current running process
            self.vfile_pid = self.pid
            return 0
        elif pid in self.processes:
            self.vfile_pid = pid
            return 0
        else:
            return -1

    def _serverGetHaltSignal(self):
        """
        Returns the signal number responsible for the current halt.

        Args:
            None

        Returns:
            int: The signal number corresponding to the halt.
        """
        # Fallback server behavior

        # Return the halt reason (signal) and the state of the PC and SP 
        # registers
        reginfo = {}
        for reg_idx in self._haltregs:
            envi_idx = self._gdb_to_envi_map[reg_idx][GDB_TO_ENVI_IDX]
            mask = self._gdb_to_envi_map[reg_idx][GDB_TO_ENVI_MASK]
            reginfo[reg_idx] = self.emu.getRegister(envi_idx) & mask

        if reginfo:
            return self._halt_reason, reginfo
        else:
            return self._halt_reason

    def _serverQC(self, cmd_data):
        '''
        return Current Thread ID
        '''
        return b'QC%s' % self._serverGetThread()

    def _serverQL(self, cmd_data):
        '''
        return Current Thread ID
        '''
        return b'qM011000000010'

    def _serverQTStatus(self, cmd_data):
        '''
        return Current Thread Status
        '''
        return b'T0'

    def _serverQfThreadInfo(self, cmd_data):
        '''
        return Current Thread Status
        just tell them we're done...
        '''
        if self._thread_iter is None:
            self._thread_iter = iter(self.threads[self.pid])

        try:
            tid = next(self._thread_iter)
            return b'm' + self._serverGetThread(pid=self.pid, tid=tid)

        except StopIteration:
            self._thread_iter = None
            return b'l'

    def _serverQAttached(self, cmd_data):
        '''
        Returns an indication of how this process was created, if multiprocess
        extensions are enabled this query has a "pid" argument indicating the
        process that the info is being queried for.

        Return values:
            1:   The remote server attached to an existing process. 
            0:   The remote server created a new process.
            E??: Error was encountered
        '''
        return b'0'

    def XferFeaturesReadTargetXml(self, fields):
        return self._gdb_target_xml

    def XferExecFile(self, fields):
        pid = fields[2]

        if not pid:
            return self.process_filenames[self.pid]
        elif pid in self.process_filenames:
            return self.process_filenames[pid]
        else:
            logger.debug('qXfer param error: %r', fields)
            return b'E01'

    def _serverVFile(self, cmd_data):
        # Use the first file that was added to the workspace.
        filename = self.emu.vw.getFiles()[0]
        imagebase = self.emu.vw.getFileMeta(filename, 'imagebase')

        # Now return the bytes for this file
        _, img = self.emu.vw.getByteDef(imagebase)
        return img

    def XferMemoryMap(self, fields):
        if self._gdb_memory_map_xml is None:
            # Generate the memory map now, it probably wouldn't have been 
            # complete when the system was first initialized.
            self.getMemoryMapXml()

        return self._gdb_memory_map_xml

    def XferThreads(self, fields):
        # Generate the thread state XML
        res = bytearray(b'<threads>\n')
        for pid in self.processes:
            filename = self.process_filenames.get(pid, b'') 
            res += b'  <thread id="' + self._serverGetThread(pid=pid) + b'"' + \
                    b' core="' + self._serverGetCore() + b'"' + \
                    b' name="' + filename + b'"/>\n'
            #res += b'  <thread id="' + self._serverGetThread(pid=pid) + b'"' + \
            #        b' core="' + self._serverGetCore() + b'"'
            #if pid in self.process_filenames:
            #        b' name="' + self.process_filenames[pid] + b'"'
            #res += b'/>\n'
        res += b'</threads>\n'
        return res

    def _serverQSetting(self, cmd_data):
        if b':' in cmd_data:
            key, value = cmd_data.split(b':', 1)
            self._settings[key] = value
        else:
            self._settings[cmd_data] = True

        if cmd_data == b'StartNoAckMode':
            self._NoAckMode = self._getClientFeat(b'StartNoAckMode')

        return b'OK'

    def _serverGetThread(self, cmd_data=None, pid=None, tid=None):
        if pid is None:
            pid = self.pid
        if tid is None:
            tid = self.tid

        # The thread syntax is p<process ID>:<thread ID>
        return b'p' + self._encodeGDBVal(pid) + b'.' + self._encodeGDBVal(tid)

    def _serverGetCore(self, cmd_data=None):
        # Single core being emulated
        return b'1'

    def _serverSetThread(self, cmd_data):
        return b'OK'

    def _serverQSymbol(self, cmd_data):
        if self._symbol_iter is None:
            self._symbol_iter = iter(self.emu.vw.getNames())

        try:
            # All valid symbols should have the filename prefixed to the symbol 
            # name
            addr, name = next(self._symbol_iter)
            while '.' not in name:
                # Iterate until we reach the end of the list or we find another 
                # valid symbol name.
                addr, name = next(self._symbol_iter)

            _, sname = name.split('.', 1)
            return b'qSymbol:' + hexlify(sname.encode()) + b':' + self._encodeGDBVal(addr)

        except StopIteration:
            self._symbol_iter = None
            return b'OK'

    def _serverQCRC(self, cmd_data):
        data = self.emu.readMemory(addr, size)
        crc = binascii.crc32(data)
        return b'C' + self._encodeGDBVal(crc)

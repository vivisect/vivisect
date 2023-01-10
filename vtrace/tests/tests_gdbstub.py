import os
import time
import random
import shutil
import signal
import struct
import logging
import unittest
import itertools
import threading
import subprocess
from binascii import unhexlify

import envi.bits as e_bits

import vivisect.cli as vivcli
import vivisect.tests.helpers as vt_help
import vtrace.platforms.gdbstub as gdbstub
import vtrace.platforms.gdb_client as gdbclient
import vtrace.platforms.gdb_reg_fmts as gdb_reg_fmts


logger = logging.getLogger(__name__)
import envi.common as ecmn
ecmn.initLogging(logger, logging.DEBUG)


class TestEmuServer(gdbstub.GdbBaseEmuServer):
    """
    Represents a GDB server using the server stub code. Once Vivisect
    integration is complete, we shouldn't need this code.
    """

    def __init__(self, emu, port=47001, find_port=True):
        """
        Constructor for the TestSever class.

        Args:
            emu (Emulator): the Emulator this GDB Server uses for test

            Returns:
                None
        """
        gdbstub.GdbBaseEmuServer.__init__(self, emu, port, find_port=find_port)


class TestServer(gdbstub.GdbServerStub):
    """
    Represents a GDB server using the server stub code. Once Vivisect
    integration is complete, we shouldn't need this code.
    """

    def __init__(self, arch, addr_size, big_endian, reg, port):
        """
        Constructor for the TestSever class.

        Args:
            arch (str): The architecture of the debug target.

            addr_size (int): Pointer size of the debug target in bits.

            big_endian (bool): True if the debug target uses big-endian
            notation.

            reg (list): The list of regisers (and their sizes) made available
            for the debug target (see gdb_reg_fmts).

            port (int): The port that the server should listen on for GDB
            client connections.

            Returns:
                None
        """
        gdbstub.GdbServerStub.__init__(self, arch, addr_size, big_endian,
                reg, port)

        fmt32bit = e_bits.getFormat(4, big_endian)
        self.targetAddr = {0x1000: struct.pack(fmt32bit, 0xdeadbeef)}
        self.targetRegs = {
                'rax': 0xcafebabe,
                'rbx': 0xfeedface,
                'rip': 0x5000,
                }

    def _serverReadMem(self, addr, size):
        """
        Simulates a debugger reading memory.

        Args:
            addr (int): The memory address to read from.

            size (int): The size of the read.

        Returns:
            None
        """
        return self.targetAddr[addr]

    def _serverWriteMem(self, addr, val):
        """
        Simulates a debugger writing memory.

        Args:
            addr (int): The memory address to read from.

            val (int): The value to write:

        Returns:
            None
        """
        print('writing', hex(addr), val.hex())
        self.targetAddr[addr] = val
        return b'OK'

    def _serverWriteRegVal(self, reg_name, reg_val):
        """
        Simulates a debugger writing to a register.

        Args:
            reg_name (str): The name of the register to write to.

            reg_val (int): The value to write to the register.

        Returns:
            None
        """
        self.targetRegs[reg_name] = reg_val
        return b'OK'

    def _serverReadRegVal(self, reg_name):
        """
        Simulates a debugger reading from a register.

        Args:
            reg_name (str): The name of the register to read from.

        Returns:
            None
        """
        reg_val = 0x0
        if reg_name in self.targetRegs.keys():
            reg_val = self.targetRegs[reg_name]
        return reg_val

    def _serverStepi(self):
        """
        Simulates a debugger single stepping (into).

        Args:
            None

        Returns:
            None
        """
        cur_addr = self.targetRegs['rip']
        self.targetRegs['rip'] = cur_addr + 2
        return signal.SIGTRAP

    def _serverDetach(self):
        """
        Simulates the receipt of a detach command.

        Args:
            None

        Returns:
            None
        """
        return 'OK'

    def _serverQSymbol(self, cmd_data):
        # unhexlify the incoming command data
        sname = unhexlify(cmd_data)

    def _serverQCRC(self, cmd_data):
        raise Exception('Server translation layer must implement this function')

portadd = itertools.count()

class TestGdbServerStub(unittest.TestCase):
    """
    Unit tests for the gdb server stub code.
    """

    def __init__(self, methodName='runTest'):
        """
        Constructor for gdb server stub testing code.

        Args:
            methodName (str): name of the testing function.

        Returns:
            None
        """
        self.client = None
        self.server = None
        self.server_thread = None

        self.host = 'localhost'
        self.port = 1235
        self.arch = None
        self.psize = None
        self.addr_size = None
        self.bigend = None

        super(TestGdbServerStub, self).__init__(methodName=methodName)

    def setUp(self):
        """
        Creates a client and server for use by a unit test.

        Args:
            None

        Returns:
            None
        """
        self.port += next(portadd)
        logger.warning("\n\nTestGdbServerStub: setUp(): port %d" % self.port)

        # setup the emulator
        vw = vivcli.VivCli()
        test_binary = vt_help.getTestPath('linux/amd64/static64.llvm.elf')
        fname = vw.loadFromFile(test_binary)
        pc = vw.parseExpression(fname+'.__entry')

        emu = vw.getEmulator()
        emu.setProgramCounter(pc)
        self.arch = emu.vw.arch._arch_name
        self.psize = emu.getPointerSize()
        self.addr_size = self.psize * 8
        self.bigend = emu.getEndian()

        # Create a GDB client instance
        #self.client = gdbstub.GdbClientStub(self.arch, self.addr_size, self.bigend,
        #        gdb_reg_fmts.QEMU_X86_64_REG, self.host, self.port,
        #        'serverstub')

        self.client = gdbclient.GdbStubMixin(self.arch, self.host, self.port,
                                             'serverstub', self.psize, self.bigend)

        # Create a test server
        #self.server = TestServer(self.arch, self.addr_size, self.bigend,
        #        gdb_reg_fmts.QEMU_X86_64_REG, self.port)
        self.server = TestEmuServer(emu, port=self.port, find_port=False)

        # Start the server
        self.server_thread = threading.Thread(target=self.server.runServer, args=(True,), daemon=True)
        self.server_thread.start()

        time.sleep(1)

        # Attach the client
        self.client.gdbAttach()

    def tearDown(self):
        """
        Destroys the client and server after a test is complete.

        Args:
            None

        Returns:
            None
        """
        logger.warning("\n\nTestGdbServerStub: tearDown()")
        self.client.gdbDetach()
        self.server_thread.join()
        self.client = None  # server teardown
        time.sleep(1)
        self.server_thread = None

    def test_GetRegisterVal(self):
        """
        Tests the server's handling of register read requests.

        Args:
            None

        Returns:
            None
        """
        registers = self.client.gdbGetRegisters()
        # TODO: We should probably check all registers in the future
        reg_name = 'rax'
        actual = self.server.emu.getRegisterByName(reg_name)
        expected = registers[reg_name]
        self.assertEqual(expected, actual)

    def test_SetRegisterVal(self):
        """
        Tests the server's handling of register write requests.

        Args:
            None

        Returns:
            None
        """
        self.server.emu.setRegisterByName('rbx', 0x47145)
        updates = {
                'rax': 123456,
                'rbx': 8675309,
                }

        self.client.gdbSetRegisters(updates)
        for reg_name in updates.keys():
            expected = updates[reg_name]
            actual = self.server.emu.getRegisterByName(reg_name)
            self.assertEqual(expected, actual)

    def test_ReadMemory(self):
        """
        Tests the server's handling of memory read operations.

        Args:
            None

        Returns:
            None
        """
        for addr, name in self.server.emu.vw.getNames()[:20]:
            expected = self.client.gdbReadMem(addr, 4)
            actual = self.server.emu.readMemory(addr, 4)
            self.assertEqual(expected, actual)

    def test_WriteMemory(self):
        """
        Tests the server's handling of memory write operations.

        Args:
            None

        Returns:
            None
        """
        for addr, name in self.server.emu.vw.getNames()[:20]:
            if not self.server.emu.vw.isValidPointer(addr):
                continue

            # create the bytes we're writing
            fmt32bit = e_bits.getFormat(4, self.bigend)
            expected = struct.pack(fmt32bit, 0xdeadface)

            # do the writing through GDB
            self.client.gdbWriteMem(addr, expected)
            # read it back directly from the Emulator
            actual = self.server.emu.readMemory(addr, 4)
            # Do the test
            self.assertEqual(expected, actual)

    def test_Stepi(self):
        """
        Tests the server's handling of single step (into) operations.

        Args:
            None

        Returns:
            None
        """
        startpc = self.server.emu.getProgramCounter()
        op = self.server.emu.parseOpcode(startpc)

        self.client.gdbStepi()

        expected = startpc + len(op)
        actual = self.server.emu.getProgramCounter()
        self.assertEqual(expected, actual)


class TestGdbClientStub(unittest.TestCase):
    """
    Unit tests for the gdb client stub code.
    """

    def __init__(self, methodName='runTest'):
        """
        Constructor for gdb client stub testing code.

        Args:
            methodName (str): Name of the main testing function.

        Returns:
            None
        """
        self.client = None
        self.server_proc = None
        self.server = None
        self.host = 'localhost'
        self.port = 1234
        # This should be guarenteed to be on the host
        # FIXME: this assumes amd64/Linux
        self.test_binary = vt_help.getTestPath('linux/amd64/static64.llvm.elf')
        self.bigend = False

        super(TestGdbClientStub, self).__init__(methodName=methodName)
        '''
        static64.__libc_start_main():
          0x00401040:  push r14
          0x00401042:  push r13
          0x00401044:  xor eax,eax
          0x00401046:  push r12
          0x00401048:  push rbp
          0x00401049:  mov r12,r8
        vdb > reg
                  cs:0x00000033 (51)                             ss:0x0000002b (43)
               ctrl0:0x00000000 (0)                             st0:0x00000000 (0)
               ctrl1:0x00000000 (0)                             st1:0x00000000 (0)
              ctrl10:0x00000000 (0)                             st2:0x00000000 (0)
              ctrl11:0x00000000 (0)                             st3:0x00000000 (0)
              ctrl12:0x00000000 (0)                             st4:0x00000000 (0)
              ctrl13:0x00000000 (0)                             st5:0x00000000 (0)
              ctrl14:0x00000000 (0)                             st6:0x00000000 (0)
              ctrl15:0x00000000 (0)                             st7:0x00000000 (0)
               ctrl2:0x00000000 (0)                           test0:0x00000000 (0)
               ctrl3:0x00000000 (0)                           test1:0x00000000 (0)
               ctrl4:0x00000000 (0)                           test2:0x00000000 (0)
               ctrl5:0x00000000 (0)                           test3:0x00000000 (0)
               ctrl6:0x00000000 (0)                           test4:0x00000000 (0)
               ctrl7:0x00000000 (0)                           test5:0x00000000 (0)
               ctrl8:0x00000000 (0)                           test6:0x00000000 (0)
               ctrl9:0x00000000 (0)                           test7:0x00000000 (0)
              debug0:0x00000000 (0)                            ymm0:0x00000000 (0)
              debug1:0x00000000 (0)                            ymm1:0x00000000 (0)
             debug10:0x00000000 (0)                           ymm10:0x00000000 (0)
             debug11:0x00000000 (0)                           ymm11:0x00000000 (0)
             debug12:0x00000000 (0)                           ymm12:0x00000000 (0)
             debug13:0x00000000 (0)                           ymm13:0x00000000 (0)
             debug14:0x00000000 (0)                           ymm14:0x00000000 (0)
             debug15:0x00000000 (0)                           ymm15:0x00000000 (0)
              debug2:0x00000000 (0)                            ymm2:0x00000000 (0)
              debug3:0x00000000 (0)                            ymm3:0x00000000 (0)
              debug4:0x00000000 (0)                            ymm4:0x00000000 (0)
              debug5:0x00000000 (0)                            ymm5:0x00000000 (0)
              debug6:0xffff4ff0 (4294922224)                   ymm6:0x00000000 (0)
              debug7:0x00000000 (0)                            ymm7:0x00000000 (0)
              debug8:0x00000000 (0)                            ymm8:0x00000000 (0)
              debug9:0x00000000 (0)                            ymm9:0x00000000 (0)
                  ds:0x00000000 (0)
              eflags:0x00000246 (582)
                  es:0x00000000 (0)
                fpcr:0x00000000 (0)
                fpsr:0x00000000 (0)
                  fs:0x00000000 (0)
                  gs:0x00000000 (0)
                 r10:0x00000000 (0)
                 r11:0x00000000 (0)
                 r12:0x00401b40 (4201280)
                 r13:0x00000000 (0)
                 r14:0x00000000 (0)
                 r15:0x00000000 (0)
                  r8:0x00401b40 (4201280)
                  r9:0x00000000 (0)
                 rax:0x00000000 (0)
                 rbp:0x00000000 (0)
                 rbx:0x00000000 (0)
                 rcx:0x00401aa0 (4201120)
                 rdi:0x00400b60 (4197216)
                 rdx:0x7fffe610a858 (140737053239384)
                 rip:0x0040104c (4198476)
                 rsi:0x00000001 (1)
                 rsp:0x7fffe610a818 (140737053239320)


        but GDB against a QEMU target differs:
            0x0000000000400a40 in ?? ()
            (gdb) i r
            rax            0x0                 0
            rbx            0x0                 0
            rcx            0x0                 0
            rdx            0x0                 0
            rsi            0x0                 0
            rdi            0x0                 0
            rbp            0x0                 0x0
            rsp            0x40007ff7f0        0x40007ff7f0
            r8             0x0                 0
            r9             0x0                 0
            r10            0x0                 0
            r11            0x0                 0
            r12            0x0                 0
            r13            0x0                 0
            r14            0x0                 0
            r15            0x0                 0
            rip            0x400a40            0x400a40
            eflags         0x202               [ IOPL=0 IF ]
            cs             0x33                51
            ss             0x2b                43
            ds             0x0                 0
            es             0x0                 0
            fs             0x0                 0
            gs             0x0                 0
            fs_base        0x0                 0
            gs_base        0x0                 0
            k_gs_base      0x0                 0
            cr0            0x80010001          [ PG WP PE ]
            cr2            0x0                 0
            cr3            0x0                 [ PDBR=0 PCID=0 ]
            cr4            0x220               [ OSFXSR PAE ]
            cr8            0x0                 0
            efer           0x500               [ LMA LME ]
            xmm0           {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm1           {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm2           {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm3           {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm4           {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm5           {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm6           {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm7           {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm8           {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm9           {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm10          {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm11          {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm12          {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm13          {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm14          {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            xmm15          {v4_float = {0x0, 0x0, 0x0, 0x0}, v2_double = {0x0, 0x0}, v16_int8 = {0x0 <repeats 16 times>}, v8_int16 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, v4_int32 = {0x0, 0x0, 0x0, 0x0}, v2_int64 = {0x0, 0x0}, uint128 = 0x0}
            mxcsr          0x1f80              [ IM DM ZM OM UM PM ]
            (gdb)
        '''

    def setUp(self):
        """
        Starts the gdb server or qemu instance (which exposes the GDB server)
        and creates a GDB stub client instance.

        Args:
            None

        Returns:
            None
        """
        logger.info("\n\nTestGdbClientStub: setUp()")
        # Start the GDB server
        port = self.port + next(portadd)

        gdbserver_path = shutil.which('gdbserver')
        qemu_path = shutil.which('qemu-x86_64-static')
        if qemu_path is not None:
            servertype = 'qemu'
            args = [qemu_path, '-g', str(port), self.test_binary]
        elif gdbserver_path is not None:
            servertype = 'gdbserver'
            args = [gdbserver_path, ':%d' % port, self.test_binary]
        else:
            raise Exception("Unable to run GDB tests, install 'qemu-user-staic'")

        logger.info('starting server: %s', ' '.join(args))
        self.server_proc = subprocess.Popen(args)
        logger.info('server available on port %d', port)

        time.sleep(1)

        # Create a GDB client instance
        #self.client = gdbstub.GdbClientStub('amd64', 64, False, None, self.host, port, servertype)
        self.client = gdbclient.GdbStubMixin('amd64', 'localhost', port, servertype, 64, False)

        # Attach the client
        self.client.gdbAttach()
        self.client._gdbJustAttached()

    def tearDown(self):
        """
        Tears down the client and server after a test is complete.

        Args:
            None

        Returns:
            None
        """
        logger.info("\n\nTestGdbClientStub: tearDown()")
        self.client.gdbDetach()
        time.sleep(1)
        # Kill the gdb server process
        self.server_proc.kill()
        time.sleep(1)

        self.server_proc = None
        self.client = None  # Client teardown

    def test_GetRegisterVal(self):
        """
        Tests the client's handling of register read requests.

        Args:
            None

        Returns:
            None
        """
        registers = self.client.gdbGetRegisters()
        logger.info(registers)
        # TODO: We should probably check all registers in the future
        self.assertEqual(registers['rip'], 0x400a40)
        self.assertEqual(registers['fctrl'], 0x37f)

        # The stack value depends on if this is qemu or gdbserver. The memory 
        # maps allocated to the server subprocess do change from those allocated 
        # by the normal qemu and gdbserver processes if they had been started 
        # directly from the shell.
        if self.client._gdb_servertype == 'qemu':
            # From shell it would be: 0x40007ffbe0
            # From a subprocess spawned by python this is: 0x40007ffaa0
            self.assertEqual(registers['rsp'], 0x40007ffaa0)

            # CR0 registers only available over QEMU
            self.assertEqual(registers['cr0'], 0x80010001)
        else:
            # From shell it would be: 0x7fffffffdbb0
            # From a subprocess spawned by python this is: 0x7fffffffda60
            self.assertEqual(registers['rsp'], 0x7fffffffda60)

        self.assertEqual(registers['xmm15'], 0x0)
        self.assertEqual(registers['mxcsr'], 0x1f80)

    def test_SetRegisterVal(self):
        """
        Tests the client's handling of register write requests.

        Args:
            None

        Returns:
            None
        """
        test_count = random.randint(1, 10)
        picked = 0
        choices = []
        updates = {}

        while picked < test_count:
            # Chose some random registers to write to
            # TODO: QEMU has some strange behaviors when writing to certain
            # registers (segfaults on code segment registers, ignoring others,
            # etc...). Only test r* and x* registers for now.
            reg = random.choice(self.client._gdb_reg_fmt)
            # NOTE: For QEMU targets vector (XMM, YMM) register reads and writes
            # are messed up, not testing the XMM/YMM registers for now
            #if (reg[0][0] == 'r') or ('xmm' in reg[0]):
            if reg[0][0] == 'r':
                choices.append(reg)
                picked += 1

        # Gen a random value for each register based on the size of the
        # register
        for r in choices:
            reg_name = r[0]
            reg_size = r[1]
            reg_val = random.randint(0, 2 ** reg_size - 1)
            updates[reg_name] = reg_val

        self.client.gdbSetRegisters(updates)
        registers = self.client.gdbGetRegisters()

        for reg_name in updates.keys():
            self.assertEqual(registers[reg_name], updates[reg_name], msg=reg_name)

    def test_WriteMemory(self):
        """
        Tests the client's handling of memory write requests.

        Args:
            None

        Returns:
            None
        """
        addr = 0x40007ffff0
        test_count = random.randint(1, 10)

        while test_count > 0:
            # Gen a random number of bytes to write
            write_size = random.randint(1, 8) # in bytes

            # Gen a random val to write that fits in the write size
            expected = os.getrandom(write_size)

            self.client.gdbWriteMem(addr, expected)
            actual = self.client.gdbReadMem(addr, write_size)
            self.assertEqual(expected, actual)
            test_count -= 1

    def test_ReadMemory(self):
        """
        Tests the client's handling of memory read requests.

        Args:
            None

        Returns:
            None
        """
        fmt32bit = e_bits.getFormat(4, self.bigend)
        expected = struct.pack(fmt32bit, 0x8949ed31)
        actual = self.client.gdbReadMem(0x400a40, 4)
        self.assertEqual(expected, actual)

    def test_Stepi(self):
        """
        Tests the client's handling of single step (into) requests.

        Args:
            None

        Returns:
            None
        """
        start = 0x400a40
        expected_end = 0x400a42

        registers = self.client.gdbGetRegisters()
        self.assertEqual(registers['rip'], start)

        self.client.gdbStepi()
        registers = self.client.gdbGetRegisters()
        self.assertEqual(registers['rip'], expected_end)

    def test_BreakandContinue(self):
        """
        Tests the client's handling of setting breakpoints and continuing
        execution.

        Args:
            None

        Returns:
            None
        """
        break_addr = 0x400a4e
        self.client.gdbSetSWBreakpoint(break_addr)
        self.client.gdbContinue()
        registers = self.client.gdbGetRegisters()

        expected = break_addr
        actual = registers['rip']

        self.assertEqual(expected, actual)

    def test_RemoveBreak(self):
        """
        Tests the client's handling of setting and removing breakpoints.

        Args:
            None

        Returns:
            None
        """
        break_addr1 = 0x400a4e
        break_addr2 = 0x40104c

        self.client.gdbSetSWBreakpoint(break_addr1)
        self.client.gdbSetSWBreakpoint(break_addr2)
        self.client.gdbRemoveSWBreakpoint(break_addr1)

        self.client.gdbContinue()
        registers = self.client.gdbGetRegisters()

        expected = break_addr2
        actual = registers['rip']
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()

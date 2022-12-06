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

import envi.bits as e_bits


import vivisect.tests.helpers as vt_help
import vtrace.platforms.gdbstub as gdbstub
import vtrace.platforms.gdb_reg_fmts as gdb_reg_fmts


logger = logging.getLogger(__name__)


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
        self.targetAddr[addr] = val

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
        self.arch = 'amd64'
        self.addr_size = 64 # bits
        self.bigend = False # little-endian

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

        # Create a GDB client instance
        self.client = gdbstub.GdbClientStub(self.arch, self.addr_size, self.bigend,
                gdb_reg_fmts.QEMU_X86_64_REG, self.host, self.port,
                'serverstub')

        # Create a test server
        self.server = TestServer(self.arch, self.addr_size, self.bigend,
                gdb_reg_fmts.QEMU_X86_64_REG, self.port)

        # Start the server
        self.server_thread = threading.Thread(target=self.server.runServer)
        self.server_thread.daemon = True
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
        actual = self.server.targetRegs[reg_name]
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
        updates = {
                'rax': 123456,
                'rbx': 8675309,
                }

        self.client.gdbSetRegisters(updates)
        for reg_name in updates.keys():
            expected = updates[reg_name]
            actual = self.server.targetRegs[reg_name]
            self.assertEqual(expected, actual)

    def test_ReadMemory(self):
        """
        Tests the server's handling of memory read operations.

        Args:
            None

        Returns:
            None
        """
        addr = 0x1000
        expected = self.client.gdbReadMem(addr, 4)
        actual = self.server.targetAddr[addr]
        self.assertEqual(expected, actual)

    def test_WriteMemory(self):
        """
        Tests the server's handling of memory write operations.

        Args:
            None

        Returns:
            None
        """
        addr = 0x1000
        fmt32bit = e_bits.getFormat(4, self.bigend)
        expected = struct.pack(fmt32bit, 0xdeadface)
        self.client.gdbWriteMem(addr, expected)
        actual = self.server.targetAddr[addr]
        self.assertEqual(expected, actual)

    def test_Stepi(self):
        """
        Tests the server's handling of single step (into) operations.

        Args:
            None

        Returns:
            None
        """
        self.client.gdbStepi()
        expected = 0x5002
        actual = self.server.targetRegs['rip']
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

    def setUp(self):
        """
        Starts the gdb server or qemu instance (which exposes the GDB server)
        and creates a GDB stub client instance.

        Args:
            None

        Returns:
            None
        """
        logger.debug("\n\nTestGdbClientStub: setUp()")
        # Start the GDB server
        port = self.port + next(portadd)

        qemu_path = shutil.which('qemu-x86_64-static')
        if qemu_path is not None:
            servertype = 'qemu'
            args = [qemu_path, '-g', str(port), self.test_binary]
        else:
            raise Exception("Unable to run GDB tests, install 'qemu-user-staic'")

        logger.debug('starting server: %s', ' '.join(args))
        self.server_proc = subprocess.Popen(args)
        logger.debug('server available on port %d', port)

        time.sleep(1)

        # Create a GDB client instance
        self.client = gdbstub.GdbClientStub('amd64', 64, False, None, self.host, port, servertype)

        # Attach the client
        self.client.gdbAttach()

    def tearDown(self):
        """
        Tears down the client and server after a test is complete.

        Args:
            None

        Returns:
            None
        """
        logger.debug("\n\nTestGdbClientStub: tearDown()")
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
        logger.debug(registers)
        # TODO: We should probably check all registers in the future
        self.assertEqual(registers['rip'], 0x400a40)
        self.assertEqual(registers['fctrl'], 0x37f)

        if self.client._gdb_servertype == 'qemu':
            # CR0 registers only available over QEMU
            self.assertEqual(registers['cr0'], 0x80010001)

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
            expected = b''.join([b'%c' % random.randint(0, 256) for x in range (write_size)])

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

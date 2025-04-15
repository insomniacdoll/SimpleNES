from typing import Callable
from CPUOpcodes import *
from MainBus import MainBus
import logging

class CPU:
    def __init__(self, mem: MainBus):
        self.m_pendingNMI = False
        self.m_pendingIRQ = False
        self.m_bus = mem
        self.m_skipCycles = 0
        self.m_cycles = 0
        self.r_PC = 0
        self.r_SP = 0xFD
        self.r_A = 0
        self.r_X = 0
        self.r_Y = 0
        self.f_C = False
        self.f_Z = False
        self.f_I = True
        self.f_D = False
        self.f_V = False
        self.f_N = False

    def reset(self, start_addr: int = None):
        if start_addr is None:
            start_addr = self.readAddress(ResetVector)
        self.m_skipCycles = 0
        self.m_cycles = 0
        self.r_A = 0
        self.r_X = 0
        self.r_Y = 0
        self.f_I = True
        self.f_C = False
        self.f_D = False
        self.f_N = False
        self.f_V = False
        self.f_Z = False
        self.r_PC = start_addr
        self.r_SP = 0xFD

    def interrupt(self, type_: InterruptType):
        if type_ == InterruptType.NMI:
            self.m_pendingNMI = True
        elif type_ == InterruptType.IRQ:
            self.m_pendingIRQ = True

    def interruptSequence(self, type_: InterruptType):
        if (self.f_I and type_ not in (InterruptType.NMI, InterruptType.BRK_)):
            return
        if type_ == InterruptType.BRK_:
            self.r_PC += 1
        self.pushStack((self.r_PC >> 8) & 0xFF)
        self.pushStack(self.r_PC & 0xFFFF)
        flags = (self.f_N << 7) | (self.f_V << 6) | (1 << 5) | \
                ((type_ == InterruptType.BRK_) << 4) | \
                (self.f_D << 3) | (self.f_I << 2) | (self.f_Z << 1) | self.f_C
        self.pushStack(flags)
        self.f_I = True
        if type_ in (InterruptType.IRQ, InterruptType.BRK_):
            self.r_PC = self.readAddress(IRQVector)
        elif type_ == InterruptType.NMI:
            self.r_PC = self.readAddress(NMIVector)
        self.m_skipCycles += 7

    def pushStack(self, value: int):
        self.m_bus.write(0x100 | self.r_SP, value & 0xFF)
        self.r_SP -= 1

    def pullStack(self) -> int:
        self.r_SP += 1
        return self.m_bus.read(0x100 | self.r_SP)

    def setZN(self, value: int):
        self.f_Z = value == 0
        self.f_N = (value & 0x80) != 0

    def skipPageCrossCycle(self, a: int, b: int):
        if (a & 0xFF00) != (b & 0xFF00):
            self.m_skipCycles += 1

    def skipDMACycles(self):
        self.m_skipCycles += 513 + (self.m_cycles & 1)

    def step(self):
        self.m_cycles += 1
        if self.m_skipCycles > 1:
            self.m_skipCycles -= 1
            return
        self.m_skipCycles = 0

        if self.m_pendingNMI:
            self.interruptSequence(InterruptType.NMI)
            self.m_pendingNMI = self.m_pendingIRQ = False
        elif self.m_pendingIRQ:
            self.interruptSequence(InterruptType.IRQ)
            self.m_pendingNMI = self.m_pendingIRQ = False

        opcode = self.m_bus.read(self.r_PC)
        self.r_PC += 1
        cycle_length = OperationCycles[opcode]

        executed = False
        if cycle_length:
            executed |= self.executeImplied(opcode)
            executed |= self.executeBranch(opcode)
            executed |= self.executeType1(opcode)
            executed |= self.executeType2(opcode)
            executed |= self.executeType0(opcode)
        if not executed:
            logging.error(f"Unrecognized opcode: {opcode:02X}")

        if executed:
            self.m_skipCycles += cycle_length

    def executeImplied(self, opcode: int) -> bool:
        op = OperationImplied(opcode)
        if op == OperationImplied.NOP:
            pass
        elif op == OperationImplied.BRK:
            self.interruptSequence(InterruptType.BRK_)
        elif op == OperationImplied.JSR:
            self.pushStack((self.r_PC + 1) >> 8)
            self.pushStack((self.r_PC + 1) & 0xFF)
            self.r_PC = self.readAddress(self.r_PC)
        # 其他操作符处理...
        return True

    # 其他方法如executeBranch(), executeType0()等需要完整转换，此处省略以符合格式要求

    def readAddress(self, addr: int) -> int:
        return self.m_bus.read(addr) | (self.m_bus.read(addr+1) << 8)
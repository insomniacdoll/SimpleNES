from enum import Enum
from typing import Callable
from Mapper import Mapper

class IORegisters(Enum):
    PPUCTRL = 0x2000
    PPUMASK = 0x2001
    PPUSTATUS = 0x2002
    OAMADDR = 0x2003
    OAMDATA = 0x2004
    PPUSCROL = 0x2005
    PPUADDR = 0x2006
    PPUDATA = 0x2007
    OAMDMA = 0x4014
    JOY1 = 0x4016
    JOY2 = 0x4017

class MainBus:
    def __init__(self):
        self.m_RAM = bytearray(0x800)  # 2KB RAM
        self.m_extRAM = bytearray()    # 扩展RAM初始为空
        self.m_mapper = None
        self.m_writeCallbacks = {}
        self.m_readCallbacks = {}

    def read(self, addr: int) -> int:
        if addr < 0x2000:
            return self.m_RAM[addr & 0x7ff]
        elif 0x2000 <= addr < 0x4020:
            # 计算对应寄存器
            reg_val = addr & 0x2007 if addr < 0x4000 else addr
            reg = IORegisters(reg_val)
            if reg in self.m_readCallbacks:
                return self.m_readCallbacks[reg]()
            else:
                print(f"Warning: No read callback for {hex(addr)}")
                return 0
        elif 0x4020 <= addr < 0x6000:
            print(f"Warning: Expansion ROM read at {hex(addr)} unsupported")
            return 0
        elif 0x6000 <= addr < 0x8000:
            if self.m_mapper and self.m_mapper.hasExtendedRAM():
                return self.m_extRAM[addr - 0x6000]
            else:
                return 0
        else:
            if self.m_mapper:
                return self.m_mapper.readPRG(addr)
            else:
                return 0

    def write(self, addr: int, value: int):
        if addr < 0x2000:
            self.m_RAM[addr & 0x7ff] = value
        elif 0x2000 <= addr < 0x4020:
            reg_val = addr & 0x2007 if addr < 0x4000 else addr
            reg = IORegisters(reg_val)
            if reg in self.m_writeCallbacks:
                self.m_writeCallbacks[reg](value)
            else:
                print(f"Warning: No write callback for {hex(addr)}")
        elif 0x4020 <= addr < 0x6000:
            print("Warning: Expansion ROM write unsupported")
        elif 0x6000 <= addr < 0x8000:
            if self.m_mapper and self.m_mapper.hasExtendedRAM():
                self.m_extRAM[addr - 0x6000] = value
        else:
            if self.m_mapper:
                self.m_mapper.writePRG(addr, value)
            else:
                print("Error: Mapper not set")

    def setMapper(self, mapper: Mapper) -> bool:
        if not mapper:
            print("Error: Mapper is None")
            return False
        self.m_mapper = mapper
        if self.m_mapper.hasExtendedRAM():
            self.m_extRAM = bytearray(0x2000)  # 分配8KB扩展RAM
        else:
            self.m_extRAM = bytearray()
        return True

    def setWriteCallback(self, reg: IORegisters, callback: Callable[[int], None]) -> bool:
        if not callable(callback):
            print("Error: Callback is not callable")
            return False
        self.m_writeCallbacks[reg] = callback
        return True

    def setReadCallback(self, reg: IORegisters, callback: Callable[[], int]) -> bool:
        if not callable(callback):
            print("Error: Callback is not callable")
            return False
        self.m_readCallbacks[reg] = callback
        return True
from enum import Enum

class BranchOnFlag(Enum):
    Negative = 0
    Overflow = 1
    Carry = 2
    Zero = 3

class Operation1(Enum):
    ORA = 0
    AND = 1
    EOR = 2
    ADC = 3
    STA = 4
    LDA = 5
    CMP = 6
    SBC = 7

class AddrMode1(Enum):
    IndexedIndirectX = 0
    ZeroPage = 1
    Immediate = 2
    Absolute = 3
    IndirectY = 4
    IndexedX = 5
    AbsoluteY = 6
    AbsoluteX = 7

class Operation2(Enum):
    ASL = 0
    ROL = 1
    LSR = 2
    ROR = 3
    STX = 4
    LDX = 5
    DEC = 6
    INC = 7

class AddrMode2(Enum):
    Immediate_ = 0
    ZeroPage_ = 1
    Accumulator = 2
    Absolute_ = 3
    Indexed = 5
    AbsoluteIndexed = 7

class Operation0(Enum):
    BIT = 1
    STY = 4
    LDY = 5
    CPY = 6
    CPX = 7

class OperationImplied(Enum):
    NOP = 0xEA
    BRK = 0x00
    JSR = 0x20
    RTI = 0x40
    RTS = 0x60
    JMP = 0x4C
    JMPI = 0x6C
    PHP = 0x08
    PLP = 0x28
    PHA = 0x48
    PLA = 0x68
    DEY = 0x88
    DEX = 0xCA
    TAY = 0xA8
    INY = 0xC8
    INX = 0xE8
    CLC = 0x18
    SEC = 0x38
    CLI = 0x58
    SEI = 0x78
    TYA = 0x98
    CLV = 0xB8
    CLD = 0xD8
    SED = 0xF8
    TXA = 0x8A
    TXS = 0x9A
    TAX = 0xAA
    TSX = 0xBA

class InterruptType(Enum):
    IRQ = 0
    NMI = 1
    BRK_ = 2

# 0 implies unused opcode
OperationCycles = [
    7, 6, 0, 0, 0, 3, 5, 0, 3, 2, 2, 0, 0, 4, 6, 0,
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,
    6, 6, 0, 0, 3, 3, 5, 0, 4, 2, 2, 0, 4, 4, 6, 0,
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,
    6, 6, 0, 0, 0, 3, 5, 0, 3, 2, 2, 0, 3, 4, 6, 0,
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,
    6, 6, 0, 0, 0, 3, 5, 0, 4, 2, 2, 0, 5, 4, 6, 0,
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,
    0, 6, 0, 0, 3, 3, 3, 0, 2, 0, 2, 0, 4, 4, 4, 0,
    2, 6, 0, 0, 4, 4, 4, 0, 2, 5, 2, 0, 0, 5, 0, 0,
    2, 6, 2, 0, 3, 3, 3, 0, 2, 2, 2, 0, 4, 4, 4, 0,
    2, 5, 0, 0, 4, 4, 4, 0, 2, 4, 2, 0, 4, 4, 4, 0,
    2, 6, 0, 0, 3, 3, 5, 0, 2, 2, 2, 0, 4, 4, 6, 0,
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,
    2, 6, 0, 0, 3, 3, 5, 0, 2, 2, 2, 2, 4, 4, 6, 0,
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,
]

InstructionModeMask = 0x3

OperationMask = 0xe0
OperationShift = 5

AddrModeMask = 0x1c
AddrModeShift = 2

BranchInstructionMask = 0x1f
BranchInstructionMaskResult = 0x10
BranchConditionMask = 0x20
BranchOnFlagShift = 6

NMIVector = 0xfffa
ResetVector = 0xfffc
IRQVector = 0xfffe

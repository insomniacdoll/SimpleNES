from abc import ABC, abstractmethod
from enum import Enum
import logging

class NameTableMirroring(Enum):
    Horizontal = 0
    Vertical = 1
    FourScreen = 8
    OneScreenLower = 9
    OneScreenHigher = 10

class MapperType(Enum):
    NROM = 0
    SxROM = 1
    UxROM = 2
    CNROM = 3
    MMC3 = 4
    AxROM = 7
    ColorDreams = 11
    GxROM = 66

class Mapper(ABC):
    def __init__(self, cartridge, mapper_type):
        self.cartridge = cartridge
        self.mapper_type = mapper_type

    @abstractmethod
    def writePRG(self, addr, value):
        pass

    @abstractmethod
    def readPRG(self, addr):
        pass

    @abstractmethod
    def readCHR(self, addr):
        pass

    @abstractmethod
    def writeCHR(self, addr, value):
        pass

    def getNameTableMirroring(self):
        return NameTableMirroring(self.cartridge.getNameTableMirroring())

    def hasExtendedRAM(self):
        return self.cartridge.hasExtendedRAM()

    def scanlineIRQ(self):
        pass

    @staticmethod
    def createMapper(mapper_t, cartridge, interrupt_cb, mirroring_cb):
        mapper_dict = {
            MapperType.NROM: MapperNROM,
            MapperType.SxROM: MapperSxROM,
            MapperType.UxROM: MapperUxROM,
            MapperType.CNROM: MapperCNROM,
            MapperType.MMC3: MapperMMC3,
            MapperType.AxROM: MapperAxROM,
            MapperType.ColorDreams: MapperColorDreams,
            MapperType.GxROM: MapperGxROM
        }
        return mapper_dict.get(mapper_t, None)(cartridge, interrupt_cb, mirroring_cb)

# Example of a derived class MapperNROM
class MapperNROM(Mapper):
    def __init__(self, cartridge, interrupt_cb, mirroring_cb):
        super().__init__(cartridge, MapperType.NROM)
        self.one_bank = len(cartridge.getROM()) == 0x4000
        self.uses_character_ram = len(cartridge.getVROM()) == 0
        if self.uses_character_ram:
            self.character_ram = bytearray(0x2000)
            logging.info("Uses character RAM")

    def writePRG(self, addr, value):
        logging.info(f"ROM memory write attempt at {addr} to set {value}")

    def readPRG(self, addr):
        if not self.one_bank:
            return self.cartridge.getROM()[addr - 0x8000]
        else:
            return self.cartridge.getROM()[(addr - 0x8000) & 0x3fff]

    def readCHR(self, addr):
        if self.uses_character_ram:
            return self.character_ram[addr]
        else:
            return self.cartridge.getVROM()[addr]

    def writeCHR(self, addr, value):
        if self.uses_character_ram:
            self.character_ram[addr] = value
        else:
            logging.info(f"Read-only CHR memory write attempt at {addr:#x}")

# Other derived classes can be implemented similarly
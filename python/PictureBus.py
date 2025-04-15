from Mapper import NameTableMirroring, Mapper

class PictureBus:
    def __init__(self):
        self.m_palette = bytearray(0x20)  # 32 bytes palette
        self.m_RAM = bytearray(0x800)     # 2KB RAM
        self.m_mapper = None
        self.NameTable0 = 0
        self.NameTable1 = 0
        self.NameTable2 = 0
        self.NameTable3 = 0

    def read(self, addr: int) -> int:
        addr &= 0x3fff
        if addr < 0x2000:
            return self.m_mapper.readCHR(addr)
        elif addr <= 0x3eff:
            index = addr & 0x3ff
            normalized_addr = addr
            if addr >= 0x3000:
                normalized_addr -= 0x1000
            if self.NameTable0 >= len(self.m_RAM):
                return self.m_mapper.readCHR(normalized_addr)
            elif normalized_addr < 0x2400:
                return self.m_RAM[self.NameTable0 + index]
            elif normalized_addr < 0x2800:
                return self.m_RAM[self.NameTable1 + index]
            elif normalized_addr < 0x2c00:
                return self.m_RAM[self.NameTable2 + index]
            else:
                return self.m_RAM[self.NameTable3 + index]
        elif addr <= 0x3fff:
            paletteAddr = addr & 0x1f
            if paletteAddr >= 0x10 and paletteAddr % 4 == 0:
                paletteAddr &= 0xf
            return self.m_palette[paletteAddr]
        return 0

    def write(self, addr: int, value: int):
        addr &= 0x3fff
        if addr < 0x2000:
            self.m_mapper.writeCHR(addr, value)
        elif addr <= 0x3eff:
            index = addr & 0x3ff
            normalized_addr = addr
            if addr >= 0x3000:
                normalized_addr -= 0x1000
            if self.NameTable0 >= len(self.m_RAM):
                self.m_mapper.writeCHR(normalized_addr, value)
            else:
                if normalized_addr < 0x2400:
                    self.m_RAM[self.NameTable0 + index] = value
                elif normalized_addr < 0x2800:
                    self.m_RAM[self.NameTable1 + index] = value
                elif normalized_addr < 0x2c00:
                    self.m_RAM[self.NameTable2 + index] = value
                else:
                    self.m_RAM[self.NameTable3 + index] = value
        elif addr <= 0x3fff:
            palette = addr & 0x1f
            if palette >= 0x10 and palette % 4 == 0:
                palette &= 0xf
            self.m_palette[palette] = value

    def updateMirroring(self):
        mirroring = self.m_mapper.getNameTableMirroring()
        if mirroring == NameTableMirroring.Horizontal:
            self.NameTable0 = self.NameTable1 = 0
            self.NameTable2 = self.NameTable3 = 0x400
            print("Horizontal Name Table mirroring set.")
        elif mirroring == NameTableMirroring.Vertical:
            self.NameTable0 = self.NameTable2 = 0
            self.NameTable1 = self.NameTable3 = 0x400
            print("Vertical Name Table mirroring set.")
        elif mirroring == NameTableMirroring.OneScreenLower:
            self.NameTable0 = self.NameTable1 = self.NameTable2 = self.NameTable3 = 0
            print("Single Screen mirroring set with lower bank.")
        elif mirroring == NameTableMirroring.OneScreenHigher:
            self.NameTable0 = self.NameTable1 = self.NameTable2 = self.NameTable3 = 0x400
            print("Single Screen mirroring set with higher bank.")
        elif mirroring == NameTableMirroring.FourScreen:
            self.NameTable0 = len(self.m_RAM)
            print("FourScreen mirroring.")
        else:
            self.NameTable0 = self.NameTable1 = self.NameTable2 = self.NameTable3 = 0
            print("Unsupported mirroring type.")

    def setMapper(self, mapper: Mapper) -> bool:
        if not mapper:
            print("Error: Mapper is None")
            return False
        self.m_mapper = mapper
        self.updateMirroring()
        return True

    def scanlineIRQ(self):
        self.m_mapper.scanlineIRQ()
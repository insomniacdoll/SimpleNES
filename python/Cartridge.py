import logging
import struct

class Cartridge:
    def __init__(self):
        self.m_PRG_ROM = bytearray()
        self.m_CHR_ROM = bytearray()
        self.m_name_table_mirroring = 0
        self.m_mapper_number = 0
        self.m_extended_ram = False
        self.m_chr_ram = False

    def loadFromFile(self, path):
        with open(path, 'rb') as rom_file:
            header = rom_file.read(0x10)
            if header[:4] != b'NES\x1A':
                logging.error("Not a valid iNES image.")
                return False

            banks = header[4]
            logging.info(f"16KB PRG-ROM Banks: {banks}")
            if not banks:
                logging.error("ROM has no PRG-ROM banks.")
                return False

            vbanks = header[5]
            logging.info(f"8KB CHR-ROM Banks: {vbanks}")

            if header[6] & 0x8:
                self.m_name_table_mirroring = NameTableMirroring.FourScreen
                logging.info("Name Table Mirroring: FourScreen")
            else:
                self.m_name_table_mirroring = NameTableMirroring(header[6] & 0x1)
                logging.info(f"Name Table Mirroring: {'Horizontal' if self.m_name_table_mirroring == NameTableMirroring.Horizontal else 'Vertical'}")

            self.m_mapper_number = ((header[6] >> 4) & 0xf) | (header[7] & 0xf0)
            logging.info(f"Mapper #: {self.m_mapper_number}")

            self.m_extended_ram = bool(header[6] & 0x2)
            logging.info(f"Extended (CPU) RAM: {self.m_extended_ram}")

            if header[6] & 0x4:
                logging.error("Trainer is not supported.")
                return False

            if (header[0xA] & 0x3) == 0x2 or (header[0xA] & 0x1):
                logging.error("PAL ROM not supported.")
                return False
            else:
                logging.info("ROM is NTSC compatible.")

            self.m_PRG_ROM = bytearray(0x4000 * banks)
            rom_file.readinto(self.m_PRG_ROM)

            if vbanks:
                self.m_CHR_ROM = bytearray(0x2000 * vbanks)
                rom_file.readinto(self.m_CHR_ROM)
            else:
                logging.info("Cartridge with CHR-RAM.")
                self.m_chr_ram = True

        return True

    def getROM(self):
        return self.m_PRG_ROM

    def getVROM(self):
        return self.m_CHR_ROM

    def getMapper(self):
        return self.m_mapper_number

    def getNameTableMirroring(self):
        return self.m_name_table_mirroring

    def hasExtendedRAM(self):
        return self.m_extended_ram
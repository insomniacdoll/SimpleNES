from enum import Enum
from PictureBus import PictureBus
from VirtualScreen import VirtualScreen
from PaletteColors import PALETTE_COLORS

class PPUState(Enum):
    PreRender = 0
    Render = 1
    PostRender = 2
    VerticalBlank = 3

class CharacterPage(Enum):
    Low = 0
    High = 1

class PPU:
    ScanlineCycleLength = 341
    ScanlineEndCycle = 340
    VisibleScanlines = 240
    ScanlineVisibleDots = 256
    FrameEndScanline = 261

    def __init__(self, bus: PictureBus, screen: VirtualScreen):
        self.m_bus = bus
        self.m_screen = screen
        self.m_spriteMemory = [0] * (64 * 4)
        self.m_scanlineSprites = []
        self.m_pipelineState = PPUState.PreRender
        self.m_cycle = 0
        self.m_scanline = 0
        self.m_evenFrame = False
        self.m_vblank = False
        self.m_sprZeroHit = False
        self.m_spriteOverflow = False
        self.m_dataAddress = 0
        self.m_tempAddress = 0
        self.m_fineXScroll = 0
        self.m_firstWrite = True
        self.m_dataBuffer = 0
        self.m_spriteDataAddress = 0
        self.m_longSprites = False
        self.m_generateInterrupt = False
        self.m_greyscaleMode = False
        self.m_showSprites = True
        self.m_showBackground = True
        self.m_hideEdgeSprites = False
        self.m_hideEdgeBackground = False
        self.m_bgPage = CharacterPage.Low
        self.m_sprPage = CharacterPage.Low
        self.m_dataAddrIncrement = 1
        self.m_vblankCallback = None
        self.m_pictureBuffer = [[0 for _ in range(PPU.VisibleScanlines)] for _ in range(PPU.ScanlineVisibleDots)]

    def reset(self):
        self.m_longSprites = False
        self.m_generateInterrupt = False
        self.m_greyscaleMode = False
        self.m_vblank = False
        self.m_spriteOverflow = False
        self.m_showBackground = True
        self.m_showSprites = True
        self.m_evenFrame = False
        self.m_firstWrite = True
        self.m_bgPage = CharacterPage.Low
        self.m_sprPage = CharacterPage.Low
        self.m_dataAddress = 0
        self.m_cycle = 0
        self.m_scanline = 0
        self.m_spriteDataAddress = 0
        self.m_fineXScroll = 0
        self.m_tempAddress = 0
        self.m_dataAddrIncrement = 1
        self.m_pipelineState = PPUState.PreRender
        self.m_scanlineSprites.clear()

    def setInterruptCallback(self, cb):
        self.m_vblankCallback = cb

    def readOAM(self, addr: int) -> int:
        return self.m_spriteMemory[addr]

    def writeOAM(self, addr: int, value: int):
        self.m_spriteMemory[addr] = value

    def doDMA(self, page_ptr: list[int]):
        offset = self.m_spriteDataAddress
        self.m_spriteMemory[offset:256] = page_ptr[0:256 - offset]
        self.m_spriteMemory[0:offset] = page_ptr[256 - offset:256]

    def getStatus(self) -> int:
        status = (self.m_sprZeroHit << 6) | (self.m_spriteOverflow << 5) | (self.m_vblank << 7)
        self.m_vblank = False
        self.m_firstWrite = True
        return status

    def getDataAddress(self) -> int:
        return self.m_dataAddress

    def setDataAddress(self, addr: int):
        if self.m_firstWrite:
            self.m_tempAddress = (self.m_tempAddress & 0xFF) | ((addr & 0x3F) << 8)
            self.m_firstWrite = False
        else:
            self.m_tempAddress = (self.m_tempAddress & 0xFF00) | addr
            self.m_dataAddress = self.m_tempAddress
            self.m_firstWrite = True

    def getScroll(self) -> int:
        return (self.m_tempAddress >> 3) & 0x1F | self.m_fineXScroll

    def setScroll(self, scroll: int):
        if self.m_firstWrite:
            self.m_tempAddress &= ~0x1F
            self.m_tempAddress |= (scroll >> 3) << 0
            self.m_fineXScroll = scroll & 0x07
            self.m_firstWrite = False
        else:
            self.m_tempAddress &= ~0x73E0
            self.m_tempAddress |= ((scroll & 0x07) << 12) | ((scroll & 0xF8) << 2)
            self.m_firstWrite = True

    def getData(self) -> int:
        data = self.m_bus.read(self.m_dataAddress)
        self.m_dataAddress += self.m_dataAddrIncrement
        if self.m_dataAddress < 0x3F00:
            data, self.m_dataBuffer = self.m_dataBuffer, data
        return data

    def setData(self, value: int):
        self.m_bus.write(self.m_dataAddress, value)
        self.m_dataAddress += self.m_dataAddrIncrement

    def getOAMData(self) -> int:
        return self.readOAM(self.m_spriteDataAddress)

    def setOAMAddress(self, addr: int):
        self.m_spriteDataAddress = addr

    def setOAMData(self, value: int):
        self.writeOAM(self.m_spriteDataAddress, value)
        self.m_spriteDataAddress = (self.m_spriteDataAddress + 1) & 0xFF

    def scanline_sprites(self):
        self.m_scanlineSprites.clear()
        for i in range(64):
            spr_y = self.m_spriteMemory[i * 4]
            if 0 <= (self.m_scanline - spr_y) < (16 if self.m_longSprites else 8):
                self.m_scanlineSprites.append(i)
        self.m_spriteOverflow = len(self.m_scanlineSprites) > 8

    def render_pixel(self, x: int, y: int):
        # 实现像素渲染逻辑（参考C++中的渲染计算）
        pass

    def update_screen(self):
        for x in range(PPU.ScanlineVisibleDots):
            for y in range(PPU.VisibleScanlines):
                color_index = self.m_pictureBuffer[x][y]
                self.m_screen.set_pixel(x, y, PALETTE_COLORS[color_index])

    # 补充其他未实现的step分支逻辑
    def step(self):
        if self.m_pipelineState == PPUState.PreRender:
            if self.m_cycle == 1:
                self.m_vblank = False
                self.m_sprZeroHit = False
            elif self.m_cycle == self.ScanlineVisibleDots + 2 and self.m_showBackground and self.m_showSprites:
                self.m_dataAddress &= ~0x41F
                self.m_dataAddress |= self.m_tempAddress & 0x41F
        
        # MMC3 scanline IRQ support
        if self.m_cycle == 260 and self.m_showBackground and self.m_showSprites:
            self.m_bus.scanlineIRQ()

        # 进入渲染阶段条件判断
        if self.m_cycle >= self.ScanlineEndCycle - (not self.m_evenFrame and self.m_showBackground and self.m_showSprites):
            self.m_pipelineState = PPUState.Render
            self.m_cycle = 0
            self.m_scanline = 0

        elif self.m_pipelineState == PPUState.Render:
            x = self.m_cycle - 1
            y = self.m_scanline

            if 0 < self.m_cycle <= self.ScanlineVisibleDots:
                # 背景渲染逻辑
                if self.m_showBackground:
                    x_fine = (self.m_fineXScroll + x) % 8
                    if not (self.m_hideEdgeBackground and x < 8):
                        addr = 0x2000 | (self.m_dataAddress & 0x0FFF)
                        tile = self.m_bus.read(addr)
                        
                        pattern_addr = (tile * 16) + ((self.m_dataAddress >> 12) & 0x7)
                        pattern_addr |= (self.m_bgPage.value << 12)
                        
                        color_bits = (self.m_bus.read(pattern_addr) >> (7 ^ x_fine)) & 0x01
                        color_bits |= ((self.m_bus.read(pattern_addr + 8) >> (7 ^ x_fine)) & 0x01) << 1
                        
                        # 属性处理（简化版）
                        attr_addr = 0x23C0 | (self.m_dataAddress & 0x0C00) | ((self.m_dataAddress >> 4) & 0x38) | ((self.m_dataAddress >> 2) & 0x07)
                        attr = self.m_bus.read(attr_addr)
                        shift = ((self.m_dataAddress >> 4) & 4) | (self.m_dataAddress & 2)
                        color_bits |= ((attr >> shift) & 0x03) << 2

                        self.m_pictureBuffer[x][y] = color_bits

                    # 数据地址更新
                    if x_fine == 7:
                        if (self.m_dataAddress & 0x001F) == 31:
                            self.m_dataAddress &= ~0x001F
                            self.m_dataAddress ^= 0x0400
                        else:
                            self.m_dataAddress += 1

                # 精灵渲染逻辑（待补充完整）
                # ...（此处需要完整实现精灵检测和渲染逻辑）

            elif self.m_cycle == self.ScanlineVisibleDots + 1 and self.m_showBackground:
                # 数据地址更新逻辑
                if (self.m_dataAddress & 0x7000) != 0x7000:
                    self.m_dataAddress += 0x1000
                else:
                    self.m_dataAddress &= ~0x7000
                    y_coarse = (self.m_dataAddress & 0x03E0) >> 5
                    if y_coarse == 29:
                        y_coarse = 0
                        self.m_dataAddress ^= 0x0800
                    elif y_coarse == 31:
                        y_coarse = 0
                    else:
                        y_coarse += 1
                    self.m_dataAddress = (self.m_dataAddress & ~0x03E0) | (y_coarse << 5)

            # 精灵数据准备
            if self.m_cycle >= self.ScanlineEndCycle:
                self.m_scanlineSprites.clear()
                range_val = 16 if self.m_longSprites else 8
                for i in range(64):
                    spr_y = self.m_spriteMemory[i*4]
                    if 0 <= (self.m_scanline - spr_y) < range_val:
                        self.m_scanlineSprites.append(i)
                        if len(self.m_scanlineSprites) > 8:
                            self.m_spriteOverflow = True
                            break

                self.m_cycle = 0
                self.m_scanline += 1

                if self.m_scanline >= self.VisibleScanlines:
                    self.m_pipelineState = PPUState.PostRender

        elif self.m_pipelineState == PPUState.PostRender:
            if self.m_cycle >= self.ScanlineEndCycle:
                self.m_cycle = 0
                self.m_scanline += 1
                self.m_pipelineState = PPUState.VerticalBlank

        elif self.m_pipelineState == PPUState.VerticalBlank:
            if self.m_cycle == 1 and self.m_scanline == self.VisibleScanlines + 1:
                self.m_vblank = True
                if self.m_generateInterrupt and self.m_vblankCallback:
                    self.m_vblankCallback()

            if self.m_cycle >= self.ScanlineEndCycle:
                self.m_cycle = 0
                self.m_scanline += 1

                if self.m_scanline >= self.FrameEndScanline:
                    self.m_pipelineState = PPUState.PreRender
                    self.m_scanline = 0
                    self.m_evenFrame = not self.m_evenFrame

        self.m_cycle += 1

    def control(self, ctrl):
        self.m_generateInterrupt = bool(ctrl & 0x80)
        self.m_longSprites = bool(ctrl & 0x20)
        self.m_bgPage = CharacterPage.High if (ctrl & 0x10) else CharacterPage.Low
        self.m_sprPage = CharacterPage.High if (ctrl & 0x8) else CharacterPage.Low
        self.m_dataAddrIncrement = 0x20 if (ctrl & 0x4) else 1
        self.m_tempAddress &= ~0xc00
        self.m_tempAddress |= (ctrl & 0x3) << 10

    def setMask(self, mask):
        self.m_greyscaleMode = bool(mask & 0x1)
        self.m_hideEdgeBackground = not bool(mask & 0x2)
        self.m_hideEdgeSprites = not bool(mask & 0x4)
        self.m_showBackground = bool(mask & 0x8)
        self.m_showSprites = bool(mask & 0x10)

    # 其他方法（如readOAM、doDMA等）的转换实现
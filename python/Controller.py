from sfml import sf

class Controller:
    A = 0
    B = 1
    Select = 2
    Start = 3
    Up = 4
    Down = 5
    Left = 6
    Right = 7
    TotalButtons = 8

    def __init__(self):
        self.m_strobe = False
        self.m_key_states = 0
        self.m_key_bindings = [
            sf.Keyboard.J,          # A
            sf.Keyboard.K,          # B
            sf.Keyboard.R_SHIFT,    # Select
            sf.Keyboard.RETURN,     # Start
            sf.Keyboard.W,          # Up
            sf.Keyboard.S,          # Down
            sf.Keyboard.A,          # Left
            sf.Keyboard.D           # Right
        ]

    def strobe(self, b: int):
        self.m_strobe = bool(b & 1)
        if not self.m_strobe:
            self.m_key_states = 0
            shift = 0
            for button in range(self.TotalButtons):
                key = self.m_key_bindings[button]
                if sf.Keyboard.is_key_pressed(key):
                    self.m_key_states |= (1 << shift)
                shift += 1

    def read(self) -> int:
        if self.m_strobe:
            key = self.m_key_bindings[self.A]
            return int(sf.Keyboard.is_key_pressed(key)) | 0x40
        else:
            result = self.m_key_states & 1
            self.m_key_states >>= 1
            return result | 0x40

    def set_key_bindings(self, keys: list):
        if len(keys) != self.TotalButtons:
            raise ValueError(f"Key bindings must have exactly {self.TotalButtons} elements")
        self.m_key_bindings = keys
import sfml as sf
import configparser

def parse_controller_config(filepath, p1_keys, p2_keys):
    button_names = ["A", "B", "Select", "Start", "Up", "Down", "Left", "Right"]
    key_names = [
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O",
        "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
        "NUM0", "NUM1", "NUM2", "NUM3", "NUM4", "NUM5", "NUM6", "NUM7", "NUM8", "NUM9",
        "ESCAPE", "LCONTROL", "LSHIFT", "LALT", "LSYSTEM", "RCONTROL", "RSHIFT", "RALT", "RSYSTEM",
        "MENU", "LBRACKET", "RBRACKET", "SEMICOLON", "COMMA", "PERIOD", "QUOTE", "SLASH",
        "BACKSLASH", "TILDE", "EQUAL", "DASH", "SPACE", "RETURN", "BACKSPACE", "TAB",
        "PAGEUP", "PAGEDOWN", "END", "HOME", "INSERT", "DELETE", "ADD", "SUBTRACT",
        "MULTIPLY", "DIVIDE", "LEFT", "RIGHT", "UP", "DOWN",
        "NUMPAD0", "NUMPAD1", "NUMPAD2", "NUMPAD3", "NUMPAD4", "NUMPAD5", "NUMPAD6",
        "NUMPAD7", "NUMPAD8", "NUMPAD9",
        "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
        "F13", "F14", "F15", "PAUSE"
    ]

    config = configparser.ConfigParser(optionxform=lambda x: x)
    config.read(filepath)

    for section in config.sections():
        if section not in ["Player1", "Player2"]:
            print(f"Warning: Ignoring unknown section {section}")
            continue

        target = p1_keys if section == "Player1" else p2_keys
        for option in config.options(section):
            if option not in button_names:
                print(f"Error: Invalid button name '{option}' in section {section}")
                continue

            value = config.get(section, option).upper()
            if value not in key_names:
                print(f"Error: Invalid key '{value}' for button '{option}' in section {section}")
                continue

            key = getattr(sf.Keyboard, value)
            btn_idx = button_names.index(option)
            target[btn_idx] = key

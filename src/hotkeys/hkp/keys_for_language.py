"""Generate a key-value-modded-strings-utf8.txt for AoE2:DE hotkey mods.

Reads custom .hkp hotkey files and produces the IDS_MOD_TTS_VISIBLE_HOTKEYS
entries that control the key labels shown on the in-game command grid:

    | 01 | 02 | 03 | 04 | 05 |
    | 06 | 07 | 08 | 09 | 10 |
    | 11 | 12 | 13 | 14 | 15 |

The 15 positions map to the Economic Build Menu hotkeys (House, Mill,
Mining Camp, ..., More Buildings) in the order defined by hk_groups.

Run from ``src/``:
    python -m hotkeys.hkp.keys_for_language Base.hkp [Profile.hkp] [-o output.txt]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

if __package__ in (None, ""):
    _here = os.path.dirname(os.path.abspath(__file__))
    _src = os.path.abspath(os.path.join(_here, "..", ".."))
    if _src not in sys.path:
        sys.path.insert(0, _src)
    from hotkeys.hkp.new_hotkey_file import HotkeyFile  # type: ignore
    from hotkeys.hkp.parse import FileType  # type: ignore
    from hotkeys.hkp.strings import hk_groups  # type: ignore
else:
    from .new_hotkey_file import HotkeyFile
    from .parse import FileType
    from .strings import hk_groups


# The 15 Economic Build Menu string IDs, in grid order 01-15.
GRID_STRING_IDS: List[int] = hk_groups["Economic Build Menu"]

# AoE2 virtual-key-code → display label for the mod overlay.
# Letters and digits are shown uppercase; special keys get short names.
KEYCODE_LABELS: Dict[int, str] = {
    0: "",
    8: "Bksp", 9: "Tab", 13: "Enter", 16: "Shift", 17: "Ctrl", 18: "Alt",
    19: "Pause", 20: "Caps", 27: "Esc", 32: "Space",
    33: "PgUp", 34: "PgDn", 35: "End", 36: "Home",
    37: "Left", 38: "Up", 39: "Right", 40: "Down",
    44: "PrtSc", 45: "Ins", 46: "Del",
    91: "LWin", 92: "RWin", 93: "Menu",
    96: "Num0", 97: "Num1", 98: "Num2", 99: "Num3", 100: "Num4",
    101: "Num5", 102: "Num6", 103: "Num7", 104: "Num8", 105: "Num9",
    106: "Num*", 107: "Num+", 108: "Num,", 109: "Num-", 110: "Num.", 111: "Num/",
    112: "F1", 113: "F2", 114: "F3", 115: "F4", 116: "F5", 117: "F6",
    118: "F7", 119: "F8", 120: "F9", 121: "F10", 122: "F11", 123: "F12",
    144: "NumLk", 145: "ScrLk",
    186: ";", 187: "=", 188: ",", 189: "-", 190: ".", 191: "/", 192: "`",
    219: "[", 220: "\\", 221: "]", 222: "'",
    251: "XBtn2", 252: "XBtn1", 253: "MBtn", 254: "WhlDn", 255: "WhlUp",
}


def keycode_to_label(code: int) -> str:
    if code in KEYCODE_LABELS:
        return KEYCODE_LABELS[code]
    if 48 <= code <= 57:
        return chr(code)
    if 65 <= code <= 90:
        return chr(code)
    return f"0x{code:02X}"


def detect_file_type(name: str) -> FileType:
    return FileType.HKP if Path(name).stem.lower() == "base" else FileType.HKI


def load_hotkeys(paths: List[str]) -> Dict[int, int]:
    """Load hotkey files and return {string_id: keycode} for all hotkeys."""
    sid_to_keycode: Dict[int, int] = {}
    for p in paths:
        ftype = detect_file_type(p)
        with open(p, "rb") as f:
            hf = HotkeyFile(f.read(), False, Path(p).name, ftype)
        for _key, entry in hf.data.items():
            sid_to_keycode[entry["string_id"]] = entry["keycode"]
    return sid_to_keycode


HEADER_TEMPLATE = """\
//INSTRUCTIONS:
//In this File you can change the Keys that are Displayed to you inGame
//Below you see the pattern for the Keys in the Building/Unit/Production menue:
//
//--------------------------
//| 01 | 02 | 03 | 04 | 05 |
//|------------------------|
//| 06 | 07 | 08 | 09 | 10 |
//|------------------------|
//| 11 | 12 | 13 | 14 | 15 |
//--------------------------
//
//The Numbers are a short form of the StringIDs below
// 01 stands for IDS_MOD_TTS_VISIBLE_HOTKEYS_01 witch is the House in the Building menue
// in the "" you can put the Key that you want to be displayed
//
//Example:
//I edit the line IDS_MOD_TTS_VISIBLE_HOTKEYS_01 and change "Q" to "P"
//It now looks like:
//IDS_MOD_TTS_VISIBLE_HOTKEYS_01 "P"
//
//If you want to make individual Keys invisible, just set them to ""
//
"""


def generate(paths: List[str]) -> str:
    sid_to_keycode = load_hotkeys(paths)
    lines = [HEADER_TEMPLATE]
    for i, sid in enumerate(GRID_STRING_IDS):
        code = sid_to_keycode.get(sid, 0)
        label = keycode_to_label(code)
        lines.append(f'IDS_MOD_TTS_VISIBLE_HOTKEYS_{i + 1:02d} "{label}"')
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m hotkeys.hkp.keys_for_language",
        description="Generate key-value-modded-strings-utf8.txt from custom .hkp files.",
    )
    p.add_argument("files", nargs="+",
                    help="One or more .hkp files (Base.hkp and/or profile)")
    p.add_argument("-o", "--output", default=None,
                    help="Output path (default: stdout)")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    result = generate(args.files)
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

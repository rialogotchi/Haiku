#!/usr/bin/env python3
"""KDE .colors  ->  Haiku app_server 'appearance' ayar dosyasi.

Haiku'nun renkleri ~/config/settings/system/app_server/appearance dosyasinda
duz (flattened) bir BMessage olarak tutulur; her renk "color<N>" adli int32
alanidir (N = color_which sabiti). Bu betik o dosyayi dogrudan uretir.

Kullanim:
  python3 kde2haiku.py Future.colors -o appearance
  python3 kde2haiku.py --verify appearance
"""
import argparse, configparser, struct, sys

WHICH = {
    "PANEL_BACKGROUND": 1, "MENU_BACKGROUND": 2, "WINDOW_TAB": 3,
    "KEYBOARD_NAVIGATION": 4, "DESKTOP": 5, "MENU_SELECTED_BACKGROUND": 6,
    "MENU_ITEM_TEXT": 7, "MENU_SELECTED_ITEM_TEXT": 8,
    "MENU_SELECTED_BORDER": 9, "PANEL_TEXT": 10, "DOCUMENT_BACKGROUND": 11,
    "DOCUMENT_TEXT": 12, "CONTROL_BACKGROUND": 13, "CONTROL_TEXT": 14,
    "CONTROL_BORDER": 15, "CONTROL_HIGHLIGHT": 16, "NAVIGATION_PULSE": 17,
    "SHINE": 18, "SHADOW": 19, "TOOLTIP_BACKGROUND": 20, "TOOLTIP_TEXT": 21,
    "WINDOW_TEXT": 22, "WINDOW_INACTIVE_TAB": 23, "WINDOW_INACTIVE_TEXT": 24,
    "WINDOW_BORDER": 25, "WINDOW_INACTIVE_BORDER": 26, "CONTROL_MARK": 27,
    "LIST_BACKGROUND": 28, "LIST_SELECTED_BACKGROUND": 29,
    "LIST_ITEM_TEXT": 30, "LIST_SELECTED_ITEM_TEXT": 31,
    "SCROLL_BAR_THUMB": 32, "LINK_TEXT": 33, "LINK_HOVER": 34,
    "LINK_VISITED": 35, "LINK_ACTIVE": 36, "STATUS_BAR": 37,
    "SUCCESS": 100, "FAILURE": 101,
}
B_INT32 = 0x4C4F4E47          # 'LONG'
FORMAT = 0x31464D48           # '1FMH'  (MESSAGE_FORMAT_HAIKU)
WHAT = 0x61736C6B             # 'aslk'
HASH_SIZE = 5
HDR = "<IIIiiiiiiIII"
FLD = "<HHIIIIi"          # field_header: 24 bayt


def rgb(s):
    r, g, b = (int(x) for x in s.split(",")[:3])
    return (r, g, b)


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def map_colors(path):
    cp = configparser.ConfigParser(interpolation=None)
    cp.optionxform = str
    cp.read(path, encoding="utf-8")

    def g(sec, key):
        return rgb(cp["Colors:" + sec][key])

    win_bg, win_fg = g("Window", "BackgroundNormal"), g("Window", "ForegroundNormal")
    win_alt = g("Window", "BackgroundAlternate")
    view_bg, view_fg = g("View", "BackgroundNormal"), g("View", "ForegroundNormal")
    btn_bg, btn_fg = g("Button", "BackgroundNormal"), g("Button", "ForegroundNormal")
    sel_bg, sel_fg = g("Selection", "BackgroundNormal"), g("Selection", "ForegroundNormal")
    sel_alt = g("Selection", "BackgroundAlternate")
    tip_bg, tip_fg = g("Tooltip", "BackgroundNormal"), g("Tooltip", "ForegroundNormal")
    wm = cp["WM"]
    tab, tab_txt = rgb(wm["activeBackground"]), rgb(wm["activeForeground"])
    itab, itab_txt = rgb(wm["inactiveBackground"]), rgb(wm["inactiveForeground"])

    if abs(lum(btn_bg) - lum(win_bg)) >= 6:
        control_bg = btn_bg
    elif abs(lum(win_alt) - lum(win_bg)) >= 6:
        control_bg = win_alt
    else:
        control_bg = mix(win_bg, win_fg, 0.07)

    return {
        "PANEL_BACKGROUND": win_bg, "PANEL_TEXT": win_fg,
        "MENU_BACKGROUND": view_bg, "MENU_ITEM_TEXT": view_fg,
        "MENU_SELECTED_BACKGROUND": sel_bg, "MENU_SELECTED_ITEM_TEXT": sel_fg,
        "MENU_SELECTED_BORDER": sel_alt,
        "WINDOW_TAB": tab, "WINDOW_TEXT": tab_txt,
        "WINDOW_INACTIVE_TAB": itab, "WINDOW_INACTIVE_TEXT": itab_txt,
        "WINDOW_BORDER": tab, "WINDOW_INACTIVE_BORDER": itab,
        "KEYBOARD_NAVIGATION": sel_bg, "NAVIGATION_PULSE": view_fg,
        "DOCUMENT_BACKGROUND": view_bg, "DOCUMENT_TEXT": view_fg,
        "CONTROL_BACKGROUND": control_bg, "CONTROL_TEXT": btn_fg,
        "CONTROL_BORDER": mix(win_bg, win_fg, 0.30),
        "CONTROL_HIGHLIGHT": sel_bg, "CONTROL_MARK": sel_alt,
        "SHINE": (255, 255, 255), "SHADOW": (0, 0, 0),
        "TOOLTIP_BACKGROUND": tip_bg, "TOOLTIP_TEXT": tip_fg,
        "LIST_BACKGROUND": view_bg, "LIST_SELECTED_BACKGROUND": sel_bg,
        "LIST_ITEM_TEXT": view_fg, "LIST_SELECTED_ITEM_TEXT": sel_fg,
        "SCROLL_BAR_THUMB": control_bg,
        "LINK_TEXT": g("View", "ForegroundLink"),
        "LINK_HOVER": g("View", "DecorationHover"),
        "LINK_VISITED": g("View", "ForegroundVisited"),
        "LINK_ACTIVE": g("View", "ForegroundActive"),
        "STATUS_BAR": sel_bg,
        "SUCCESS": g("View", "ForegroundPositive"),
        "FAILURE": g("View", "ForegroundNegative"),
        "DESKTOP": (51, 102, 152),
    }


def hash_name(name):
    M = 0xFFFFFFFF
    r = 0
    for ch in name.encode():
        r = (((r << 7) & M) ^ (r >> 24)) & M
        r ^= ch
    r ^= (r << 12) & M
    return r & M


def flatten(colors):
    names = [("color%d" % w, colors[k] + (255,)) for k, w in sorted(WHICH.items(), key=lambda kv: kv[1])]
    names.append(("color102", (0, 0, 0, 0)))
    hashtab = [-1] * HASH_SIZE
    next_field = [-1] * len(names)
    data, fields = b"", []
    for idx, (name, (r, g, b, a)) in enumerate(names):
        h = hash_name(name) % HASH_SIZE
        if hashtab[h] < 0:
            hashtab[h] = idx
        else:
            j = hashtab[h]
            while next_field[j] >= 0:
                j = next_field[j]
            next_field[j] = idx
        nm = name.encode() + b"\0"
        fields.append((len(data), len(nm)))
        data += nm + bytes([r, g, b, a])      # rgb_color: red,green,blue,alpha
    out = struct.pack(HDR, FORMAT, WHAT, 1, -1, -1, -1, -1, -1, -1,
                      len(data), len(names), HASH_SIZE)
    out += struct.pack("<%di" % HASH_SIZE, *hashtab)
    for idx, (offset, nlen) in enumerate(fields):
        out += struct.pack(FLD, 0x0003, nlen, B_INT32, 1, 4, offset, next_field[idx])
    return out + data


def verify(blob):
    """BMessage::Unflatten + _ValidateMessage + hash aramasini taklit eder."""
    hdr = struct.calcsize(HDR)
    v = struct.unpack_from(HDR, blob, 0)
    fmt, flags, data_size, count, hsize = v[0], v[2], v[9], v[10], v[11]
    assert fmt == FORMAT and flags & 1 and hsize == HASH_SIZE, "baslik hatali"
    tab = struct.unpack_from("<%di" % HASH_SIZE, blob, hdr)
    fpos = hdr + 4 * HASH_SIZE
    dpos = fpos + count * struct.calcsize(FLD)
    assert len(blob) == dpos + data_size, "boyut tutmuyor"
    flds = [struct.unpack_from(FLD, blob, fpos + struct.calcsize(FLD) * i) for i in range(count)]
    for f in flds:
        assert f[5] + f[1] + f[4] <= data_size and f[6] <= count, "bozuk alan"
    found = {}
    for w in WHICH.values():
        name = "color%d" % w
        i = tab[hash_name(name) % HASH_SIZE]
        while i >= 0:
            f = flds[i]
            o = dpos + f[5]
            if blob[o:o + f[1] - 1] == name.encode():
                found[w] = tuple(blob[o + f[1]:o + f[1] + 3])
                break
            i = f[6]
        assert w in found, name + " bulunamadi"
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("colors", nargs="?", help="KDE .colors dosyasi")
    ap.add_argument("-o", "--output", default="appearance")
    ap.add_argument("--verify", metavar="DOSYA", help="uretilmis dosyayi dogrula")
    a = ap.parse_args()
    if a.verify:
        print("OK: %d renk dogrulandi" % len(verify(open(a.verify, "rb").read())))
        return
    if not a.colors:
        ap.error("bir .colors dosyasi verin")
    blob = flatten(map_colors(a.colors))
    verify(blob)
    open(a.output, "wb").write(blob)
    print("yazildi:", a.output, len(blob), "bayt")


if __name__ == "__main__":
    sys.exit(main())

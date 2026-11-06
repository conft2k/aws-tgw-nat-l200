"""Tiny helpers for writing skill-format drafts (rect/image/text/line/polyline/circle only)."""
from xml.sax.saxutils import escape

INK = "#232F3E"
SUB = "#3B4552"      # secondary text: darker than the old #545B64
GREY = "#7D8998"
TEAL = "#00A4A6"
PURPLE = "#8C4FFF"
GREEN = "#7AA116"
RED = "#DD344C"
PINK = "#E7157B"
S = 48
F_NODE = 19   # node labels
F_SUB = 16    # sub-captions, connector labels, table
F_TITLE = 19  # container titles (bold)
F_TAG = 16
LH = 21       # line pitch for 16-19px lines


def tw(s, fs):
    w = 0.0
    for c in s:
        wide = ("ᄀ" <= c <= "ᇿ" or "←" <= c <= "⯿" or "　" <= c <= "鿿" or "가" <= c <= "힣")
        w += fs * (1.0 if wide else 0.55)
    return w


class D:
    def __init__(self):
        self.el = []

    def raw(self, s):
        self.el.append(s)

    def text(self, x, y, s, fs=F_SUB, fill=INK, weight=None, anchor=None):
        a = f' font-weight="{weight}"' if weight else ""
        b = f' text-anchor="{anchor}"' if anchor else ""
        self.el.append(f'<text x="{x:g}" y="{y:g}" font-size="{fs}"{a}{b} fill="{fill}">{escape(s)}</text>')

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=None, dash=None, rx=None):
        s = f' stroke="{stroke}"' if stroke else ""
        s += f' stroke-width="{sw}"' if sw else ""
        s += f' stroke-dasharray="{dash}"' if dash else ""
        s += f' rx="{rx}"' if rx else ""
        self.el.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}"{s}/>')

    def img(self, ref, x, y, size=S):
        self.el.append(f'<image href="bundle:{ref}" x="{x:g}" y="{y:g}" width="{size}" height="{size}"/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.5, dash=None, marker=None):
        s = f' stroke-dasharray="{dash}"' if dash else ""
        s += f' marker-end="url(#{marker})"' if marker else ""
        self.el.append(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="{sw}"{s}/>')

    def poly(self, pts, stroke=INK, sw=1.5, dash=None, marker=None):
        p = " ".join(f"{x:g},{y:g}" for x, y in pts)
        s = f' stroke-dasharray="{dash}"' if dash else ""
        s += f' marker-end="url(#{marker})"' if marker else ""
        self.el.append(f'<polyline points="{p}" fill="none" stroke="{stroke}" stroke-width="{sw}"{s}/>')

    def circle(self, cx, cy, r, fill):
        self.el.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="{r}" fill="{fill}"/>')

    # --- composites -------------------------------------------------------
    def node(self, ref, cx, cy, lines):
        """Icon centred on (cx, cy) with lines below: (text, kind) kind in name/sub/bold/subbold."""
        self.img(ref, cx - S / 2, cy - S / 2)
        y = cy + S / 2 + 20
        for i, ln in enumerate(lines):
            s, kind = ln if isinstance(ln, tuple) else (ln, "name" if i == 0 else "sub")
            self._ln(cx, y, s, kind, "middle")
            y += LH
        return y - LH  # last baseline

    def side(self, x, cy, lines, anchor="start"):
        """Lines beside an icon, vertically centred on cy."""
        n = len(lines)
        y0 = cy - (n - 1) * LH / 2 + 6
        for i, ln in enumerate(lines):
            s, kind = ln if isinstance(ln, tuple) else (ln, "name" if i == 0 else "sub")
            self._ln(x, y0 + i * LH, s, kind, anchor if anchor != "start" else None)

    def _ln(self, x, y, s, kind, anchor):
        if kind == "name":
            self.text(x, y, s, F_NODE, INK, None, anchor)
        elif kind == "namebold":
            self.text(x, y, s, F_NODE, INK, "600", anchor)
        elif kind == "sub":
            self.text(x, y, s, F_SUB, SUB, None, anchor)
        elif kind == "subink":
            self.text(x, y, s, F_SUB, INK, None, anchor)
        elif kind == "bold":
            self.text(x, y, s, F_SUB, INK, "700", anchor)
        else:
            raise ValueError(kind)

    def group(self, x, y, w, h, kind, title, cidr=None, badge=True):
        sty = {
            "cloud": (INK, 2, None, "group/AWS-Cloud-logo_32"),
            "region": (TEAL, 2, "3,3", "group/Region_32"),
            "vpc": (PURPLE, 2, None, "group/Virtual-private-cloud-VPC_32"),
            "private": (TEAL, 1.5, None, "group/Private-subnet_32"),
            "onprem": (GREY, 2, None, "group/Corporate-data-center_32"),
            "sg": (RED, 1.5, None, None),
        }[kind]
        col, sw, dash, ref = sty
        self.rect(x, y, w, h, "none", col, sw, dash)
        if kind == "cloud":
            self.img(ref, x, y, 32)
            self.text(x + 42, y + 23, title, F_TITLE, col, "600")
            return
        if ref:
            self.img(ref, x, y, 24)
            tx = x + 32
        else:
            tx = x + 12
        self.text(tx, y + 19, title, F_TITLE, col, "600")
        if cidr:
            self.text(tx, y + 37, cidr, F_SUB, INK)

    def tag(self, x, base, s, fill=INK, anchor="start"):
        """Dark label chip; base is the text baseline. Returns (x0, x1)."""
        w = tw(s, F_TAG) + 14
        x0 = x - w / 2 if anchor == "middle" else x
        self.rect(x0, base - 16.5, w, 22, fill, rx=3)
        self.text(x0 + w / 2, base, s, F_TAG, "#FFFFFF", "600", "middle")
        return x0, x0 + w

    def svg(self, w, h, defs):
        head = (f'<svg viewBox="0 0 {w:g} {h:g}" xmlns="http://www.w3.org/2000/svg" '
                "font-family=\"'Noto Sans CJK KR', 'Pretendard', Arial, sans-serif\">\n")
        return head + defs + f'<rect width="{w:g}" height="{h:g}" fill="#FFFFFF"/>\n' + "\n".join(self.el) + "\n</svg>\n"


def markers(*names):
    cols = {"arrow": INK, "arrowGreen": "#1D8102", "arrowOrange": "#E07000", "arrowRed": "#D13212", "arrowGrey": GREY}
    out = ["<defs>"]
    for n in names:
        out.append(f'<marker id="{n}" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
                   f'<path d="M0,0 L8,3 L0,6 Z" fill="{cols[n]}"/></marker>')
    out.append("</defs>\n")
    return "\n".join(out)

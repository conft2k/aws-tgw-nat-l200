"""Tiny helper for writing skill-subset SVG drafts with exact coordinates."""
from xml.sax.saxutils import escape

INK = "#232F3E"
L = 18   # node labels, container titles
M = 16   # captions, connector labels, table cells
S = 48   # node icon size


def tw(s, fs):
    w = 0.0
    for c in s:
        wide = ("ᄀ" <= c <= "ᇿ" or "←" <= c <= "⯿" or "　" <= c <= "鿿" or "가" <= c <= "힣")
        w += fs * (1.0 if wide else 0.55)
    return w


class D:
    def __init__(self):
        self.out = []

    def add(self, s):
        self.out.append(s)

    def text(self, x, y, s, fs=M, fill=INK, weight=None, anchor=None):
        a = f' font-weight="{weight}"' if weight else ""
        b = f' text-anchor="{anchor}"' if anchor else ""
        self.add(f'<text x="{x:g}" y="{y:g}" font-size="{fs}"{a}{b} fill="{fill}">{escape(s)}</text>')

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=None, dash=None, rx=None):
        s = f' stroke="{stroke}"' if stroke else ""
        s += f' stroke-width="{sw}"' if sw else ""
        s += f' stroke-dasharray="{dash}"' if dash else ""
        s += f' rx="{rx}"' if rx else ""
        self.add(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}"{s}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.5, dash=None, marker=None):
        s = f' stroke-dasharray="{dash}"' if dash else ""
        s += f' marker-end="url(#{marker})"' if marker else ""
        self.add(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="{sw}"{s}/>')

    def poly(self, pts, stroke=INK, sw=1.5, dash=None, marker=None):
        p = " ".join(f"{x:g},{y:g}" for x, y in pts)
        s = f' stroke-dasharray="{dash}"' if dash else ""
        s += f' marker-end="url(#{marker})"' if marker else ""
        self.add(f'<polyline points="{p}" fill="none" stroke="{stroke}" stroke-width="{sw}"{s}/>')

    def image(self, ref, x, y, size):
        self.add(f'<image href="bundle:{ref}" x="{x:g}" y="{y:g}" width="{size}" height="{size}"/>')

    def circle(self, cx, cy, r, fill):
        self.add(f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="{fill}"/>')

    # ---- AWS groups. Header: 28px badge, 18px bold title at baseline y+21, optional 16px
    # sub-line at y+39; nested boxes start at y+36 (y+52 with a sub-line).
    GROUPS = {
        "region": ("#00A4A6", 2, "3,3", "group/Region_32"),
        "vpc": ("#8C4FFF", 2, None, "group/Virtual-private-cloud-VPC_32"),
        "private": ("#00A4A6", 1.5, None, "group/Private-subnet_32"),
        "onprem": ("#7D8998", 2, None, "group/Corporate-data-center_32"),
    }

    def cloud(self, x, y, w, h):
        self.rect(x, y, w, h, stroke=INK, sw=2)
        self.image("group/AWS-Cloud-logo_32", x, y, 32)
        self.text(x + 42, y + 23, "AWS Cloud", 19, weight="600")

    def group(self, kind, x, y, w, h, title, sub=None):
        color, sw, dash, badge = self.GROUPS[kind]
        self.rect(x, y, w, h, stroke=color, sw=sw, dash=dash)
        self.image(badge, x, y, 28)
        self.text(x + 36, y + 21, title, L, fill=color, weight="600")
        if sub:
            self.text(x + 36, y + 39, sub, M)

    def node(self, ref, cx, cy, lines):
        """Icon centered at (cx, cy); lines = [(text, size, fill, weight)] below it."""
        self.image(ref, cx - S / 2, cy - S / 2, S)
        y = cy + S / 2 + 20
        prev = None
        for i, ln in enumerate(lines):
            s, fs = ln[0], ln[1]
            fill = ln[2] if len(ln) > 2 else INK
            wt = ln[3] if len(ln) > 3 else None
            if i:
                y += 22 if prev == L else 20
            self.text(cx, y, s, fs, fill=fill, weight=wt, anchor="middle")
            prev = fs
        return y

    def svg(self, w, h, defs=""):
        head = (f'<svg viewBox="0 0 {w:g} {h:g}" xmlns="http://www.w3.org/2000/svg" '
                f'font-family="\'Noto Sans CJK KR\', \'Pretendard\', Arial, sans-serif">\n')
        return head + f"<defs>{defs}</defs>\n" + f'<rect width="{w:g}" height="{h:g}" fill="#FFFFFF"/>\n' + \
            "\n".join(self.out) + "\n</svg>\n"


def marker(mid, color):
    return (f'<marker id="{mid}" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
            f'<path d="M0,0 L8,3 L0,6 Z" fill="{color}"/></marker>')


def table(d, x, y, cols, rows, header=None, row_h=34, line="#AAB7B8"):
    """cols = [(title, width)]; rows = [[(text, fill, weight) or text, ...]].
    header = (text, bg, fg) band above the column titles. Returns bottom y."""
    W = sum(c[1] for c in cols)
    if header:
        txt, bg, fg = header[:3]
        d.rect(x, y, W, row_h, fill=bg, stroke=bg, sw=1)
        d.text(x + 10, y + 22, txt, M, fill=fg, weight="700")
        y += row_h
    cx = x
    for t, w in cols:
        d.rect(cx, y, w, row_h, fill="#EAEDED", stroke=line, sw=1)
        d.text(cx + 9, y + 21, t, M, weight="700")
        cx += w
    y += row_h
    for r in rows:
        if isinstance(r, dict):  # full-width row
            d.rect(x, y, W, row_h, fill=r.get("bg", "#FFFFFF"), stroke=line, sw=1)
            d.text(x + 9, y + 21, r["text"], M, fill=r.get("fill", INK), weight=r.get("weight"))
            y += row_h
            continue
        cx = x
        for (t, w), cell in zip(cols, r):
            s, fill, wt = (cell, INK, None) if isinstance(cell, str) else cell
            d.rect(cx, y, w, row_h, fill="#FFFFFF", stroke=line, sw=1)
            d.text(cx + 9, y + 21, s, M, fill=fill, weight=wt)
            cx += w
        y += row_h
    return y

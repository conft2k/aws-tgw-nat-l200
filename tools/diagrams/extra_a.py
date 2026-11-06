"""extra-a: on-premises at the bottom, traffic flows upward to VPC-B.

On the left is impossible at a 900px-readable size (canvas <= 1200px wide), so the
guide's fallback applies: the on-premises group goes at the bottom.
"""
import sys
sys.path.insert(0, sys.path[0])
from lib import *

OUT = sys.argv[1]
d = D()
G1, OR, RD = "#1D8102", "#E07000", "#D13212"
BR = 13          # flow badge radius


def badge_row(x, base, tag, col, s, weight="600"):
    d.circle(x + BR, base - 5.5, BR, col)
    d.text(x + BR, base, tag, F_SUB, "#FFFFFF", "700", "middle")
    d.text(x + 2 * BR + 6, base, s, F_SUB, col, weight)


# four flows: (colour, dash, marker, forward?) -- forward = on-prem -> AWS direction
FLOWS = [(G1, None, "arrowGreen", True), (G1, "6,3", "arrowGreen", False),
         (OR, None, "arrowOrange", False), (RD, "6,3", "arrowRed", True)]


def hflows(x1, x2, cy):
    """x1 < x2, lines at cy-21..cy+21 (A1 on top); forward points right."""
    for i, (c, dash, m, fwd) in enumerate(FLOWS):
        y = cy - 21 + 14 * i
        if fwd:
            d.line(x1, y, x2, y, c, dash=dash, marker=m)
        else:
            d.line(x2, y, x1, y, c, dash=dash, marker=m)


def vflows_up(cx, y1, y2):
    """y1 < y2, lines at cx-21..cx+21 (A1 on the left, as the bundle turns right -> up);
    forward points up."""
    for i, (c, dash, m, fwd) in enumerate(FLOWS):
        x = cx - 21 + 14 * i
        if fwd:
            d.line(x, y2, x, y1, c, dash=dash, marker=m)
        else:
            d.line(x, y1, x, y2, c, dash=dash, marker=m)


X = 630                      # the spine: DX -> DXGW -> TGW -> VPC-B EC2
RY = 56                      # Region top: 8px under the 19px AWS Cloud title

# ---------------- VPC-B (top of the Region) ----------------
VB_X, VB_R = X - 222, X + 72
VB_Y = RY + 32
EY = VB_Y + 152              # EC2 centre
sg_b = EY + 24 + 16
d.group(VB_X, VB_Y, VB_R - VB_X, sg_b + 24 - VB_Y, "vpc", "VPC-B", "10.1.1.0/24")
d.text(VB_X + 32, VB_Y + 55, "(NAT 없음)", F_SUB, INK)
d.group(VB_X + 12, VB_Y + 68, VB_R - VB_X - 24, sg_b + 12 - VB_Y - 68, "private", "프라이빗 서브넷")
d.group(VB_X + 24, VB_Y + 100, VB_R - VB_X - 48, sg_b - VB_Y - 100, "sg", "보안 그룹")
d.img("service/Amazon-EC2", X - 24, EY - 24)
# the flows enter from below, so the label sits beside the icon (like every spine node)
d.side(X - 36, EY, [("EC2", "name"), ("10.1.1.10", "sub")], anchor="end")

# what happens to the A3 replies, left of the VPC-B box
NX = 48
ny = VB_Y + 70
d.text(NX, ny, "ICMP 응답: VPC-B EC2까지 도착 —", F_SUB, INK, "600")
d.text(NX, ny + LH, "ping은 다른 주소의 응답이라 무시(추론)", F_SUB, INK, "600")
d.circle(NX + BR, ny + 2 * LH + 6 - 5.5, BR, RD)
d.text(NX + BR, ny + 2 * LH + 6 + 1, "×", 20, "#FFFFFF", "700", "middle")
d.text(NX + 2 * BR + 6, ny + 2 * LH + 6, "TCP SYN-ACK: 보안 그룹이 거부(REJECT)", F_SUB, RD, "700")

# addresses seen on the VPC-B side, right of the VPC-B box
SX = VB_R + 22
sy = VB_Y + 60
d.text(SX, sy, "VPC-B 쪽에서 본 주소 (NAT 없음)", F_SUB, INK, "700")
badge_row(SX, sy + 26, "A2", G1, "10.1.1.10 → 100.64.1.10")
badge_row(SX, sy + 52, "A1", G1, "100.64.1.10 → 10.1.1.10")
badge_row(SX, sy + 78, "A3", OR, "10.1.1.10 → 172.20.N.10")
badge_row(SX, sy + 104, "A3", RD, "100.64.1.10 → 10.1.1.10 (응답)")

# ---------------- TGW row ----------------
TY = sg_b + 24 + 8 + 46       # TGW centre: its label clears the VPC-B box by 8px
vflows_up(X, EY + 28, TY - 28)
d.img("service/AWS-Transit-Gateway", X - 24, TY - 24)
d.text(X - 36, TY - 30, "Transit Gateway", F_NODE, INK, None, "end")
d.text(X - 36, TY - 9, "AS 65400", F_SUB, SUB, None, "end")

# VPC-A on the left, EC2 on the TGW's line; the A2 DNAT path is the green dashed arrow
VA_X, VA_W = 48, 210
VA_Y = TY - 124
d.group(VA_X, VA_Y, VA_W, 216, "vpc", "VPC-A", "172.20.N.0/24")
d.text(VA_X + 32, VA_Y + 55, "(온프레미스와 같음)", F_SUB, INK)
d.group(VA_X + 12, VA_Y + 68, VA_W - 24, 136, "private", "프라이빗 서브넷")
EA = VA_X + VA_W / 2
d.node("service/Amazon-EC2", EA, TY, [("EC2", "name"), ("172.20.N.10", "sub")])
d.line(X - 28, TY, EA + 28, TY, G1, dash="6,3", marker="arrowGreen")
AX = VA_X + VA_W + 22
d.text(AX, TY + 30, "VPC-A 연결 (1:1 NAT)", F_SUB, INK, "700")
d.text(AX, TY + 51, "172.20.N.0/24 → 100.64.2.0/24", F_SUB, INK)
badge_row(AX, TY + 78, "A2", G1, "DNAT 100.64.2.10 → 172.20.N.10")

# DXGW attachment labels, left of the TGW -> DXGW hop, under the VPC-A attachment
y = TY + 114
d.text(AX, y, "DXGW 연결 (1:1 NAT)", F_SUB, INK, "700")
d.text(AX, y + LH, "172.20.N.0/24 → 100.64.1.0/24", F_SUB, INK)
d.text(AX, y + 2 * LH, "SNAT: A1, A3 응답", F_SUB, SUB)
d.text(AX, y + 3 * LH, "DNAT: A1 응답, A2", F_SUB, SUB)
dx_lab_b = y + 3 * LH + 4

# TGW route table geometry (drawn last, on top)
TX = X + 28 + 30
COLS = [134, 66, 108]
TW = sum(COLS)
rows = [("CIDR", "연결", "유형", "hdr"),
        ("100.64.1.0/24", "DXGW", "system", ""), ("100.64.2.0/24", "VPC-A", "system", ""),
        ("172.20.N.0/24", "DXGW", "propagated", "hl"), ("10.1.1.0/24", "VPC-B", "propagated", "")]
table_b = TY + 18 + 36 + 34 * 4
ANN_X = TX + TW + 10
ANN_W = max(tw("← 원래 경로가", F_SUB), tw("남아 있음 (A3)", F_SUB))

# ---------------- Region bottom, DXGW, Cloud bottom ----------------
RB = max(table_b, dx_lab_b, VA_Y + 216) + 16
DY = RB + 42
CB = DY + 42
vflows_up(X, TY + 28, DY - 28)
d.img("resource/AWS-Direct-Connect_Gateway", X - 24, DY - 24)
d.side(X - 36, DY, [("Direct Connect gateway", "name"), ("AS 65300", "sub")], anchor="end")

# ---------------- on-premises (bottom band) ----------------
OT = CB + 18
M0 = OT + 149
VM, RT = 95, 522
box_r = RT + 48 + 16
d.group(16, OT, box_r - 16, 272, "onprem", "온프레미스 (Pod N)", "온프레미스 대역 172.20.N.0/24")
d.node("resource/Server", VM, M0, [("온프레미스 VM", "name"), ("vmN", "name"), ("172.20.N.10", "sub")])
d.node("resource/Amazon-VPC_Customer-Gateway", RT, M0,
       [("온프레미스", "name"), ("라우터", "name"), ("rtN", "name"), ("AS 65000", "sub")])
hflows(VM + 28, RT - 28, M0)
RX = VM + 71
d.text(RX, M0 - 88, "온프레미스에서 본 주소", F_SUB, INK, "700")
badge_row(RX, M0 - 62, "A2", G1, "10.1.1.10 → 172.20.N.10")
badge_row(RX, M0 - 36, "A1", G1, "172.20.N.10 → 10.1.1.10")
badge_row(RX, M0 + 44, "A3", OR, "10.1.1.10 → 172.20.N.10")
badge_row(RX, M0 + 70, "A3", RD, "172.20.N.10 → 10.1.1.10 (응답)")
hflows(RT + 28, X - 28, M0)
d.img("service/AWS-Direct-Connect", X - 24, M0 - 24)
d.side(X + 36, M0, [("AWS Direct Connect", "name"), ("transit VIF 2개", "sub")])
vflows_up(X, DY + 28, M0 - 28)

W = int(ANN_X + ANN_W + 8 + 16 + 16 + 0.5) + 1
H = OT + 272 + 16
d.group(32, RY, W - 64, RB - RY, "region", "아시아 태평양(서울) ap-northeast-2")
d.group(16, 16, W - 32, CB - 16, "cloud", "AWS Cloud")

# ---------------- TGW route table: on top, white background, purple dashed tie ----------------
d.line(X + 28, TY, TX, TY, PURPLE, 1.5, dash="4 3")
d.rect(TX, TY - 18, ANN_X + ANN_W + 4 - TX, table_b - (TY - 18), "#FFFFFF")
d.rect(TX, TY - 18, TW, 36, PURPLE)
d.text(TX + 10, TY + 6, "TGW 라우팅 테이블 (1:1 NAT 적용 후)", F_SUB, "#FFFFFF", "700")
ry = TY + 18
for cells in rows:
    kind = cells[3]
    h = 36 if kind == "hdr" else 34
    fill = "#EAEDED" if kind == "hdr" else "#FDEEDD" if kind == "hl" else "#FFFFFF"
    cx = TX
    for w, s in zip(COLS, cells[:3]):
        d.rect(cx, ry, w, h, fill, "#AAB7B8", 1)
        col = OR if kind == "hl" else INK
        wt = "700" if kind in ("hdr", "hl") else None
        d.text(cx + 10, ry + (23 if kind == "hdr" else 22), s, F_SUB, col, wt)
        cx += w
    if kind == "hl":
        hl_y = ry
    ry += h
d.text(ANN_X, hl_y + 13, "← 원래 경로가", F_SUB, OR, "700")
d.text(ANN_X, hl_y + 34, "남아 있음 (A3)", F_SUB, OR, "700")

open(OUT, "w").write(d.svg(W, H, markers("arrowGreen", "arrowOrange", "arrowRed")))
print(W, H, "TY", TY, "EY", EY, "RB", RB, "900px scale", round(900 / W, 3),
      "min text", round(16 * 900 / W, 2), "node", round(19 * 900 / W, 2))

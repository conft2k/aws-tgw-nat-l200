import sys
sys.path.insert(0, sys.path[0])
from lib import *

OUT = sys.argv[1]
d = D()
CON = "콘솔에서 직접"
CFN = "CloudFormation"


def tagw(s):
    return tw(s, F_TAG) + 14


def grp(nid):
    """Open a node group: the checker reads the label lines inside it as that node's own."""
    d.raw(f'<g id="node:{nid}">')


def end():
    d.raw("</g>")


def widest(lines):
    return max(tagw(s) if k == "tag" else tw(s, F_NODE if k == "name" else F_SUB) for s, k in lines)


def stack_h(lines):
    """How far below an icon's centre the last line of stack() ends."""
    y = S / 2 + 20
    for s, k in lines:
        y += 6 if k == "tag" else 0
        y += LH
    return y - LH + (1.5 if lines[-1][1] == "tag" else 4)


def stack(cx, cy, lines):
    """Icon-less label stack centred under an icon at (cx, cy); kind 'tag' draws a console chip."""
    y = cy + S / 2 + 20
    for s, k in lines:
        if k == "tag":
            y += 2
            d.tag(cx, y, s, INK, "middle")
            y += 4
        else:
            d._ln(cx, y, s, k, "middle")
        y += LH
    return y - LH + (1.5 if lines[-1][1] == "tag" else 4)   # bottom of the last line


# ---------------- what each node says ----------------
OP_TITLE = "온프레미스 (Pod N)"
VM_LINES = [("VM vmN", "name"), ("172.20.N.10", "sub")]
RT_LINES = [("라우터 rtN", "name"), ("AS 65000", "sub"), ("LAN 172.20.N.1", "sub"),
            ("Loopback1", "sub"), ("10.200.0.1/32", "sub"), ("(NAT 없음)", "sub")]
DX_LINES = [("AWS Direct Connect", "name"), ("hosted connection 2개", "sub"),
            ("(50Mbps, 콘솔에서 수락)", "sub"), ("전송 가상 인터페이스 2개", "subink"), (CON, "tag")]
DG_LINES = [("Direct Connect", "name"), ("gateway", "name"), ("AS 65300", "sub"), ("허용된 접두사:", "sub"),
            ("100.64.2.0/24,", "sub"), ("10.1.1.0/24", "sub"), (CON, "tag")]
# The TGW attachment for the DX gateway ("DXGW 연결", not the gateway association) and its 1:1 NAT rule, above the DXGW -> TGW line (bottom up)
R1_LINES = [("TGW의 DXGW 연결", "subink"), ("1:1 NAT 규칙 100:", "subink"),
            ("172.20.N.0/24", "subink"), ("→ 100.64.1.0/24", "subink")]
CW_LINES = [("Amazon CloudWatch", "name"), ("지표 (PacketsInNAT / PacketsOutNAT)", "sub"),
            ("로그 (TGW·VPC Flow Logs)", "sub"), (CFN, "tag")]

# ---------------- x tracks: on-premises | Direct Connect | Cloud: DXGW | Region: TGW | VPCs ----------------
OP_X = 16
XC = OP_X + 8 + int(widest(RT_LINES) / 2 + 1)          # VM and router column
OP_R = int(max(XC + 36 + widest(VM_LINES) + 8, OP_X + 32 + tw(OP_TITLE, F_TITLE) + 8) + 1)
DXW = widest(DX_LINES)
DXX = round(OP_R + 8 + DXW / 2)                         # Direct Connect (outside the Cloud)
CX0 = int(OP_R + 8 + DXW + 8 + 1)                       # AWS Cloud left
DGX = CX0 + 16 + int(widest(DG_LINES) / 2 + 1)          # Direct Connect gateway (Cloud, outside the Region)
R1X = DGX + 24 + 8
R1W = max(widest(R1_LINES), tagw(CON))
RX0 = int(R1X + R1W + 8 + 1)                            # Region left
TX = RX0 + 40                                           # Transit Gateway
VX = TX + 50                                            # both VPCs (left border)
VW = 336
RR = VX + VW + 16
CR = RR + 16
W = CR + 16

# ---------------- y tracks ----------------
RY0 = 56
CWX = VX + VW / 2
CW_Y = RY0 + 38 + 24                                    # CloudWatch above VPC-A
VH = 238 + LH
VA_Y = int(CW_Y + stack_h(CW_LINES) + 16 + 1)          # below CloudWatch's tag
M = VA_Y + VH + 88                                      # main line: router -> DX -> DXGW -> TGW
VB_Y = M + 68


def vpc(x, y, name, cidr, note, ec2_sub):
    d.group(x, y, VW, VH, "vpc", name, cidr)
    d.text(x + 32, y + 55, note, F_SUB, INK)
    d.tag(x + VW - 12 - tagw(CFN), y + 19, CFN, PINK)
    d.group(x + 12, y + 68, VW - 24, 158 + LH, "private", "프라이빗 서브넷")
    ey = y + 68 + 32 + 24
    ex, ix = x + 12 + 73, x + VW - 12 - 96
    grp(name.lower() + "-ec2")
    d.node("service/Amazon-EC2", ex, ey, [("EC2", "name")] + ec2_sub)
    end()
    grp(name.lower() + "-eice")
    d.node("resource/Amazon-VPC_Endpoints", ix, ey, [("EICE", "name"), ("EC2 Instance Connect", "sub"), ("Endpoint", "sub")])
    end()
    d.line(ix - 28, ey, ex + 28, ey, INK, dash="5,4", marker="arrow")
    d.text((ix + ex) / 2, ey - 8, "SSH", F_SUB, INK, None, "middle")
    return ey


# ---------------- on-premises: VM above the router, both in one column ----------------
VM_Y = M - 100
OP_Y = VM_Y - 24 - 50
grp("vm")
d.img("resource/Server", XC - 24, VM_Y - 24)
d.side(XC + 36, VM_Y, VM_LINES)
end()
d.line(XC, VM_Y + 28, XC, M - 28, INK)
grp("router")
d.img("resource/Amazon-VPC_Customer-Gateway", XC - 24, M - 24)
op_b = stack(XC, M, RT_LINES)
end()
OP_B = int(op_b + 16 + 1)
d.group(OP_X, OP_Y, OP_R - OP_X, OP_B - OP_Y, "onprem", OP_TITLE, "LAN 172.20.N.0/24")

# ---------------- two transit VIFs over the hosted connections: router -> DX location -> DXGW ----------------
for dy in (-8, 8):
    d.line(XC + 28, M + dy, DXX - 28, M + dy, INK)
    d.line(DXX + 28, M + dy, DGX - 28, M + dy, INK)
grp("dx")
d.img("service/AWS-Direct-Connect", DXX - 24, M - 24)
dx_b = stack(DXX, M, DX_LINES)
end()

# ---------------- Direct Connect gateway and its attachment to the TGW ----------------
grp("dxgw")
d.img("resource/AWS-Direct-Connect_Gateway", DGX - 24, M - 24)
dg_b = stack(DGX, M, DG_LINES)
end()
d.line(DGX + 28, M, TX - 28, M, INK)
y = M - 10
d.tag(R1X, y, CON)
for s, k in reversed(R1_LINES):
    y -= 24 if y == M - 10 else LH
    d._ln(R1X, y, s, k, None)
r1_top = y - 14

# ---------------- Transit Gateway: VPC-A up and to the right, VPC-B down and to the right ----------------
grp("tgw")
d.img("service/AWS-Transit-Gateway", TX - 24, M - 24)
d.text(TX + 36, M - 2, "Transit Gateway · AS 65400", F_NODE, INK)
d.tag(TX + 36, M + 24, CFN, PINK)
end()

ea = vpc(VX, VA_Y, "VPC-A", "172.20.N.0/24", "(온프레미스와 같은 대역)",
         [("172.20.N.10", "sub"), ("(+ 보조 IP .20)", "sub")])
d.poly([(TX + 10, M - 28), (TX + 10, ea), (VX, ea)], INK)
d.text(TX + 20, M - 62, "1:1 NAT 규칙 100:", F_SUB, INK)
d.tag(TX + 20 + tw("1:1 NAT 규칙 100:", F_SUB) + 8, M - 62, CON)
d.text(TX + 20, M - 38, "172.20.N.0/24 → 100.64.2.0/24", F_SUB, INK)

eb = vpc(VX, VB_Y, "VPC-B", "10.1.1.0/24", "(대조군, NAT 없음)", [("10.1.1.10", "sub")])
d.poly([(TX + 10, M + 28), (TX + 10, eb), (VX, eb)], INK)
d.text(TX + 20, M + 54, "NAT 없음", F_SUB, INK)

# ---------------- regional service above VPC-A ----------------
grp("cloudwatch")
d.img("service/Amazon-CloudWatch", CWX - 24, CW_Y - 24)
cw_b = stack(CWX, CW_Y, CW_LINES)
end()
assert cw_b + 16 <= VA_Y, (cw_b, VA_Y)

# ---------------- containers (bottom of the z-order) ----------------
RB = VB_Y + VH + 16
CB = int(max(RB, dg_b + 8) + 16)
H = int(max(CB, dx_b + 8, OP_B) + 16)
n0 = len(d.el)
d.group(CX0, 16, CR - CX0, CB - 16, "cloud", "AWS Cloud")
d.group(RX0, RY0, RR - RX0, RB - RY0, "region", "아시아 태평양(서울) ap-northeast-2")
d.el = d.el[n0:] + d.el[:n0]

# ---------------- TGW route table: on top, white background, dashed purple link up from the TGW ----------------
COLS = [int(tw(s, F_SUB) + 19 + 1) for s in ("100.64.1.0/24", "VPC-A", "propagated")]
TW_ = sum(COLS)
TR = TX - 4                       # right edge, clear of the VPC-A line at TX + 10
TL = TR - TW_
HDR = 58
rows = [("CIDR", "연결", "유형"), ("100.64.1.0/24", "DXGW", "system"), ("100.64.2.0/24", "VPC-A", "system"),
        ("172.20.N.0/24", "DXGW", "propagated"), ("10.200.0.1/32", "DXGW", "propagated"),
        ("10.1.1.0/24", "VPC-B", "propagated")]
TABLE_H = HDR + 36 + 34 * (len(rows) - 1)
TB = int(r1_top - 8)
TT = TB - TABLE_H
print("table left", TL, "cloud left", CX0)
assert TT >= RY0 + 34, TT
d.line(TX - 10, M - 28, TX - 10, TB, PURPLE, 1.5, dash="4 3")
d.rect(TL, TT, TW_, TABLE_H, "#FFFFFF")
d.rect(TL, TT, TW_, HDR, PURPLE)
d.rect(TL + 6, TT + 7, 26, 26, "#FFFFFF")
d.img("resource/Amazon-Route-53_Route-Table", TL + 7, TT + 8, 24)
d.text(TL + 40, TT + 24, "TGW 라우팅 테이블", F_SUB, "#FFFFFF", "700")
d.text(TL + 40, TT + 46, "(1:1 NAT 적용 후)", F_SUB, "#FFFFFF")
ry = TT + HDR
for i, cells in enumerate(rows):
    h = 36 if i == 0 else 34
    cx = TL
    for w, s in zip(COLS, cells):
        d.rect(cx, ry, w, h, "#F2F3F3" if i == 0 else "#FFFFFF", "#879196", 1)
        d.text(cx + 10, ry + (23 if i == 0 else 22), s, F_SUB, INK, "600" if i == 0 else None)
        cx += w
    ry += h
d.rect(TL, TT, TW_, TABLE_H, "none", PURPLE, 1.5)   # outline: the dashed link ends on it

open(OUT, "w").write(d.svg(W, H, markers("arrow")))
print(W, H, "M", M, "TX", TX, "table", (TL, TT, TW_, TABLE_H), "W900 scale", round(900 / W, 3),
      "min", round(min(F_SUB, F_TAG) * 900 / W, 2))

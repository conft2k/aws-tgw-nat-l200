import sys
sys.path.insert(0, sys.path[0])
from lib import *

OUT = sys.argv[1]
d = D()
CON = "콘솔에서 직접"
CFN = "CloudFormation"

# ---------------- left column: on-premises (top) -> two transit VIFs (down) -> Direct Connect ----------------
IX = 56                      # x of the VM / router / DX icons
VM_Y, RT_Y = 94, 182
OP_W, OP_H = 306, 220
d.group(16, 16, OP_W, OP_H, "onprem", "온프레미스 (내 Pod N)", "LAN 172.20.N.0/24")
d.img("resource/Server", IX - 24, VM_Y - 24)
d.text(IX + 36, VM_Y + 6, "VM vmN · 172.20.N.10", F_NODE, INK)
d.line(IX, VM_Y + 28, IX, RT_Y - 28, INK)
d.img("resource/Amazon-VPC_Customer-Gateway", IX - 24, RT_Y - 24)
d.side(IX + 36, RT_Y, [("라우터 rtN · AS 65000", "name"), ("LAN 172.20.N.1", "sub"),
                       ("Loopback1 10.200.0.1/32", "sub"), ("(NAT 없음)", "sub")])

# VIF labels to the right of the two vertical lines
VL = IX + 20
y = 16 + OP_H + 22
d.text(VL, y, "전송 가상 인터페이스 1", F_SUB, INK)
d.text(VL, y + LH, "(VLAN은 hosted", F_SUB, SUB)
d.text(VL, y + 2 * LH, "connection 1의 값)", F_SUB, SUB)
d.tag(VL, y + 3 * LH + 3, CON)
y2 = y + 3 * LH + 3 + 32
d.text(VL, y2, "전송 가상 인터페이스 2", F_SUB, INK)
d.tag(VL, y2 + LH + 3, CON)
vif_b = y2 + LH + 3 + 6

# ---------------- geometry of the AWS side ----------------
CX0 = 340                    # AWS Cloud left
RX0 = CX0 + 16               # Region left
TL = 88                      # route table left
COLS = [134, 68, 110]
TW = sum(COLS)
TX = TL + TW + 28 + 24       # TGW centre x (dashed link 28px)
VW = 352
VH = 238 + LH

RY0 = 56                     # Region top
VB_X, VB_Y = RX0 + 16, RY0 + 38    # VPC-B above the TGW
TY = max(vif_b + 8 + 18, VB_Y + VH + 8 + 56)
TABLE_H = 36 + 36 + 5 * 34
table_b = TY - 18 + TABLE_H
DY = table_b + 14            # main line: DX -> DXGW
VA_X = TX + 28 + 12 + 274 + 4

# ---------------- Direct Connect (outside the Cloud) ----------------
d.line(IX - 8, RT_Y + 28, IX - 8, DY - 28, INK)
d.line(IX + 8, RT_Y + 28, IX + 8, DY - 28, INK)
d.img("service/AWS-Direct-Connect", IX - 24, DY - 24)
d.text(IX - 24, DY + 48, "AWS Direct Connect", F_NODE, INK)
d.text(IX - 24, DY + 48 + LH, "hosted connection 2개 · 50Mbps", F_SUB, SUB)
_, e = d.tag(IX - 24, DY + 48 + 2 * LH + 3, CON)
d.text(e + 8, DY + 48 + 2 * LH + 3, "수락", F_SUB, SUB)
dx_b = DY + 48 + 2 * LH + 3 + 6

# ---------------- Direct Connect gateway (Cloud, outside the Region) ----------------
d.line(IX + 28, DY, TX - 28, DY, INK)
d.img("resource/AWS-Direct-Connect_Gateway", TX - 24, DY - 24)
gx = TX + 36
gy = DY - 36
d.text(gx, gy, "Direct Connect gateway", F_NODE, INK)
d.text(gx, gy + LH, "AS 65300", F_SUB, SUB)
d.text(gx, gy + 2 * LH, "허용된 접두사:", F_SUB, SUB)
d.text(gx, gy + 3 * LH, "100.64.2.0/24, 10.1.1.0/24", F_SUB, SUB)
d.tag(gx, gy + 4 * LH + 3, CON)
dxgw_top = gy - 15
dxgw_b = gy + 4 * LH + 3 + 6

# ---------------- Transit Gateway ----------------
d.line(TX, DY - 28, TX, TY + 28, INK)
d.img("service/AWS-Transit-Gateway", TX - 24, TY - 24)
ly = TY + 30
d.text(TX + 36, ly, "Transit Gateway · AS 65400", F_NODE, INK)
d.tag(TX + 36, ly + 24, CFN, PINK)
lx = TX + 12
# DXGW attachment (gateway association) with its 1:1 NAT rule, beside the DXGW -> TGW hop
y = ly + 24 + 34
d.text(lx, y, "1:1 NAT 규칙 100:", F_SUB, INK)
d.tag(lx + tw("1:1 NAT 규칙 100:", F_SUB) + 8, y, CON)
d.text(lx, y + LH + 2, "172.20.N.0/24 → 100.64.1.0/24", F_SUB, INK)
d.text(lx, y + 2 * LH + 8, "게이트웨이 연결", F_SUB, SUB)
d.tag(lx + tw("게이트웨이 연결", F_SUB) + 8, y + 2 * LH + 8, CON)
att_b = y + 2 * LH + 8 + 6


def vpc(x, y, name, cidr, note, ec2_sub):
    d.group(x, y, VW, VH, "vpc", name, cidr)
    d.text(x + 32, y + 55, note, F_SUB, INK)
    d.tag(x + VW - 12 - tw(CFN, F_TAG) - 14, y + 19, CFN, PINK)
    d.group(x + 12, y + 68, VW - 24, 158 + LH, "private", "프라이빗 서브넷")
    ey = y + 68 + 32 + 24
    ex, ix = x + 12 + 73, x + VW - 12 - 98
    d.node("service/Amazon-EC2", ex, ey, [("EC2", "name")] + ec2_sub)
    d.node("resource/Amazon-VPC_Endpoints", ix, ey, [("EICE", "name"), ("EC2 Instance Connect", "sub")])
    d.line(ix - 28, ey, ex + 28, ey, INK, dash="5,4", marker="arrow")
    d.text((ix + ex) / 2, ey - 8, "SSH", F_SUB, INK, None, "middle")
    return ey


# VPC-B above the TGW, attached straight up (no NAT)
vpc(VB_X, VB_Y, "VPC-B", "10.1.1.0/24", "(대조군, NAT 없음)", [("10.1.1.10", "sub")])
d.line(TX, VB_Y + VH, TX, TY - 28, INK)
d.text(TX - 12, (VB_Y + VH + TY - 24) / 2 + 6, "NAT 없음", F_SUB, INK, None, "end")

# VPC-A right of the TGW, on the TGW's line; its 1:1 NAT rule above the attachment
VA_Y = TY - 124
vpc(VA_X, VA_Y, "VPC-A", "172.20.N.0/24", "(온프레미스와 같은 대역)",
    [("172.20.N.10", "sub"), ("(+ 보조 IP .20)", "sub")])
d.line(TX + 28, TY, VA_X, TY, INK)
AX = TX + 28 + 12
d.text(AX, TY - 32, "1:1 NAT 규칙 100:", F_SUB, INK)
d.tag(AX + tw("1:1 NAT 규칙 100:", F_SUB) + 8, TY - 32, CON)
d.text(AX, TY - 9, "172.20.N.0/24 → 100.64.2.0/24", F_SUB, INK)

# regional service above VPC-A
CWX = VA_X + VW / 2
cwy = VB_Y + 32
d.node("service/Amazon-CloudWatch", CWX, cwy,
       [("Amazon CloudWatch", "name"), ("지표 (PacketsInNAT / PacketsOutNAT)", "sub"), ("로그 (TGW·VPC Flow Logs)", "sub")])
d.tag(CWX, cwy + 24 + 20 + 3 * LH + 2, CFN, PINK, "middle")

RR = VA_X + VW + 16
W = RR + 16 + 16
RB = max(att_b + 8, VA_Y + VH + 16)
assert RB <= dxgw_top - 8, (RB, dxgw_top)
CB = max(dxgw_b, dx_b) + 12
H = CB + 16
n0 = len(d.el)
d.group(CX0, 16, W - 16 - CX0, CB - 16, "cloud", "AWS Cloud")
d.group(RX0, RY0, RR - RX0, RB - RY0, "region", "아시아 태평양(서울) ap-northeast-2")
d.el = d.el[n0:] + d.el[:n0]   # containers first (bottom of the z-order)

# ---------------- TGW route table: on top, white background, dashed purple link to the TGW ----------------
d.line(TL + TW, TY, TX - 28, TY, PURPLE, 1.5, dash="4,3")
d.rect(TL, TY - 18, TW, TABLE_H, "#FFFFFF")
d.rect(TL, TY - 18, TW, 36, PURPLE)
d.text(TL + 10, TY + 6, "TGW 라우팅 테이블 (1:1 NAT 적용 후)", F_SUB, "#FFFFFF", "600")
rows = [("CIDR", "연결", "유형"), ("100.64.1.0/24", "DXGW", "system"), ("100.64.2.0/24", "VPC-A", "system"),
        ("172.20.N.0/24", "DXGW", "propagated"), ("10.200.0.1/32", "DXGW", "propagated"),
        ("10.1.1.0/24", "VPC-B", "propagated")]
ry = TY + 18
for i, cells in enumerate(rows):
    h = 36 if i == 0 else 34
    cx = TL
    for w, s in zip(COLS, cells):
        d.rect(cx, ry, w, h, "#F2F3F3" if i == 0 else "#FFFFFF", "#879196", 1)
        d.text(cx + 10, ry + (23 if i == 0 else 22), s, F_SUB, INK, "600" if i == 0 else None)
        cx += w
    ry += h

open(OUT, "w").write(d.svg(W, H, markers("arrow")))
print(W, H, "TY", TY, "DY", DY, "RB", RB, "dxgw_top", dxgw_top, "W900 scale", round(900 / W, 3), "min", round(16 * 900 / W, 2))

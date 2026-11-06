"""observed-loss-location, on-premises on the left: VM -> router -> DX -> DXGW -> TGW -> VPC-A EC2.
The lost AWS -> on-premises flow runs right to left (black), the delivered return left to right (green)."""
import sys
from dg import D, L, M, S, INK, tw, marker

OUT = sys.argv[1]
d = D()
GREEN, RED, GREY = "#1D8102", "#D13212", "#7D8998"
h = S / 2

d.text(8, 30, "사전 테스트에서 관찰(2026-11-03): NAT system routes 끔 + 원래 대역 광고 중단", 20, weight="700")

# ---- x grid (left -> right) ---------------------------------------------------
OP_X = 8
vm_half = tw("온프레미스 VM", L) / 2
r_half = tw("Loopback1 10.200.0.1/32", M) / 2
vmx = round(OP_X + 9 + vm_half)
rtx = round(vmx + vm_half + 8 + r_half)
OP_R = round(rtx + r_half + 9)
dx_half = tw("transit VIF 2개", M) / 2
dxx = round(OP_R + 9 + dx_half)
CL_X = round(dxx + dx_half + 9)
RG_X = CL_X + 236
gwx = (CL_X + RG_X) / 2
tgx = RG_X + 93
lead1 = tgx - 80                         # evidence 1 leader, between the Region border and block A
blockA_l = tgx - 72                      # block A sits above the TGW
VPC_X = round(tgx + tw("Transit Gateway", L) / 2 + 9)
VPC_W = 206
SUB_X, SUB_W = VPC_X + 10, VPC_W - 20
ec2x = SUB_X + SUB_W / 2
RG_R = VPC_X + VPC_W + 10
CL_R = RG_R + 10
W = CL_R + 8

# ---- y grid -----------------------------------------------------------------
CL_Y = 48
RG_Y = CL_Y + 36
EV1_Y, EV1_H = RG_Y + 36, 96
cy = EV1_Y + EV1_H + 8 + 110             # VPC box top (cy - 110) sits under evidence 1
fy, ry = cy - 8, cy + 8                  # lost AWS -> on-prem line / delivered return line
VPC_Y = cy - 110
SUB_Y = VPC_Y + 52
VPC_B = cy + 108

# TGW route table: right under the TGW label, as far left as the red loss caption allows,
# below the EC2 captions (glyph bottom cy + 88) that it would otherwise cover.
TB_COLS = [("CIDR", 132), ("연결", 64), ("유형", 106)]
TB_W = sum(w for _, w in TB_COLS)
loss_r = gwx + tw("이 구간 어딘가에서 사라짐", M) / 2
TB_X = round(max(loss_r + 8, RG_X + 8))
TB_Y = cy + 96
TB_B = TB_Y + 38 + 34 * 4
RG_B = TB_B + 10
CL_B = RG_B + 10
H = CL_B + 16

# ---- containers -------------------------------------------------------------
d.cloud(CL_X, CL_Y, CL_R - CL_X, CL_B - CL_Y)
d.group("region", RG_X, RG_Y, RG_R - RG_X, RG_B - RG_Y, "아시아 태평양(서울) ap-northeast-2")
d.group("vpc", VPC_X, VPC_Y, VPC_W, VPC_B - VPC_Y, "VPC-A", "172.20.N.0/24")
d.group("private", SUB_X, SUB_Y, SUB_W, VPC_B - 10 - SUB_Y, "프라이빗 서브넷")

# loss span: router inbound <- ... <- TGW DXGW-attachment egress
d.rect(rtx + h, cy - 12, (tgx - h) - (rtx + h), 24, fill="#FADBD8")

# ---- evidence 1: TGW -> DXGW attachment metrics -------------------------------
ex = lead1 - 6
d.rect(ex, EV1_Y, 254, EV1_H, fill="#FFFFFF", stroke=GREY, sw=1, rx=4)
for i, (s, wt) in enumerate([("TGW → DXGW 연결", "600"), ("PacketsOut = PacketsOutNAT", None),
                             ("평소와 같음 ≈ 분당 580,", None), ("TGW 폐기 지표 없음", None)]):
    d.text(ex + 10, EV1_Y + 22 + 20 * i, s, M, weight=wt)
d.line(lead1, EV1_Y + EV1_H, lead1, fy - 3, stroke=GREY, sw=1, dash="3,2")
d.circle(lead1, fy, 3, GREY)

# ---- block A: VPC-A attachment SNAT (above the TGW) --------------------------
ax = blockA_l + tw("출발지 주소 바꾸기", M) / 2
for i, s in enumerate(["VPC-A 연결", "출발지 주소 바꾸기", "→ 100.64.2.10"]):
    d.text(ax, cy - 36 - 20 * (2 - i), s, M, anchor="middle")

# ---- block B: DXGW attachment (above the Direct Connect gateway) -------------
ys = [0, 20, 46, 66, 86, 112, 132]
lines_b = ["DXGW 연결 ·", "NAT system routes 끔", "1:1 NAT 규칙", "172.20.N.0/24", "→ 100.64.1.0/24",
           "나갈 때 목적지 주소", "되돌리기 → 172.20.N.10"]
y0 = cy - 36 - ys[-1]
for dy, s in zip(ys, lines_b):
    d.text(gwx, y0 + dy, s, M, anchor="middle")

# ---- on-premises (left) ---------------------------------------------------------
d.group("onprem", OP_X, CL_Y, OP_R - OP_X, 0, "온프레미스(Pod N)", "온프레미스 대역 172.20.N.0/24")
op_rect = len(d.out) - 4
EV3_Y = CL_Y + 52
e3w = 162
e3x = OP_X + 9
d.rect(e3x, EV3_Y, e3w, 56, fill="#FFFFFF", stroke=GREY, sw=1, rx=4)
d.text(e3x + 10, EV3_Y + 22, "온프레미스 VM vmN", M, weight="600")
d.text(e3x + 10, EV3_Y + 42, "tcpdump: 0개", M, fill=RED, weight="600")
d.line(vmx, EV3_Y + 56, vmx, cy - h - 3, stroke=GREY, sw=1, dash="3,2")

EV2_Y = EV3_Y + 56 + 8
e2w = 192
e2x = OP_R - 9 - e2w
assert e2x > vmx + 8, "evidence 2 would sit on the VM leader"
lead2 = rtx + h + 18
d.rect(e2x, EV2_Y, e2w, 118, fill="#FFFFFF", stroke=GREY, sw=1, rx=4)
for i, (s, c) in enumerate([("온프레미스 라우터 rtN", INK), ("VIF 서브인터페이스", INK), ("인바운드 ACL 카운터", RED),
                            ("(받은 패킷 수):", RED), ("손실 중 증가 0", RED)]):
    d.text(e2x + 10, EV2_Y + 22 + 20 * i, s, M, fill=c, weight="600")
d.line(lead2, EV2_Y + 118, lead2, fy - 3, stroke=GREY, sw=1, dash="3,2")
d.circle(lead2, fy, 3, GREY)
assert EV2_Y + 118 + 8 <= cy - h, "evidence 2 runs into the router"

# ---- nodes --------------------------------------------------------------------
d.node("resource/Server", vmx, cy, [("온프레미스 VM", L), ("vmN", L), ("172.20.N.10", M)])
rb = d.node("resource/Amazon-VPC_Customer-Gateway", rtx, cy,
            [("온프레미스 라우터", L), ("rtN", L), ("광고: 100.64.1.0/24", M), ("(Null0)", M),
             ("Loopback1 10.200.0.1/32", M), ("172.20.N.0/24 광고 중단", M, RED, "600")])
OP_B = rb + 4 + 10
d.out[op_rect] = d.out[op_rect].replace('height="0"', f'height="{OP_B - CL_Y:g}"')
d.node("service/AWS-Direct-Connect", dxx, cy, [("AWS Direct", L), ("Connect", L), ("transit VIF 2개", M)])
d.node("resource/AWS-Direct-Connect_Gateway", gwx, cy, [("Direct Connect gateway", L)])
d.text(gwx, cy + 80, "이 구간 어딘가에서 사라짐", M, fill=RED, weight="700", anchor="middle")
d.text(gwx, cy + 100, "(정확한 위치는 모름)", M, fill=RED, weight="700", anchor="middle")
d.node("service/AWS-Transit-Gateway", tgx, cy, [("Transit Gateway", L)])
d.image("service/Amazon-EC2", ec2x - h, cy - h, S)
d.text(ec2x, cy + 44, "EC2", L, anchor="middle")
d.text(ec2x, cy + 64, "172.20.N.10", M, anchor="middle")
d.text(ec2x, cy + 84, "ping → 100.64.1.10", M, anchor="middle")

# ---- AWS -> on-premises (y = cy - 8), right to left ---------------------------
d.line(ec2x - h - 4, fy, tgx + h + 4, fy, marker="arrow")
for a, b in ((tgx, gwx), (gwx, dxx), (dxx, rtx)):
    d.line(a - h - 4, fy, b + h + 4, fy, dash="5,4", marker="arrow")
d.line(rtx - h - 4, fy, vmx + h + 4, fy, stroke=GREY, dash="5,4", marker="arrowGrey")

# ---- on-premises -> AWS (y = cy + 8), left to right, delivered ----------------
for a, b in ((vmx, rtx), (rtx, dxx), (dxx, gwx), (gwx, tgx), (tgx, ec2x)):
    d.line(a + h, ry, b - h - 4, ry, stroke=GREEN, sw=1, dash="5,3", marker="arrowGreen")
d.text((rtx + vmx) / 2, cy + 24, "전달됨", M, fill=GREEN, weight="600", anchor="middle")

# ---- TGW route table: last (top z-order), white backing hides the borders under it
d.line(tgx, cy + 54, tgx, TB_Y, stroke="#8C4FFF", sw=1.5, dash="4,3")
d.rect(TB_X - 2, TB_Y - 2, TB_W + 4, TB_B - TB_Y + 4, fill="#FFFFFF")
d.rect(TB_X, TB_Y, TB_W, 38, fill="#8C4FFF", stroke="#8C4FFF", sw=1)
d.rect(TB_X + 6, TB_Y + 6, 26, 26, fill="#FFFFFF")
d.image("resource/Amazon-Route-53_Route-Table", TB_X + 7, TB_Y + 7, 24)
d.text(TB_X + 40, TB_Y + 24, "TGW 라우팅 테이블", L, fill="#FFFFFF", weight="700")
y = TB_Y + 38
for row, bg, wt in [(["CIDR", "연결", "유형"], "#F2F3F3", "600"),
                    (["100.64.1.0/24", "DXGW", "propagated"], "#FFFFFF", None),
                    (["100.64.2.0/24", "VPC-A", "system"], "#FFFFFF", None)]:
    x = TB_X
    for s, (_, w) in zip(row, TB_COLS):
        d.rect(x, y, w, 34, fill=bg, stroke="#AAB7B8", sw=1)
        d.text(x + 9, y + 21, s, M, weight=wt)
        x += w
    y += 34
d.rect(TB_X, y, TB_W, 34, fill="#FDF3F2", stroke="#AAB7B8", sw=1)
d.text(TB_X + 9, y + 21, "172.20.N.0/24 — 경로 없음", M, fill=RED, weight="600")

print("canvas", W, H, "table", TB_X, TB_Y, "tgw", tgx, file=sys.stderr)
defs = marker("arrow", INK) + marker("arrowGrey", GREY) + marker("arrowGreen", GREEN)
open(OUT, "w").write(d.svg(W, H, defs))

"""extra-c-observability: on-premises band at the bottom-left, chain DX -> DXGW -> TGW -> TGW ENI -> EC2 upward."""
import sys
sys.path.insert(0, sys.path[0])
from lib import *

d = D()
OUT = sys.argv[1]
GRN = "#1D8102"
LEAD = "#7D8998"


def node_above(ref, cx, cy, lines):
    """Icon centred on (cx, cy) with its label lines stacked above it."""
    d.img(ref, cx - S / 2, cy - S / 2)
    y = cy - S / 2 - 12 - (len(lines) - 1) * LH
    for s, kind in lines:
        d._ln(cx, y, s, kind, "middle")
        y += LH


def metric_box(x, y, title, rows, lead_y, chain_x):
    lines = [(title, "700")]
    for name, desc1, desc2 in rows:
        lines += [(name, "600"), (desc1, None), (desc2, None)]
    w = max(tw(s, F_SUB) for s, _ in lines) + 28
    h = 22 + LH * (len(lines) - 1) + 16
    d.rect(x, y, w, h, "none", LEAD, 1, rx=4)  # unfilled: the checker reads it as the leader's end
    yy = y + 26
    for s, wt in lines:
        d.text(x + 14, yy, s, F_SUB, INK if wt else SUB, wt)
        yy += LH
    d.line(x, lead_y, chain_x + 11, lead_y, LEAD, 1, dash="3,2")
    d.circle(chain_x + 8, lead_y, 3, LEAD)
    return w, h


X = 668                       # chain column: EC2, TGW ENI, TGW, DXGW, DX
C1, C2 = 160, 352             # left columns: CloudWatch Logs / TGW Flow Logs, VPC Flow Logs
VB_X = 430                    # VPC-B column


def pair(y_low, y_high):
    """Request up on the right (X+8), response down on the left (X-8)."""
    d.line(X + 8, y_low, X + 8, y_high, INK, marker="arrow")
    d.line(X - 8, y_high, X - 8, y_low, GRN, dash="6,3", marker="arrowGreen")


CLOUD_Y = 16
RY = CLOUD_Y + 40             # Region top

# ---------------- top row: VPC-A (app subnet over TGW subnet) ----------------
# Subnet titles and CIDRs end left of the chain, so the ENI -> EC2 hop clears the TGW subnet header.
SUB_L = X - 14 - 4 - max(32 + tw("172.20.N.224/28", F_SUB), 32 + tw("프라이빗 서브넷", F_TITLE))
VA_X, VA_Y = SUB_L - 12, RY + 36
VA_R = X + 166                # VPC-A right: node labels sit right of the chain icons
SY = VA_Y + 50                # app subnet top
EY = SY + 74                  # EC2 centre
SY2 = EY + 52                 # TGW subnet top
NY = SY2 + 74                 # TGW ENI centre
VB = NY + 52                  # VPC-A bottom
FY = EY                       # VPC Flow Logs / CloudWatch Logs row
d.group(VA_X, VA_Y, VA_R - VA_X, VB - VA_Y, "vpc", "VPC-A", "172.20.N.0/24")
d.group(SUB_L, SY, VA_R - 12 - SUB_L, EY + 40 - SY, "private", "프라이빗 서브넷", "172.20.N.0/26")
d.group(SUB_L, SY2, VA_R - 12 - SUB_L, NY + 40 - SY2, "private", "TGW 서브넷", "172.20.N.224/28")
d.img("service/Amazon-EC2", X - S / 2, EY - S / 2)
d.side(X + 36, EY, [("EC2", "name"), ("172.20.N.10", "sub")])
d.img("resource/Amazon-VPC_Elastic-Network-Interface", X - S / 2, NY - S / 2)
d.side(X + 36, NY, [("TGW ENI", "name"), ("172.20.N.234", "sub"), ("(예시 주소)", "sub")])
pair(NY - 28, EY + 28)

# VPC Flow Logs (left of VPC-A, on the EC2 row) records at both ENIs: its leader forks down to the TGW ENI
node_above("resource/Amazon-VPC_Flow-Logs", C2, FY,
           [("VPC Flow Logs", "name"), ("direction = ENI 기준", "sub"),
            ("EC2 ENI에서 본 출발지", "sub"), ("pkt-srcaddr 100.64.1.10", "bold")])
FK = (C2 + 28 + VA_X) // 2    # leader fork, between VPC Flow Logs and the VPC-A border
d.line(C2 + 28, EY, X - 30, EY, LEAD, 1, dash="3,2")
d.poly([(FK, EY), (FK, NY), (X - 30, NY)], LEAD, 1, dash="3,2")
for yy in (EY, NY):
    d.circle(X - 30, yy, 3, LEAD)
node_above("resource/Amazon-CloudWatch_Logs", C1, FY, [("CloudWatch Logs", "name"), ("Log Analytics로 조회", "sub")])
d.line(C2 - 28, FY, C1 + 28, FY, LEAD, 1.5, dash="5,4", marker="arrowGrey")

# CloudWatch (metrics) at the top right, above the VPC-A attachment metrics
BX2 = VA_R + 12
W2 = max(tw(s, F_SUB) for s in ("= 들어올 때 출발지 주소", "= 나갈 때 목적지 주소")) + 28
CW_LINES = [("Amazon CloudWatch", "name"), ("NAT 지표 (Sum, 1분)", "sub"), ("두 NAT 연결의 값이 같음", "bold"),
            ("In/Out = TGW 기준", "sub")]
CW_HALF = max(tw(s, F_NODE if k == "name" else F_SUB) for s, k in CW_LINES) / 2
CW_X = max(BX2 + W2 / 2, VA_R + 16 + CW_HALF)
d.node("service/Amazon-CloudWatch", CW_X, VA_Y + 24, CW_LINES)
cw_bottom = VA_Y + 24 + 24 + 20 + 3 * LH + 4

# VPC-A attachment metrics, leader just below VPC-A
lead2 = VB + 16
B2 = max(cw_bottom + 10, lead2 + 24 - (22 + LH * 6 + 16))
w2, h2 = metric_box(BX2, B2, "VPC-A 연결 지표",
                    [("PacketsInNAT", "= 들어올 때 출발지 주소", "바꾸기(SNAT) · 응답"),
                     ("PacketsOutNAT", "= 나갈 때 목적지 주소", "되돌리기(DNAT) · 요청")], lead2, X)

# request / response on the TGW -> TGW ENI -> EC2 hops (left of the pair)
d.text(X - 22, VB + 30, "요청 100.64.1.10 → 172.20.N.10", F_SUB, INK, "600", "end")
d.text(X - 22, VB + 51, "응답 172.20.N.10 → 100.64.1.10", F_SUB, GRN, "600", "end")

TY = max(VB + 91, B2 + h2 + 32)
pair(TY - 28, NY + 28)
d.img("service/AWS-Transit-Gateway", X - 24, TY - 24)
d.side(X + 36, TY, [("Transit Gateway", "name"), ("AS 65400", "sub")])

# TGW Flow Logs on the TGW's left, arrow up to CloudWatch Logs
d.line(X - 28, TY, C1 + 28, TY, LEAD, 1, dash="3,2")
tfl_last = d.node("resource/Amazon-VPC_Flow-Logs", C1, TY,
                  [("TGW Flow Logs", "name"), ("설정은 Transit Gateway 1개", "sub"), ("기록은 연결·방향별", "sub"),
                   ("사전 테스트에서 관찰한 기록:", "sub"), ("172.20.N.10 → 172.20.N.10", "bold"),
                   ("출발지는 바꾸기 전,", "sub"), ("목적지는 되돌린 후", "sub")])
d.line(C1, TY - 28, C1, FY + 28, LEAD, 1.5, dash="5,4", marker="arrowGrey")

# VPC-B on its attachment, below the TGW row
VBY = TY + 126
d.poly([(X - 28, TY + 14), (VB_X, TY + 14), (VB_X, VBY - 28)])
vb_last = d.node("service/Amazon-Virtual-Private-Cloud", VB_X, VBY,
                 [("VPC-B", "name"), ("10.1.1.0/24", "sub"), ("VPC-B 연결: NAT 지표 0", "bold")])

# DXGW attachment metrics between TGW and DXGW
B1 = TY + 40
w1, h1 = metric_box(X + 52, B1, "DXGW 연결 지표",
                    [("PacketsInNAT", "= 들어올 때 출발지 주소", "바꾸기(SNAT) · 요청"),
                     ("PacketsOutNAT", "= 나갈 때 목적지 주소", "되돌리기(DNAT) · 응답")], B1 + 40, X)

RB = max(tfl_last + 4, vb_last + 4, B1 + h1) + 16          # Region bottom
DY = RB + 42                                             # DXGW centre
pair(DY - 28, TY + 28)
d.img("resource/AWS-Direct-Connect_Gateway", X - 24, DY - 24)
d.side(X - 36, DY, [("Direct Connect gateway", "name"), ("AS 65300", "sub")], anchor="end")
CB = DY + 42                                             # Cloud bottom

# ---------------- bottom band: on-premises -> Direct Connect ----------------
OY = CB + 26                                             # on-prem box top
M0 = OY + 84
VM, RT = 95, 478
box_r = RT + 81 + 16
d.group(16, OY, box_r - 16, 186, "onprem", "온프레미스 (Pod N)", "온프레미스 대역 172.20.N.0/24")
d.node("resource/Server", VM, M0, [("온프레미스 VM", "name"), ("vmN", "name"), ("172.20.N.10", "sub")])
d.node("resource/Amazon-VPC_Customer-Gateway", RT, M0, [("온프레미스 라우터", "name"), ("rtN", "name"), ("AS 65000", "sub")])
d.line(VM + 28, M0 - 8, RT - 28, M0 - 8, INK, marker="arrow")
d.line(RT - 28, M0 + 8, VM + 28, M0 + 8, GRN, dash="6,3", marker="arrowGreen")
d.text(VM + 74, M0 - 16, "요청 172.20.N.10 → 100.64.2.10", F_SUB, INK, "600")
d.text(VM + 74, M0 + 24, "응답 100.64.2.10 → 172.20.N.10", F_SUB, GRN, "600")
d.line(RT + 28, M0 - 8, X - 28, M0 - 8, INK, marker="arrow")
d.line(X - 28, M0 + 8, RT + 28, M0 + 8, GRN, dash="6,3", marker="arrowGreen")
d.img("service/AWS-Direct-Connect", X - 24, M0 - 24)
d.side(X + 36, M0, [("AWS Direct Connect", "name"), ("transit VIF 2개", "sub")])
pair(M0 - 28, DY + 28)

H = OY + 186 + 16
RR = max(BX2 + w2, X + 52 + w1, CW_X + CW_HALF) + 16      # Region right
W = RR + 32
d.group(32, RY, RR - 32, RB - RY, "region", "아시아 태평양(서울) ap-northeast-2")
d.group(16, CLOUD_Y, W - 32, CB - CLOUD_Y, "cloud", "AWS Cloud")

open(OUT, "w").write(d.svg(W, H, markers("arrow", "arrowGreen", "arrowGrey")))
print(W, H, "TY", TY, "EY", EY, "NY", NY, "DY", DY, "w", w1, w2, "min px@900:", round(F_SUB * 900 / W, 2))

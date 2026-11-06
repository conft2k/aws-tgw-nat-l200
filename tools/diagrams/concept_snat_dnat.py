"""Generate docs/images/diagrams/concept-snat-dnat.draft.svg (layout source)."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/.claude/skills/skill-aws-arch-diagram/scripts"))
from check_layout import text_width as tw

OUT = sys.argv[1]
L, s, CL = 18.5, 16, 19.5          # node/container labels, secondary, AWS Cloud title
S = 52                             # node icon size
INK, GREY, TEAL, ORANGE = "#232F3E", "#7D8998", "#00A4A6", "#C7511F"
m = 12
P_L, P_s = 22, 21                  # line pitch

el = []
def T(x, y, txt, fs, anchor=None, bold=False, fill=INK):
    a = f' text-anchor="{anchor}"' if anchor else ""
    b = ' font-weight="600"' if bold else ""
    el.append(f'  <text x="{x:g}" y="{y:g}" font-size="{fs:g}"{b}{a} fill="{fill}">{txt}</text>')
def R(x, y, w, h, stroke, sw=2, dash=None, fill="none", rx=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    r = f' rx="{rx}"' if rx else ""
    el.append(f'  <rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{r}/>')
def I(ref, x, y, size=S):
    el.append(f'  <image href="bundle:{ref}" x="{x:g}" y="{y:g}" width="{size}" height="{size}"/>')
def node(ref, cx, cy, lines):
    I(ref, cx - S / 2, cy - S / 2)
    y = cy + S / 2 + 22
    for txt, fs, bold in lines:
        T(cx, y, txt, fs, "middle", bold)
        y += P_L if fs == L else P_s
    return y
def w(lines):
    return max(tw(t, fs) for t, fs, _ in lines)

# ---- label sets
VM = [("온프레미스 VM", L, False), ("vmN", L, False), ("172.20.N.10", s, False)]
RT = [("온프레미스 라우터", L, False), ("rtN", L, False)]
DX = [("AWS Direct", L, False), ("Connect", L, False)]
DXGW = [("Direct Connect", L, False), ("gateway", L, False)]
TGW = [("Transit Gateway", L, False)]
VA = [("VPC-A", L, False), ("172.20.N.0/24", s, False)]
VB = [("VPC-B", L, False), ("10.1.1.0/24", s, False),
      ("VPC-B 연결: 규칙 없음", s, True), ("→ 아무것도 바꾸지 않음", s, False)]
SNAT = [("TGW로 들어올 때: 출발지 주소 바꾸기(SNAT)", s, True),
        ("Source CIDR 안의 출발지 → NAT 대역", s, False), ("목적지와 관계없이", s, False)]
DNAT = [("TGW에서 나갈 때: 목적지 주소 되돌리기(DNAT)", s, True),
        ("NAT 대역 안의 목적지 → 원래 대역", s, False)]
snat_w, dnat_w = w(SNAT), w(DNAT)
col_w = max(snat_w, dnat_w)

# ---- x layout
op_x = m
vm_cx = round(op_x + 10 + w(VM) / 2)
rt_cx = round(vm_cx + w(VM) / 2 + 12 + w(RT) / 2)
op_r = round(max(rt_cx + w(RT) / 2 + 10, op_x + 34 + tw("온프레미스 대역 172.20.N.0/24", s) + 10))
dx_cx = round(op_r + 10 + w(DX) / 2)
cloud_x = round(dx_cx + w(DX) / 2 + 10)
dxgw_cx = round(cloud_x + 10 + w(DXGW) / 2)
reg_x = round(dxgw_cx + w(DXGW) / 2 + 10)
col_l = round(reg_x + 10)  # TGW column (SNAT/DNAT text) left
col_r = round(col_l + col_w)
tgw_cx = round((col_l + col_r) / 2)
trunk = round(col_r + 6)
vpc_cx = round(trunk + 5 + tw("172.20.N.0/24", s) / 2)
vpc_cx = max(vpc_cx, trunk + 28 + S / 2)
reg_r = round(vpc_cx + w(VB) / 2 + 10)
# NAT rule boxes
lab_w = tw("Source CIDR", s)
val_dx = round(12 + lab_w + 14)
box_w = max(val_dx + tw("172.20.N.0/24", s) + 12,
            12 + tw("VPC-A 연결의 1:1 NAT 규칙", s) + 12); box_w = round(box_w)
reg_r = round(max(reg_r, col_l + box_w + 14 + box_w + 10))
cloud_r = round(reg_r + 12)
W = round(cloud_r + m)

# ---- y layout
cloud_y = m
reg_y = cloud_y + 42
box_y = reg_y + 38
box_h = 82
snat_b1 = box_y + box_h + 28
M = snat_b1 + 2 * P_s + 4 + 10 + S / 2       # main line
lab1 = M + S / 2 + 22
dnat_b1 = lab1 + 4 + 10 + 12
vb_cy = M + S / 2 + 22 + P_s + 6 + 10 + S / 2  # below VPC-A labels
vb_last = vb_cy + S / 2 + 22 + P_L + 2 * P_s
reg_b = vb_last + 4 + 12
op_y = M - S / 2 - 56
op_b = lab1 + 2 * P_L - 6 + 4 + 12 + 2   # VM's third line is s
cloud_b = reg_b + 12
H = cloud_b + m

# ---- draw
hdr = (f'<svg viewBox="0 0 {W:g} {H:g}" xmlns="http://www.w3.org/2000/svg" '
       "font-family=\"'Noto Sans CJK KR', 'Pretendard', Arial, sans-serif\">")
el.append("  <!-- Concept: where TGW 1:1 NAT rewrites addresses (per attachment, both directions). -->")
el.append('  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
          '<path d="M0,0 L8,3 L0,6 Z" fill="#232F3E"/></marker></defs>')
el.append(f'  <rect width="{W:g}" height="{H:g}" fill="#FFFFFF"/>')
# on-premises
R(op_x, op_y, op_r - op_x, op_b - op_y, GREY)
I("group/Corporate-data-center_32", op_x, op_y, 26)
T(op_x + 34, op_y + 21, "온프레미스 (내 Pod N)", L, bold=True, fill=GREY)
T(op_x + 34, op_y + 42, "온프레미스 대역 172.20.N.0/24", s)
# AWS Cloud / Region
R(cloud_x, cloud_y, cloud_r - cloud_x, cloud_b - cloud_y, INK)
I("group/AWS-Cloud-logo_32", cloud_x, cloud_y, 32)
T(cloud_x + 42, cloud_y + 24, "AWS Cloud", CL, bold=True)
R(reg_x, reg_y, reg_r - reg_x, reg_b - reg_y, TEAL, dash="3,3")
I("group/Region_32", reg_x, reg_y, 26)
T(reg_x + 34, reg_y + 21, "아시아 태평양(서울) ap-northeast-2", L, bold=True, fill=TEAL)
# nodes
node("resource/Server", vm_cx, M, VM)
node("resource/Amazon-VPC_Customer-Gateway", rt_cx, M, RT)
node("service/AWS-Direct-Connect", dx_cx, M, DX)
node("resource/AWS-Direct-Connect_Gateway", dxgw_cx, M, DXGW)
node("service/AWS-Transit-Gateway", tgw_cx, M, TGW)
node("service/Amazon-Virtual-Private-Cloud", vpc_cx, M, VA)
node("service/Amazon-Virtual-Private-Cloud", vpc_cx, vb_cy, VB)
# connectors
h = S / 2 + 4
def line(x1, y1, x2, y2, arrow=False, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    a = ' marker-end="url(#arrow)"' if arrow else ""
    el.append(f'  <line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="#232F3E" stroke-width="1.5"{d}{a}/>')
line(vm_cx + h, M, rt_cx - h, M)
line(rt_cx + h, M, dx_cx - h, M)
line(dx_cx + h, M, dxgw_cx - h, M)
line(dxgw_cx + h, M - 9, tgw_cx - h - 4, M - 9, arrow=True)
line(tgw_cx - h, M + 9, dxgw_cx + h + 4, M + 9, arrow=True, dash="5,4")
line(tgw_cx + h, M, vpc_cx - h, M)
el.append(f'  <polyline points="{tgw_cx + h:g},{M + 14:g} {trunk:g},{M + 14:g} {trunk:g},{vb_cy:g} '
          f'{vpc_cx - h:g},{vb_cy:g}" fill="none" stroke="#232F3E" stroke-width="1.5"/>')
# SNAT above TGW, DNAT below its label
y = snat_b1
for t, fs, b in SNAT:
    T(tgw_cx, y, t, fs, "middle", b); y += P_s
y = dnat_b1
for t, fs, b in DNAT:
    T(tgw_cx, y, t, fs, "middle", b); y += P_s
# NAT rule boxes
def rule_box(bx, title, nat):
    R(bx, box_y, box_w, box_h, GREY, sw=1, fill="#FFFFFF", rx=4)
    T(bx + 12, box_y + 24, title, s, bold=True)
    T(bx + 12, box_y + 48, "Source CIDR", s)
    T(bx + val_dx, box_y + 48, "172.20.N.0/24", s)
    T(bx + 12, box_y + 70, "NAT CIDR", s)
    T(bx + val_dx, box_y + 70, nat, s, bold=True, fill=ORANGE)
rule_box(col_l, "DXGW 연결의 1:1 NAT 규칙", "100.64.1.0/24")
rule_box(reg_r - 10 - box_w, "VPC-A 연결의 1:1 NAT 규칙", "100.64.2.0/24")

open(OUT, "w").write(hdr + "\n" + "\n".join(el) + "\n</svg>\n")
k = 900 / W
print(f"W={W:.1f} H={H:.1f}  900px: L={L*k:.2f} s={s*k:.2f}  snat_w={snat_w:.0f} dnat_w={dnat_w:.0f} box_w={box_w:.0f}")

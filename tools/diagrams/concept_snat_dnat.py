"""Generate docs/images/diagrams/concept-snat-dnat.draft.svg (layout source).
With --steps, also draw step badges 1-4 matching the numbered walk-through in docs/index.md 1-1-3
(written to concept-snat-dnat-steps.draft.svg by build.sh); the drawing is otherwise identical.

Concept: a TGW 1:1 NAT rule belongs to one Transit Gateway attachment and applies to every
packet crossing it. Entering the TGW through the attachment: SNAT (source, original range ->
NAT range). Leaving the TGW through it: DNAT (destination, NAT range -> original range).
The DXGW and VPC-A attachments each have a rule; the VPC-B attachment has none.
"""
import os, sys
sys.path.insert(0, os.path.expanduser("~/.claude/skills/skill-aws-arch-diagram/scripts"))
from check_layout import text_width as tw

OUT = sys.argv[1]
STEPS = "--steps" in sys.argv[2:]
L, s, CL = 18.5, 16, 19.5          # node/container labels, secondary, AWS Cloud title
S = 52                             # node icon size
INK, GREY, TEAL, PURPLE = "#232F3E", "#7D8998", "#00A4A6", "#8C4FFF"
m = 12
P_L, P_s = 22, 21                  # line pitch
OFF = 9                            # half the spacing of the arrow pair

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
def line(x1, y1, x2, y2, arrow=False, dash=None, stroke=INK):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    a = ' marker-end="url(#arrow)"' if arrow else ""
    el.append(f'  <line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="1.5"{d}{a}/>')

# ---- label sets
VM = [("VM vmN", L, False), ("172.20.N.10", s, False)]
RT = [("라우터 rtN", L, False)]
DX = [("AWS Direct", L, False), ("Connect", L, False)]
DXGW = [("Direct Connect", L, False), ("gateway", L, False)]
TGW = [("Transit", L, False), ("Gateway", L, False)]
# Transit Gateway attachments are the lines between the TGW and what they attach (guide: "TGW attachments are lines")
ATT_DX, ATT_A = "DXGW 연결", "VPC-A 연결"
ATT_B = [("VPC-B 연결", L, False), ("NAT 규칙 없음", s, True)]
VA = [("VPC-A", L, False), ("172.20.N.0/24", s, False)]
VB = [("VPC-B", L, False), ("10.1.1.0/24", s, False)]
def rule(att, nat):
    return [(f"{att} 연결의 1:1 NAT 규칙", s, True),
            ("TGW로 들어올 때 SNAT: 출발지", s, True),
            (f"172.20.N.0/24 → {nat}", s, False),
            ("TGW에서 나갈 때 DNAT: 목적지", s, True),
            (f"{nat} → 172.20.N.0/24", s, False)]
RULE_DX, RULE_A = rule("DXGW", "100.64.1.0/24"), rule("VPC-A", "100.64.2.0/24")
box_w = round(max(w(RULE_DX), w(RULE_A)) + 24)
box_h = 24 + 4 * P_s + 13

# ---- x layout
op_x = m
rt_cx = round(op_x + 14 + w(RT) / 2)
vm_x = rt_cx - S / 2                           # VM icon left; its labels sit to the right
op_r = round(max(op_x + 34 + tw("온프레미스 (Pod N)", L) + 12,
                 vm_x + S + 10 + w(VM) + 12, rt_cx + w(RT) / 2 + 12))
dx_cx = round(op_r + 14 + w(DX) / 2)
cloud_x = round(dx_cx + w(DX) / 2 + 12)
dxgw_cx = round(cloud_x + 12 + w(DXGW) / 2)
reg_x = round(dxgw_cx + w(DXGW) / 2 + 12)
h = S / 2 + 4                                  # connector gap from an icon center
reg_r = round(reg_x + 2 * box_w + 44)          # the two rule boxes side by side set the Region width
vpc_cx = round(reg_r - 12 - max(w(VA), w(VB)) / 2)
tgw_cx = round(reg_x + (vpc_cx - reg_x) / 2 + 12)
cloud_r = round(reg_r + 12)
W = round(cloud_r + m)
box_dx_x = reg_x + 10
box_a_x = reg_r - 10 - box_w
dx_lab = round((reg_x + tgw_cx - h) / 2)       # labels of the DXGW attachment (inside the Region)
a_lab = round((tgw_cx + h + vpc_cx - h) / 2)   # labels of the VPC-A attachment
dx_lead = box_dx_x + 30                        # where each rule box's leader meets its attachment line
a_lead = vpc_cx - h - 30
trunk = tgw_cx + h + 14                        # VPC-B attachment turns down here
assert reg_x + 8 <= dx_lead <= dx_lab - tw(ATT_DX, L) / 2 - 12
assert a_lab + tw(ATT_A, L) / 2 + 12 <= a_lead <= box_a_x + box_w - 24 and a_lead >= box_a_x + 24
assert box_dx_x + box_w + 20 <= box_a_x
assert dx_lab - tw(ATT_DX, L) / 2 >= reg_x + 10 and dx_lab + tw(ATT_DX, L) / 2 <= tgw_cx - 40
assert vpc_cx - h - trunk >= w(ATT_B) + 20

# ---- y layout
cloud_y = m
reg_y = cloud_y + 42
box_y = reg_y + 40
M = box_y + box_h + 34 + S / 2                 # main line
lab1 = M + S / 2 + 22                          # first label line under the main-row icons
vb_cy = lab1 + P_L + 10 + 22 + S / 2           # below VPC-A's two label lines and the attachment names
reg_b = vb_cy + S / 2 + 22 + P_L + 14
cloud_b = reg_b + 12
H = cloud_b + m
vm_cy = M - 132
op_y = vm_cy - S / 2 - 58
op_b = lab1 + 14

# ---- draw
hdr = (f'<svg viewBox="0 0 {W:g} {H:g}" xmlns="http://www.w3.org/2000/svg" '
       "font-family=\"'Noto Sans CJK KR', 'Pretendard', Arial, sans-serif\">")
el.append("  <!-- Concept: a TGW 1:1 NAT rule is set per attachment; entering the TGW -> SNAT, leaving -> DNAT. -->")
el.append('  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
          '<path d="M0,0 L8,3 L0,6 Z" fill="#232F3E"/></marker></defs>')
el.append(f'  <rect width="{W:g}" height="{H:g}" fill="#FFFFFF"/>')
# on-premises
R(op_x, op_y, op_r - op_x, op_b - op_y, GREY)
I("group/Corporate-data-center_32", op_x, op_y, 26)
T(op_x + 34, op_y + 21, "온프레미스 (Pod N)", L, bold=True, fill=GREY)
T(op_x + 34, op_y + 42, "LAN 172.20.N.0/24", s)
# AWS Cloud / Region
R(cloud_x, cloud_y, cloud_r - cloud_x, cloud_b - cloud_y, INK)
I("group/AWS-Cloud-logo_32", cloud_x, cloud_y, 32)
T(cloud_x + 42, cloud_y + 24, "AWS Cloud", CL, bold=True)
R(reg_x, reg_y, reg_r - reg_x, reg_b - reg_y, TEAL, dash="3,3")
I("group/Region_32", reg_x, reg_y, 26)
T(reg_x + 34, reg_y + 21, "아시아 태평양(서울) ap-northeast-2", L, bold=True, fill=TEAL)
# nodes
I("resource/Server", vm_x, vm_cy - S / 2)
T(vm_x + S + 10, vm_cy - 3, VM[0][0], L)
T(vm_x + S + 10, vm_cy + 19, VM[1][0], s)
node("resource/Amazon-VPC_Customer-Gateway", rt_cx, M, RT)
node("service/AWS-Direct-Connect", dx_cx, M, DX)
node("resource/AWS-Direct-Connect_Gateway", dxgw_cx, M, DXGW)
node("service/AWS-Transit-Gateway", tgw_cx, M, TGW)
node("service/Amazon-Virtual-Private-Cloud", vpc_cx, M, VA)
node("service/Amazon-Virtual-Private-Cloud", vpc_cx, vb_cy, VB)
# plain links (no address change on these hops)
line(rt_cx, vm_cy + h, rt_cx, M - h)
line(rt_cx + h, M, dx_cx - h, M)
line(dx_cx + h, M, dxgw_cx - h, M)
el.append(f'  <polyline points="{tgw_cx + S / 2:g},{M + 19:g} {trunk:g},{M + 19:g} {trunk:g},{vb_cy:g} '
          f'{vpc_cx - h:g},{vb_cy:g}" fill="none" stroke="#232F3E" stroke-width="1.5"/>')
# Each NAT-rule attachment is drawn as an arrow pair between the TGW and its peer:
# upper arrow = into the TGW (SNAT), lower arrow = out of the TGW (DNAT), name under the pair
def pair(p_cx, t_cx, lab_x, name):
    sgn = 1 if t_cx > p_cx else -1
    p_edge, t_edge = p_cx + sgn * h, t_cx - sgn * h
    line(p_edge, M - OFF, t_edge, M - OFF, arrow=True)
    line(t_edge, M + OFF, p_edge, M + OFF, arrow=True)
    T(lab_x, M - OFF - 8, "SNAT", s, "middle", True)
    T(lab_x, M + OFF + 19, "DNAT", s, "middle", True)
    T(lab_x, M + OFF + 19 + 26, name, L, "middle")
pair(dxgw_cx, tgw_cx, dx_lab, ATT_DX)
pair(vpc_cx, tgw_cx, a_lab, ATT_A)
# VPC-B attachment: the plain branch, named above its horizontal run
vb_lab = round((trunk + vpc_cx - h) / 2)
T(vb_lab, vb_cy - 8 - P_s, ATT_B[0][0], L, "middle")
T(vb_lab, vb_cy - 8, ATT_B[1][0], s, "middle", True)
# rule boxes, tied to their attachment with the purple dotted line
def rule_box(bx, lines, lead_x):
    el.append(f'  <rect x="{bx:g}" y="{box_y:g}" width="{box_w:g}" height="{box_h:g}" fill="#FFFFFF"/>')
    R(bx, box_y, box_w, box_h, GREY, sw=1)
    y = box_y + 24
    for t, fs, b in lines:
        T(bx + 12, y, t, fs, bold=b); y += P_s
    line(lead_x, box_y + box_h, lead_x, M - OFF, dash="4 3", stroke=PURPLE)
rule_box(box_dx_x, RULE_DX, dx_lead)
rule_box(box_a_x, RULE_A, a_lead)
# optional step badges (1 send, 2 SNAT into the TGW on DXGW, 3 DNAT out of the TGW on VPC-A, 4 reply)
def badge(cx, cy, n):
    el.append(f'  <circle cx="{cx:g}" cy="{cy:g}" r="13" fill="{INK}" stroke="#FFFFFF" stroke-width="2"/>')
    T(cx, cy + 0.35 * s, str(n), s, "middle", True, "#FFFFFF")
if STEPS:
    up, dn = M - OFF - 8 - 0.35 * s, M + OFF + 19 - 0.35 * s      # centers of the SNAT / DNAT labels
    gap = tw("SNAT", s) / 2 + 22
    badge(rt_cx + 24, (vm_cy + h + M - h) / 2, 1)                # VM -> router: the request leaves
    badge(dx_lab - gap, up, 2)                                   # DXGW attachment, into the TGW: SNAT
    badge(a_lab + gap, dn, 3)                                    # VPC-A attachment, out of the TGW: DNAT
    badge(a_lab + gap, up, 4)                                    # reply: VPC-A in (SNAT) ...
    badge(dx_lab - gap, dn, 4)                                   # ... and DXGW out (DNAT)
    assert dx_lab - gap - 13 >= dx_lead + 8 and a_lab + gap + 13 <= a_lead - 8

open(OUT, "w").write(hdr + "\n" + "\n".join(el) + "\n</svg>\n")
k = 900 / W
print(f"W={W:.1f} H={H:.1f}  900px: L={L*k:.2f} s={s*k:.2f}  box_w={box_w}")

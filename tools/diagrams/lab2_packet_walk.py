"""Generate lab2-packet-walk.draft.svg with large text (parametric layout)."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/.claude/skills/skill-aws-arch-diagram/scripts"))
from check_layout import text_width as tw

L = float(sys.argv[1]) if len(sys.argv) > 1 else 20      # node / container labels
s = float(sys.argv[2]) if len(sys.argv) > 2 else 17      # secondary text
OUT = sys.argv[3] if len(sys.argv) > 3 else 'out.draft.svg'
S = 56
INK = '#232F3E'
SUB = '#3B4553'      # darker secondary grey
LEAD = '#687078'
ORANGE = '#C7511F'

def r(v):
    return round(v, 1)

def f(v):
    v = r(v)
    return f'{v:g}'

out = []
def add(x):
    out.append(x)

def text(x, y, t, size, fill=INK, weight=None, anchor=None):
    a = f' font-weight="{weight}"' if weight else ''
    b = f' text-anchor="{anchor}"' if anchor else ''
    add(f'  <text x="{f(x)}" y="{f(y)}" font-size="{f(size)}"{a}{b} fill="{fill}">{t}</text>')

# ---------- text metrics
def w(t, size):
    return tw(t, size)

LP = L + 3          # pitch for L lines
SP = s + 4          # pitch for s lines

# ---------- packet boxes
HDR_BASE = 0.75 * s + 14           # header baseline from box top
ROW1 = HDR_BASE + s + 7
ROW2 = ROW1 + s + 6
BH = ROW2 + 0.25 * s + 10
TXT = 20                             # text start from box left (badge hangs on the left border)
VAL = TXT + w('출발지', s) + 10
def box_w(hdr, v1, v2):
    return max(TXT + w(hdr, s) + 12, VAL + max(w(v1, s), w(v2, s)) + 12)

BOXES = {
    1: ('온프레미스 VM이 보냄', ('172.20.N.10', False), ('100.64.2.10', False)),
    2: ('DXGW 연결 · 들어올 때 SNAT', ('100.64.1.10', True), ('100.64.2.10', False)),
    3: ('VPC-A 연결 · 나갈 때 DNAT', ('100.64.1.10', False), ('172.20.N.10', True)),
    4: ('VPC-A EC2가 응답', ('172.20.N.10', False), ('100.64.1.10', False)),
    5: ('VPC-A 연결 · 들어올 때 SNAT', ('100.64.2.10', True), ('100.64.1.10', False)),
    6: ('DXGW 연결 · 나갈 때 DNAT', ('100.64.2.10', False), ('172.20.N.10', True)),
}
BW = {k: box_w(v[0], v[1][0], v[2][0]) for k, v in BOXES.items()}

def packet_box(n, x, y, bw):
    hdr, (v1, o1), (v2, o2) = BOXES[n]
    add(f'  <rect x="{f(x)}" y="{f(y)}" width="{f(bw)}" height="{f(BH)}" fill="#FFFFFF" stroke="#7D8998" stroke-width="1" rx="4"/>')
    cy = y + HDR_BASE - 0.3 * s
    add(f'  <rect x="{f(x - 14)}" y="{f(cy - 14)}" width="28" height="28" fill="#FFFFFF"/>')
    add(f'  <circle cx="{f(x)}" cy="{f(cy)}" r="13" fill="{INK}"/>')
    text(x, cy + 0.35 * s, str(n), s, '#FFFFFF', '700', 'middle')
    text(x + TXT, y + HDR_BASE, hdr, s, INK, '600')
    for yy, lab, v, o in ((ROW1, '출발지', v1, o1), (ROW2, '목적지', v2, o2)):
        text(x + TXT, y + yy, lab, s, SUB)
        if o:
            text(x + VAL, y + yy, v, s, ORANGE, '600')
        else:
            text(x + VAL, y + yy, v, s, INK)

def leader(x, y_box, y_line):
    add(f'  <line x1="{f(x)}" y1="{f(y_box)}" x2="{f(x)}" y2="{f(y_line + (3 if y_box < y_line else -3))}" stroke="{LEAD}" stroke-width="1" stroke-dasharray="3,2"/>')
    add(f'  <circle cx="{f(x)}" cy="{f(y_line)}" r="3" fill="{LEAD}"/>')

def leader_turn(x, y_badge, x_badge, y_line):
    y0 = y_line + (3 if y_badge < y_line else -3) * -1
    y0 = y_line - 3 if y_badge < y_line else y_line + 3
    add(f'  <polyline points="{f(x)},{f(y0)} {f(x)},{f(y_badge)} {f(x_badge)},{f(y_badge)}" fill="none" stroke="{LEAD}" stroke-width="1" stroke-dasharray="3,2"/>')
    add(f'  <circle cx="{f(x)}" cy="{f(y_line)}" r="3" fill="{LEAD}"/>')

# ---------- header geometry (scaled for L)
BADGE = 28
TITLE_B = 22                 # container title baseline from top
CIDR_B = TITLE_B + 18        # CIDR line baseline
NEST = 30 if L <= 15 else TITLE_B + 0.25 * L + 9          # nested box start without CIDR
NEST_C = CIDR_B + 0.25 * s + 9                              # with CIDR
ICON_OFF = TITLE_B + 0.25 * L + 7                           # first icon under a subnet title

# ---------- X layout
M0 = 16
op_x = M0
wVM = w('온프레미스 VM', L)
wR = w('온프레미스', L)
vm_cx = op_x + 14 + wVM / 2
r_cx = max(vm_cx + wVM / 2 + 12 + wR / 2, vm_cx + 128)
op_title = '온프레미스 (내 Pod N)'
op_cidr = '온프레미스 대역 172.20.N.0/24'
box1_x = op_x + 16 + 13
op_r = max(r_cx + wR / 2 + 12,
           op_x + BADGE + 8 + w(op_cidr, s) + 10,
           op_x + BADGE + 8 + w(op_title, L) + 8,
           box1_x + BW[1] + 16)
dx_lab = ['AWS Direct', 'Connect']
dx_sub = ['전송 가상', '인터페이스']
wDX = max(max(w(t, L) for t in dx_lab), max(w(t, s) for t in dx_sub))
dx_cx = op_r + 10 + wDX / 2
cloud_x = dx_cx + wDX / 2 + 10
g_lab = ['Direct Connect', 'gateway']
wG = max(w(t, L) for t in g_lab)
g_cx = cloud_x + 10 + wG / 2
R = g_cx + wG / 2 + 10

wTGW = w('Transit Gateway', L)
wDL = w('DXGW 연결', s)
wVL = w('VPC-A 연결', s)
box2_x = R + 16 + 13
x2 = box2_x + 8
T = max(x2 + 8 + wDL + 8 + S / 2, x2 + wTGW / 2 + 6)
x3 = max(T + S / 2 + 8 + wVL + 6, T + wTGW / 2 + 6, box2_x + max(BW[2], BW[6]) + 14)
vpc_x = x3 + 16
sub_x = vpc_x + 16
box4_x = sub_x + 16 + 13
sub_w = max(16 + 13 + BW[4] + 16, BADGE + 8 + w('프라이빗 서브넷', L) + 8)
vpc_w = max(16 + sub_w + 16, BADGE + 8 + w('172.20.N.0/24', s) + 8)
vpc_r = vpc_x + vpc_w
ec2_cx = sub_x + sub_w / 2 + 20
x4 = ec2_cx - max(w('172.20.N.10', s), w('EC2', L)) / 2 - 10
box35_x = x3 + 20          # badge centered on the box edge; the leader turns into the badge
BW35 = max(BW[3], BW[5])
BW26 = max(BW[2], BW[6])

# table
cols = [('CIDR', ['100.64.1.0/24', '100.64.2.0/24', '172.20.N.0/24']),
        ('연결', ['DXGW', 'VPC-A', 'DXGW']),
        ('유형', ['system', 'system', 'propagated'])]
col_w = [max(w(h, s), max(w(v, s) for v in vs)) + 20 for h, vs in cols]
tbl_title = ['TGW 라우팅 테이블', '(1:1 NAT 적용 후)']
tbl_ts = L
tbl_w = max(sum(col_w), max(w(t, tbl_ts) for t in tbl_title) + 24)
col_w[-1] += tbl_w - sum(col_w)
ROWH = s + 20
TH = 2 * L + 22
tbl_h = TH + ROWH * 4
tbl_in_left = True

region_r = max(vpc_r, box35_x + BW35) + 16
cloud_r = region_r + 16
W = cloud_r + 16

# ---------- Y layout
# above the line, from the line upwards
M = 0.0   # temporary, shift later
conn_base = M - 8 - 0.75 - 4 - 0.25 * s
conn_top = conn_base - 0.75 * s
box2_y = min(conn_top - 10, M - S / 2 - 12) - BH
sub_y = M - S / 2 - ICON_OFF
vpc_y = sub_y - NEST_C
box3_y = vpc_y - 14 - BH
region_title_w = w('아시아 태평양(서울) ap-northeast-2', L)
region_y = min(box3_y, box2_y) - NEST if box35_x - 13 < R + BADGE + 8 + region_title_w else min(box3_y, box2_y) - 16
region_y = min(region_y, min(box3_y, box2_y) - NEST)
cloud_y = region_y - (TITLE_B + 0.25 * L + 3 + 9) - 3
box1_y = M - S / 2 - 14 - BH
op_y = box1_y - NEST_C

# below the line
lab1 = M + S / 2 + 0.75 * L + 6
def lines_below(specs):
    """specs: list of (text, size); returns baselines"""
    ys, y = [], lab1
    prev = None
    for t, sz in specs:
        if prev is not None:
            y += (prev * 0.25 + sz * 0.75 + 4)
        ys.append(y)
        prev = sz
    return ys
vm_specs = [('온프레미스 VM', L), ('vmN', L), ('172.20.N.10', s)]
r_specs = [('온프레미스', L), ('라우터', L), ('rtN', L)]
dx_specs = [(t, L) for t in dx_lab] + [(t, s) for t in dx_sub]
g_specs = [(t, L) for t in g_lab]
tgw_specs = [('Transit Gateway', L)]
ec2_specs = [('EC2', L), ('172.20.N.10', s)]
vm_y, r_y, dx_y, g_y, tgw_y, ec2_y = (lines_below(x) for x in (vm_specs, r_specs, dx_specs, g_specs, tgw_specs, ec2_specs))
op_b = max(vm_y[-1] + 0.25 * s, r_y[-1] + 0.25 * L) + 14
box6_y = tgw_y[-1] + 0.25 * L + 12
box4_y = ec2_y[-1] + 0.25 * s + 14
sub_b = box4_y + BH + 16
vpc_b = sub_b + 16
box5_y = vpc_b + 14
tbl_x = x3 - 12 - tbl_w      # exception: may overlap the Region border (white background masks it)
tbl_y = box6_y + BH + 16
region_b = max(box5_y + BH, tbl_y + tbl_h) + 16
cloud_b = region_b + 16
H0 = cloud_b + 16

shift = 16 - cloud_y
def Y(v):
    return v + shift
H = H0 + shift

print(f"op_r={op_r:.0f} cloud={cloud_x:.0f} R={R:.0f} T={T:.0f} x3={x3:.0f} vpc_r={vpc_r:.0f} b35r={box35_x+BW35:.0f} BW={ {k:round(v) for k,v in BW.items()} } tbl={tbl_w:.0f}", file=sys.stderr)
print(f"L={L} s={s} W={W:.0f} H={H:.0f}  L@900={L*900/W:.2f} s@900={s*900/W:.2f} table_in_left={tbl_in_left}", file=sys.stderr)

# ---------- emit
Wc, Hc = round(W), round(H)
add(f'<svg viewBox="0 0 {Wc} {Hc}" xmlns="http://www.w3.org/2000/svg" font-family="\'Noto Sans CJK KR\', \'Pretendard\', Arial, sans-serif">')
add('  <!-- Lab 2 after NAT: packet walk VM -> VPC-A EC2 and back. Orange = the address the step rewrote. -->')
add('  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#232F3E"/></marker></defs>')
add(f'  <rect width="{Wc}" height="{Hc}" fill="#FFFFFF"/>')

def group(x, y, wd, ht, color, badge, title, title_fill, cidr=None, sw=2, dash=None, tsize=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    add(f'  <rect x="{f(x)}" y="{f(Y(y))}" width="{f(wd)}" height="{f(ht)}" fill="none" stroke="{color}" stroke-width="{sw}"{d}/>')
    bs = 32 if badge.startswith('group/AWS-Cloud') else BADGE
    add(f'  <image href="bundle:{badge}" x="{f(x)}" y="{f(Y(y))}" width="{bs}" height="{bs}"/>')
    ts = tsize or L
    off = bs + 8 if bs == 32 else BADGE + 8
    tb = TITLE_B + 3 if bs == 32 else TITLE_B
    text(x + off, Y(y) + tb, title, ts, title_fill, '600')
    if cidr:
        text(x + off, Y(y) + CIDR_B, cidr, s, INK)

# containers
group(op_x, op_y, op_r - op_x, op_b - op_y, '#7D8998', 'group/Corporate-data-center_32', op_title, '#5F6B7A', op_cidr)
group(cloud_x, cloud_y, cloud_r - cloud_x, cloud_b - cloud_y, INK, 'group/AWS-Cloud-logo_32', 'AWS Cloud', INK, tsize=L + 1)
group(R, region_y, region_r - R, region_b - region_y, '#00A4A6', 'group/Region_32', '아시아 태평양(서울) ap-northeast-2', '#00A4A6', sw=2, dash='3,3')
group(vpc_x, vpc_y, vpc_w, vpc_b - vpc_y, '#8C4FFF', 'group/Virtual-private-cloud-VPC_32', 'VPC-A', '#8C4FFF', '172.20.N.0/24')
group(sub_x, sub_y, sub_w, sub_b - sub_y, '#00A4A6', 'group/Private-subnet_32', '프라이빗 서브넷', '#00A4A6', sw=1.5)

# nodes
def node(ref, cx, specs, ys):
    add(f'  <image href="bundle:{ref}" x="{f(cx - S / 2)}" y="{f(Y(M - S / 2))}" width="{S}" height="{S}"/>')
    for (t, sz), yy in zip(specs, ys):
        text(cx, Y(yy), t, sz, INK if sz == L else SUB, None, 'middle')

node('resource/Server', vm_cx, vm_specs, vm_y)
node('resource/Amazon-VPC_Customer-Gateway', r_cx, r_specs, r_y)
node('service/AWS-Direct-Connect', dx_cx, dx_specs, dx_y)
node('resource/AWS-Direct-Connect_Gateway', g_cx, g_specs, g_y)
node('service/AWS-Transit-Gateway', T, tgw_specs, tgw_y)
node('service/Amazon-EC2', ec2_cx, ec2_specs, ec2_y)

# connector labels (above the request line)
text(x2 + 8, Y(conn_base), 'DXGW 연결', s, SUB)
text(T + S / 2 + 8, Y(conn_base), 'VPC-A 연결', s, SUB)

# arrows: request solid at M-8 (left -> right), response dashed at M+8
xs = [vm_cx, r_cx, dx_cx, g_cx, T, ec2_cx]
for a, b in zip(xs, xs[1:]):
    x1, x2_ = a + S / 2 + 4, b - S / 2 - 4
    add(f'  <line x1="{f(x1)}" y1="{f(Y(M - 8))}" x2="{f(x2_ - 4)}" y2="{f(Y(M - 8))}" stroke="{INK}" stroke-width="1.5" marker-end="url(#arrow)"/>')
    add(f'  <line x1="{f(x2_)}" y1="{f(Y(M + 8))}" x2="{f(x1 + 4)}" y2="{f(Y(M + 8))}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5,4" marker-end="url(#arrow)"/>')

# packet boxes and leaders
x1l = (vm_cx + r_cx) / 2
packet_box(1, box1_x, Y(box1_y), BW[1])
leader(x1l, Y(box1_y + BH), Y(M - 8))
packet_box(2, box2_x, Y(box2_y), BW[2])
leader(x2, Y(box2_y + BH), Y(M - 8))
packet_box(3, box35_x, Y(box3_y), BW35)
leader_turn(x3, Y(box3_y) + HDR_BASE - 0.3 * s, box35_x - 13, Y(M - 8))
packet_box(4, box4_x, Y(box4_y), BW[4])
leader(x4, Y(box4_y), Y(M + 8))
packet_box(5, box35_x, Y(box5_y), BW35)
leader_turn(x3, Y(box5_y) + HDR_BASE - 0.3 * s, box35_x - 13, Y(M + 8))
packet_box(6, box2_x, Y(box6_y), BW[6])
leader(x2, Y(box6_y), Y(M + 8))

# TGW route table
ty = Y(tbl_y)
# TGW -> its route table: purple dashed link, out of the icon's right side, down past box 6
lx = box2_x + BW[6] + 12
add(f'  <polyline points="{f(T + S / 2)},{f(Y(M + 20))} {f(lx)},{f(Y(M + 20))} {f(lx)},{f(ty)}" fill="none" stroke="#8C4FFF" stroke-width="1.5" stroke-dasharray="4,3"/>')
add(f'  <!-- TGW route table: drawn last on a white background; it may sit over container borders -->')
add(f'  <rect x="{f(tbl_x - 1)}" y="{f(ty - 1)}" width="{f(tbl_w + 2)}" height="{f(tbl_h + 2)}" fill="#FFFFFF"/>')
add(f'  <rect x="{f(tbl_x)}" y="{f(ty)}" width="{f(tbl_w)}" height="{f(TH)}" fill="#8C4FFF"/>')
text(tbl_x + 12, ty + 11 + 0.75 * L, tbl_title[0], tbl_ts, '#FFFFFF', '600')
text(tbl_x + 12, ty + 11 + 1.75 * L + 2, tbl_title[1], tbl_ts, '#FFFFFF', '600')
rows = [[h for h, _ in cols]] + [list(t) for t in zip(*[vs for _, vs in cols])]
yy = ty + TH
for i, row in enumerate(rows):
    xx = tbl_x
    for j, cell in enumerate(row):
        fill = '#F2F3F3' if i == 0 else '#FFFFFF'
        add(f'  <rect x="{f(xx)}" y="{f(yy)}" width="{f(col_w[j])}" height="{f(ROWH)}" fill="{fill}" stroke="#879196" stroke-width="1"/>')
        text(xx + 10, yy + (ROWH - s) / 2 + 0.75 * s, cell, s, INK, '600' if i == 0 else None)
        xx += col_w[j]
    yy += ROWH
add('</svg>')
open(OUT, 'w').write('\n'.join(out) + '\n')

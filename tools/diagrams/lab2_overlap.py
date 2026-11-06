"""Generate lab2-overlap-problem.draft.svg sized for a ~900 CSS px column."""
import sys

FL, FS, FC = 19.5, 16.7, 21      # node/header labels, secondary, AWS Cloud title
GREY = "#3D4550"                 # darker secondary text
INK = "#232F3E"
GREEN, RED = "#1D8102", "#D13212"
S = 56                           # node icon size
B = 32                           # group badge size


def tw(s, f):
    return sum(f * (1.0 if ("가" <= c <= "힣" or "←" <= c <= "⯿") else 0.55) for c in s)


out = []


def T(x, y, s, f=FL, fill=INK, anchor=None, bold=False):
    a = f' text-anchor="{anchor}"' if anchor else ""
    w = ' font-weight="600"' if bold else ""
    out.append(f'  <text x="{x:g}" y="{y:g}" font-size="{f:g}"{w}{a} fill="{fill}">{s}</text>')


def R(x, y, w, h, stroke, sw=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'  <rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def I(ref, x, y, s=S):
    out.append(f'  <image href="bundle:{ref}" x="{x:g}" y="{y:g}" width="{s}" height="{s}"/>')


def group(ref, x, y, w, h, title, color, sw=2, dash=None, cidr=None, badge=B):
    R(x, y, w, h, color, sw, dash)
    I(ref, x, y, badge)
    T(x + badge + 8, y + 22, title, FL, color, bold=True)
    if cidr:
        T(x + badge + 8, y + 40, cidr, FS, INK)


def node(cx, top, lines):
    """lines: list of (text, font, fill, bold); first baseline 23 under the icon."""
    y = top + S + 23
    prev = None
    for s, f, fill, bold in lines:
        if prev is not None:
            y += 23 if f == FL and prev == FL else 21
        T(cx, y, s, f, fill, "middle", bold)
        prev = f
    return y


def half(lines):
    return max(tw(s, f) for s, f, *_ in lines) / 2



vm = [("온프레미스 VM", FL, INK, False), ("vmN", FL, INK, False), ("172.20.N.10", FS, GREY, False)]
rt = [("온프레미스 라우터", FL, INK, False), ("rtN", FL, INK, False),
      ("광고: 172.20.N.0/24", FS, GREY, False), ("및 10.200.0.1/32", FS, GREY, False)]
dx = [("AWS Direct Connect", FL, INK, False), ("전송 가상 인터페이스 2개", FS, GREY, False)]
dxgw = [("Direct Connect", FL, INK, False), ("gateway", FL, INK, False)]
tgw = [("Transit Gateway", FL, INK, False)]
ec2b = [("EC2 · 10.1.1.10", FL, INK, False), ("요청을 받고 응답함", FS, GREY, False)]
ec2a = [("EC2 · 172.20.N.10", FL, INK, False), ("tcpdump에 응답이 보임", FS, RED, True)]

MARGIN = 12
PAD = 12
# on-premises box
op_x = MARGIN
vm_cx = op_x + PAD + half(vm)
rt_cx = vm_cx + half(vm) + 20 + half(rt)
op_r = rt_cx + half(rt) + PAD
dx_cx = op_r + 10 + half(dx)
cloud_x = dx_cx + half(dx) + 10
dxgw_cx = cloud_x + 14 + half(dxgw)
reg_x = dxgw_cx + half(dxgw) + 12
lab_w = tw("DXGW 연결", FS)
tgw_cx = reg_x + 9 + lab_w + 9 + S / 2
CALLOUT = ["응답이 VPC-A로 감 —", "온프레미스 VM은", "받지 못함"]
x_c = 0
vpc_x = tgw_cx + max(half(tgw) + 8, max(tw(c, FS) for c in CALLOUT) / 2 + 10)
# VPC column width from the EC2-A label (widest node label in it)
ec2_half = max(half(ec2a), half(ec2b))
sub_pad = 10
vpc_w = 10 + sub_pad + 2 * ec2_half + sub_pad + 10
ec2_cx = vpc_x + vpc_w / 2
reg_r = vpc_x + vpc_w + 12
cloud_r = reg_r + 12
W = cloud_r + MARGIN

for name, v in [("vm", vm_cx), ("rt", rt_cx), ("op_r", op_r), ("dx", dx_cx), ("cloud", cloud_x),
                ("dxgw", dxgw_cx), ("reg", reg_x), ("tgw", tgw_cx), ("vpc", vpc_x),
                ("vpc_w", vpc_w), ("W", W)]:
    print(f"{name}={v:.1f}", file=sys.stderr)
print("min font at 900:", FS * 900 / W, "label:", FL * 900 / W, file=sys.stderr)

# round to integers for a tidy draft
r = lambda v: round(v)
vm_cx, rt_cx, op_r, dx_cx, cloud_x, dxgw_cx, reg_x, tgw_cx, x_c, vpc_x = map(
    r, (vm_cx, rt_cx, op_r, dx_cx, cloud_x, dxgw_cx, reg_x, tgw_cx, x_c, vpc_x))
vpc_w = r(vpc_w)
ec2_cx = vpc_x + vpc_w // 2
reg_r = vpc_x + vpc_w + 12
cloud_r = reg_r + 12
W = cloud_r + MARGIN

# ---- vertical layout ----
cloud_y = 16
reg_y = cloud_y + 44
va_y = reg_y + 38                      # VPC-A on top, VPC-B on the main line below it
va_sub_y = va_y + 72                   # CIDR on two lines
a_top = va_sub_y + 22 + 5 + 9
a_cy = a_top + S // 2
va_last = a_top + S + 23 + 21
va_sub_h = va_last + 4 + 12 - va_sub_y
va_h = va_sub_y + va_sub_h + 10 - va_y

vb_y = va_y + va_h + 20
vb_sub_y = vb_y + 54
ITOP = vb_sub_y + 34
M = ITOP + S // 2                      # main line
vb_last = ITOP + S + 23 + 21
vb_sub_h = vb_last + 4 + 12 - vb_sub_y
vb_h = vb_sub_y + vb_sub_h + 10 - vb_y
call_y = ITOP + S + 23 + 29            # callout under the TGW label

# TGW route table
cw = [146, 70, 112]                     # CIDR / 연결 / 유형 column widths
tbl_w = sum(cw)
tbl_x = tgw_cx - 12 - tbl_w              # right above the TGW, left of the red reply going up
BLOCK = 40 + 38 * 4 + 75                 # title bar, 4 rows, 3 note lines
tbl_y = ITOP - 16 - BLOCK                # block ends 16px above the TGW icon
th = 40                                  # title bar
rh = 38                                  # row height
rows = [("CIDR", "연결", "유형", "hdr"),
        ("172.20.N.0/24", "VPC-A", "propagated", "red"),
        ("10.1.1.0/24", "VPC-B", "propagated", ""),
        ("10.200.0.1/32", "DXGW", "propagated", "")]
tbl_bot = tbl_y + th + rh * len(rows)
n1 = tbl_bot + 28
n1b = n1 + 21
n2 = n1b + 22
reg_h = max(vb_y + vb_h + 16, call_y + 42 + 4 + 14) - reg_y
cloud_h = reg_y + reg_h + 16 - cloud_y

# on-prem box
op_y = ITOP - 58
op_last = ITOP + S + 23 + 23 + 21 + 21
op_h = op_last + 4 + 14 - op_y
note_y = op_y - 36                     # the two on-prem notes sit right above the box
H = cloud_y + cloud_h + MARGIN

# ---- emit ----
out.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
           "font-family=\"'Noto Sans CJK KR', 'Pretendard', Arial, sans-serif\">")
out.append("  <!-- Lab 2 before NAT: overlapping 172.20.N.0/24. Green = request (1), red dashed = reply (2). "
           "Sized for a ~900 CSS px column: 19.5px labels, 16.7px secondary text. -->")
out.append('  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
           f'<path d="M0,0 L8,3 L0,6 Z" fill="{INK}"/></marker>'
           '<marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
           f'<path d="M0,0 L8,3 L0,6 Z" fill="{GREEN}"/></marker>'
           '<marker id="arrowRed" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
           f'<path d="M0,0 L8,3 L0,6 Z" fill="{RED}"/></marker></defs>')
out.append(f'  <rect width="{W}" height="{H}" fill="#FFFFFF"/>')

# on-premises
group("group/Corporate-data-center_32", op_x, op_y, op_r - op_x, op_h, "온프레미스 (내 Pod N)", "#7D8998",
      cidr="온프레미스 대역 172.20.N.0/24")
T(op_x, note_y, "온프레미스에서 VPC-A로는 아예 갈 수 없음:", FS, GREY)
T(op_x, note_y + 22, "172.20.N.x는 온프레미스 대역의 주소이기 때문", FS, GREY)

# AWS Cloud / Region
R(cloud_x, cloud_y, cloud_r - cloud_x, cloud_h, INK)
I("group/AWS-Cloud-logo_32", cloud_x, cloud_y, 40)
T(cloud_x + 50, cloud_y + 27, "AWS Cloud", FC, INK, bold=True)
group("group/Region_32", reg_x, reg_y, reg_r - reg_x, reg_h, "아시아 태평양(서울) ap-northeast-2", "#00A4A6",
      dash="3,3")

# VPC-B
group("group/Virtual-private-cloud-VPC_32", vpc_x, vb_y, vpc_w, vb_h, "VPC-B", "#8C4FFF", cidr="10.1.1.0/24")
group("group/Private-subnet_32", vpc_x + 10, vb_sub_y, vpc_w - 20, vb_sub_h, "프라이빗 서브넷", "#00A4A6", sw=1.5)
# VPC-A (CIDR line kept, wrapped after the CIDR)
group("group/Virtual-private-cloud-VPC_32", vpc_x, va_y, vpc_w, va_h, "VPC-A", "#8C4FFF", cidr="172.20.N.0/24")
T(vpc_x + B + 8, va_y + 58, "(온프레미스와 같음)", FS, INK)
group("group/Private-subnet_32", vpc_x + 10, va_sub_y, vpc_w - 20, va_sub_h, "프라이빗 서브넷", "#00A4A6", sw=1.5)

# nodes on the main line
I("resource/Server", vm_cx - S / 2, ITOP); node(vm_cx, ITOP, vm)
I("resource/Amazon-VPC_Customer-Gateway", rt_cx - S / 2, ITOP); node(rt_cx, ITOP, rt)
I("service/AWS-Direct-Connect", dx_cx - S / 2, ITOP); node(dx_cx, ITOP, dx)
I("resource/AWS-Direct-Connect_Gateway", dxgw_cx - S / 2, ITOP); node(dxgw_cx, ITOP, dxgw)
I("service/AWS-Transit-Gateway", tgw_cx - S / 2, ITOP); node(tgw_cx, ITOP, tgw)
I("service/Amazon-EC2", ec2_cx - S / 2, ITOP); node(ec2_cx, ITOP, ec2b)
I("service/Amazon-EC2", ec2_cx - S / 2, a_top); node(ec2_cx, a_top, ec2a)

h = S / 2 + 4


def ln(x1, y1, x2, y2, color, mk, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'  <line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{color}" stroke-width="1.5"{d} '
               f'marker-end="url(#{mk})"/>')


def badge(cx, cy, n, color):
    out.append(f'  <circle cx="{cx:g}" cy="{cy:g}" r="13" fill="{color}"/>')
    T(cx, cy + 6, n, FS, "#FFFFFF", "middle")
    out[-1] = out[-1].replace('font-size', 'font-weight="700" font-size', 1)


# request (green), all on the main line
ln(vm_cx + h, M, rt_cx - h, M, GREEN, "arrowGreen")
ln(rt_cx + h, M, dx_cx - h, M, GREEN, "arrowGreen")
ln(dx_cx + h, M, dxgw_cx - h, M, GREEN, "arrowGreen")
ln(dxgw_cx + h, M, tgw_cx - h, M, GREEN, "arrowGreen")
ln(tgw_cx + h, M, ec2_cx - h, M, GREEN, "arrowGreen")
badge((vm_cx + rt_cx) / 2, M - 4 - 13, "1", GREEN)
T((reg_x + tgw_cx - S / 2) / 2, M - 8, "DXGW 연결", FS, GREY, "middle")

# reply (red dashed): VPC-B EC2 -> TGW, then TGW -> VPC-A EC2 through the corridor
ln(ec2_cx - h, M - 14, tgw_cx + h, M - 14, RED, "arrowRed", "5,4")
badge((tgw_cx + S / 2 + vpc_x) / 2, M - 14 - 4 - 13, "2", RED)
out.append(f'  <polyline points="{tgw_cx:g},{ITOP - 4} {tgw_cx:g},{a_cy} {ec2_cx - h:g},{a_cy}" '
           f'fill="none" stroke="{RED}" stroke-width="1.5" stroke-dasharray="5,4" marker-end="url(#arrowRed)"/>')
for i, s in enumerate(CALLOUT):
    T(tgw_cx, call_y + 21 * i, s, FS, RED, "middle", bold=True)

# TGW route table: drawn last, on a white mask over the Cloud and Region borders
out.append(f'  <rect x="{tbl_x - 8}" y="{tbl_y - 8}" width="{tbl_w + 12}" height="{n2 + 4 + 4 - tbl_y + 8}" fill="#FFFFFF"/>')
out.append(f'  <rect x="{tbl_x}" y="{tbl_y}" width="{tbl_w}" height="{th}" fill="#8C4FFF"/>')
T(tbl_x + 12, tbl_y + 27, "TGW 라우팅 테이블 (NAT 적용 전)", FL, "#FFFFFF", bold=True)
y = tbl_y + th
for row in rows:
    *cells, kind = row
    x = tbl_x
    for c, wdt in zip(cells, cw):
        out.append(f'  <rect x="{x}" y="{y}" width="{wdt}" height="{rh}" fill="{"#F2F3F3" if kind == "hdr" else "#FFFFFF"}" '
                   'stroke="#879196" stroke-width="1"/>')
        T(x + 10, y + 25, c, FS, RED if kind == "red" else INK, bold=kind in ("hdr", "red"))
        x += wdt
    y += rh
T(tbl_x, n1, "온프레미스가 광고한 172.20.N.0/24는", FS, RED, bold=True)
T(tbl_x, n1b, "보이지 않음", FS, RED, bold=True)
T(tbl_x, n2, "— 같은 접두사에서는 VPC 경로가 우선", FS, GREY)

# TGW route table <-> TGW: purple dashed leader, no arrowhead, one bend; enters the TGW top
# 14px left of the red reply line that leaves from the top center
lx = tgw_cx - 20
out.append(f'  <line x1="{lx:g}" y1="{tbl_bot}" x2="{lx:g}" y2="{ITOP - 4}" '
           'stroke="#8C4FFF" stroke-width="1.5" stroke-dasharray="4,3"/>')
print("table", tbl_x, tbl_y, tbl_x + tbl_w, tbl_bot, "notes end", n2 + 4, "leader", lx, tbl_bot, ITOP - 4, "len", ITOP - 4 - tbl_bot,
      "notes right", tbl_x + tw("온프레미스가 광고한 172.20.N.0/24는", FS), file=sys.stderr)

out.append("</svg>")
print(f"canvas {W} x {H}", file=sys.stderr)
open(sys.argv[1], "w").write("\n".join(out) + "\n")

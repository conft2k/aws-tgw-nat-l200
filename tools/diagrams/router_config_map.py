"""Generate router-config-map.draft.svg (900px-readable version)."""
import sys

INK, BLUE, ORANGE = "#232F3E", "#2563EB", "#C2410C"
GREY = "#3F4650"          # secondary text, darker than the old #545B64 / #7D8998
FL, FS, FD = 18, 16, 16    # label, secondary, badge digit sizes
S = 56                     # node icon size
R_B = 15                   # badge radius


def tw(s, fs):
    return sum(fs * (1.0 if ("가" <= c <= "힣" or "←" <= c <= "⯿") else 0.55) for c in s)


out = []
def add(s): out.append("  " + s)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, fs=FL, fill=INK, anchor=None, weight=None):
    a = f' text-anchor="{anchor}"' if anchor else ""
    w = f' font-weight="{weight}"' if weight else ""
    add(f'<text x="{x:g}" y="{y:g}" font-size="{fs}"{w}{a} fill="{fill}">{esc(s)}</text>')


def badge(cx, cy, n, color, label=None, lw="500"):
    add(f'<circle cx="{cx:g}" cy="{cy:g}" r="{R_B}" fill="{color}"/>')
    text(cx, cy + 5.5, str(n), FD, "#FFFFFF", "middle", "700")
    if label:
        text(cx + R_B + 6, cy + 6, label, FL, color, weight=lw)


def badge_w(label):
    return 2 * R_B + 6 + tw(label, FL)


def badge_c(cx, cy, n, color, label):
    """badge row centered on cx"""
    left = cx - badge_w(label) / 2
    badge(left + R_B, cy, n, color, label)


def icon(ref, cx, cy):
    add(f'<image href="bundle:{ref}" x="{cx - S/2:g}" y="{cy - S/2:g}" width="{S}" height="{S}"/>')


def pl(pts, color, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:g},{y:g}" for x, y in pts)
    add(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="1.5"{d}/>')


# ---- horizontal grid
X0 = 16
VMX, RTX = 110, 266
F = RTX + 82               # fork x (router side), clear of the router label
R = F + 20                 # on-prem right border
DXX = R + 98               # DX location column center
C = R + 196                # AWS Cloud left border
J = C + 24                 # rejoin x (AWS side)
GWX = J + 90               # DX gateway center
RGX = GWX + 78             # Region left (DXGW badge row passes under it)
RGT = "아시아 태평양(서울) ap-northeast-2"
RGW = round(36 + tw(RGT, FL) + 8)
TGX = RGX + RGW / 2
CR = RGX + RGW + 16        # Cloud right
W = CR + 16
ROWX = 48                  # left badge column (cx) inside on-prem

# ---- vertical grid
Y1 = 120                   # DX1 line
M = Y1 + 87                # main line
Y2 = M + 234               # DX2 line
YB1, YB2 = Y1 - 48, Y2 + 48  # BGP session brackets
TOP = 16
BOT = 534
H = BOT + 16

add(f'<rect width="{W:g}" height="{H}" fill="#FFFFFF"/>')

# on-premises group
add(f'<rect x="{X0}" y="{TOP}" width="{R - X0:g}" height="{BOT - TOP}" fill="none" stroke="#7D8998" stroke-width="2"/>')
add(f'<image href="bundle:group/Corporate-data-center_32" x="{X0}" y="{TOP}" width="28" height="28"/>')
text(X0 + 36, TOP + 22, "온프레미스 (내 Pod N)", FL, "#7D8998", weight="600")
badge(ROWX, 70, 1, INK, "Pod 번호 N")

# AWS Cloud
add(f'<rect x="{C:g}" y="{TOP}" width="{CR - C:g}" height="{BOT - TOP}" fill="none" stroke="{INK}" stroke-width="2"/>')
add(f'<image href="bundle:group/AWS-Cloud-logo_32" x="{C:g}" y="{TOP}" width="36" height="36"/>')
text(C + 46, TOP + 25, "AWS Cloud", 20, INK, weight="600")

# Region (around the TGW)
RGY = M - S / 2 - 36
RGB = M + S / 2 + 22 + 22 + 4 + 8
add(f'<rect x="{RGX:g}" y="{RGY:g}" width="{RGW:g}" height="{RGB - RGY:g}" fill="none" stroke="#00A4A6" stroke-width="2" stroke-dasharray="3,3"/>')
add(f'<image href="bundle:group/Region_32" x="{RGX:g}" y="{RGY:g}" width="28" height="28"/>')
text(RGX + 36, RGY + 22, RGT, FL, "#00A4A6", weight="600")

# on-premises nodes
icon("resource/Server", VMX, M)
text(VMX, M + S / 2 + 22, "온프레미스 VM", anchor="middle")
text(VMX, M + S / 2 + 44, "vmN", anchor="middle")
badge_c(VMX, M + S / 2 + 76, 2, INK, "온프레미스 대역")
text(VMX, M + S / 2 + 106, "172.20.N.0/24", anchor="middle", weight="500")
pl([(VMX + S / 2 + 4, M), (RTX - S / 2 - 4, M)], INK)

icon("resource/Amazon-VPC_Customer-Gateway", RTX, M)
text(RTX, M + S / 2 + 22, "온프레미스 라우터", anchor="middle")
text(RTX, M + S / 2 + 44, "rtN", anchor="middle")
badge_c(RTX, M + S / 2 + 76, 4, INK, "라우터 ASN")
text(RTX, M + S / 2 + 106, "65000", anchor="middle", weight="500")
badge(ROWX, M + S / 2 + 132, 3, INK, "Loopback1 10.200.0.1/32")

# DX paths: router -> fork -> DX location -> rejoin -> DX gateway
def dx_path(y, sign, color, n_ip, ip, n_if, ifname, n_vlan, vlan, n_aws, aws, n_key, tag, conn, vif, yb):
    mo = M + sign * 8                       # leaves / enters on the main line +-8
    pl([(RTX + S / 2 + 4, mo), (F, mo), (F, y), (DXX - S / 2 - 4, y)], color)
    pl([(DXX + S / 2 + 4, y), (J, y), (J, mo), (GWX - S / 2 - 4, mo)], color)
    icon("service/AWS-Direct-Connect", DXX, y)
    # router-side values, left of the fork corner (IP on the line, interface toward the main line)
    badge(ROWX, y, n_ip, color, ip)
    badge(ROWX, y - sign * 36, n_if, color, ifname)
    # AWS-side value, right of the rejoin corner
    badge(J + 10 + R_B, y, n_aws, color, aws)
    # DX location captions (below DX1 icon, above DX2 icon)
    lines = [("hosted connection", FL, INK), (conn, FS, GREY), (vif, FS, GREY)]
    if sign < 0:
        b = y + S / 2 + 22
        for s, fs, fill in lines:
            text(DXX, b, s, fs, fill, "middle"); b += 22
        badge_c(DXX, b + 4, n_vlan, color, vlan)
    else:
        b = y - S / 2 - 14
        for s, fs, fill in lines:
            text(DXX, b, s, fs, fill, "middle"); b -= 22
        badge_c(DXX, b - 4 - 6, n_vlan, color, vlan)
    # BGP session bracket over / under the line
    pl([(F, y + sign * 6), (F, yb), (J, yb), (J, y + sign * 6)], color, "5,4")
    text(F - 10, yb + 6, tag, FL, color, "end", "500")
    cy = yb - 20 if sign < 0 else yb + 20
    l1 = "BGP 세션"
    total = tw(l1, FS) + 10 + badge_w("BGP 키")
    left = DXX - total / 2
    text(left, cy + 6, l1, FS, GREY)
    badge(left + tw(l1, FS) + 10 + R_B, cy, n_key, color, "BGP 키")


dx_path(Y1, -1, BLUE, 8, "라우터 169.254.96.54/29", 6, "GigabitEthernet1.<VLAN1>", 7, "VLAN 189",
        9, "AWS 169.254.96.49/29", 10, "DX1", "awsdx1_…", "전송 가상 인터페이스 1", YB1)
dx_path(Y2, +1, ORANGE, 13, "라우터 169.254.96.46/29", 11, "GigabitEthernet2.<VLAN2>", 12, "VLAN 289",
        14, "AWS 169.254.96.41/29", 15, "DX2", "awsdx2_…", "전송 가상 인터페이스 2", YB2)

# DX gateway and TGW
icon("resource/AWS-Direct-Connect_Gateway", GWX, M)
text(GWX, M + S / 2 + 22, "Direct Connect", anchor="middle")
text(GWX, M + S / 2 + 44, "gateway", anchor="middle")
badge_c(GWX, M + S / 2 + 76, 5, INK, "Amazon 쪽 ASN")
text(GWX, M + S / 2 + 106, "65300", anchor="middle", weight="500")
pl([(GWX + S / 2 + 4, M), (TGX - S / 2 - 4, M)], INK)
icon("service/AWS-Transit-Gateway", TGX, M)
text(TGX, M + S / 2 + 22, "Transit Gateway", anchor="middle")
text(TGX, M + S / 2 + 44, "AS 65400", FS, GREY, "middle")

head = (f'<svg viewBox="0 0 {W:g} {H}" xmlns="http://www.w3.org/2000/svg" '
        "font-family=\"'Noto Sans CJK KR', 'Pretendard', Arial, sans-serif\">\n"
        "  <!-- Router config map (docs/router-config.md): badges 1-15 = input field numbers "
        "(1-5 common, 6-10 DX1, 11-15 DX2). Blue = DX1 (upper path), orange = DX2 (lower path). "
        "Example values = form placeholders (Pod 89). Sized for a ~900px page column: "
        "18px labels, 16px secondary text and badge digits. -->\n")
sys.stdout.write(head + "\n".join(out) + "\n</svg>\n")
print(f"canvas {W:g} x {H}", file=sys.stderr)

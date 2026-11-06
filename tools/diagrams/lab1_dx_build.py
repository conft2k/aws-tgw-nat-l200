# Generates lab1-dx-build.draft.svg with larger text for a ~900px-wide page.
import sys
F2, F1, FB = 15, 18, 15          # secondary, node/header, badge digit
S = 56; H = S // 2
INK = "#232F3E"
out = []
def t(x, y, s, fs=F2, w=None, anchor="middle", fill=INK):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    wt = f' font-weight="{w}"' if w else ""
    out.append(f'  <text x="{x:g}" y="{y:g}" font-size="{fs}"{wt}{a} fill="{fill}">{s}</text>')
def icon(ref, cx, cy, size=S):
    out.append(f'  <image href="bundle:{ref}" x="{cx-size/2:g}" y="{cy-size/2:g}" width="{size}" height="{size}"/>')
def badge(cx, cy, n):
    out.append(f'  <circle cx="{cx:g}" cy="{cy:g}" r="10.5" fill="{INK}"/>')
    t(cx, cy + 5.5, str(n), FB, 700, fill="#FFFFFF")
def pl(pts, dash=False, arrow=False):
    p = " ".join(f"{x:g},{y:g}" for x, y in pts)
    d = ' stroke-dasharray="6,4"' if dash else ""
    m = ' marker-end="url(#arrow)"' if arrow else ""
    out.append(f'  <polyline points="{p}" fill="none" stroke="{INK}" stroke-width="1.5"{d}{m}/>')

M = 12
# columns
R = 118                      # on-premises router
B = 360                      # fork bend (inside on-premises)
P = 372                      # on-premises right border
D = 488                      # hosted connections (DX location, outside both boxes)
C = 604                      # AWS Cloud left border
X2 = 616                     # merge bend (inside the Cloud)
G = 730                      # Direct Connect gateway
Rg = 848                     # Region left
T = 1008                     # Transit Gateway
RgR = 1092                   # Region right
CR = 1104                    # Cloud right
W = CR + M
# rows
yA1, yA2 = 82, 101           # BGP advertisement labels
ytop = 111                   # advertisement line
y1, ym, y2 = 175, 267, 359   # hosted connection 1, main line, hosted connection 2
ybot = 480                   # received-routes line
top, bottom = M, 565
Hh = bottom + M

out.append(f'<svg viewBox="0 0 {W} {Hh}" xmlns="http://www.w3.org/2000/svg" font-family="\'Noto Sans CJK KR\', \'Pretendard\', Arial, sans-serif">')
out.append('  <!-- Lab 1: how the Direct Connect side is built (pod N). Badges = creation order 1-5. -->')
out.append(f'  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="{INK}"/></marker></defs>')
out.append(f'  <rect width="{W}" height="{Hh}" fill="#FFFFFF"/>')
# on-premises group
out.append(f'  <rect x="{M}" y="{top}" width="{P-M}" height="{bottom-top}" fill="none" stroke="#7D8998" stroke-width="2"/>')
out.append(f'  <image href="bundle:group/Corporate-data-center_32" x="{M}" y="{top}" width="28" height="28"/>')
t(M + 36, top + 21, "온프레미스 (내 Pod N)", F1, 600, "start", "#7D8998")
t(M + 36, top + 40, "온프레미스 대역 172.20.N.0/24", F2, None, "start")
# AWS Cloud
out.append(f'  <rect x="{C}" y="{top}" width="{CR-C}" height="{bottom-top}" fill="none" stroke="{INK}" stroke-width="2"/>')
out.append(f'  <image href="bundle:group/AWS-Cloud-logo_32" x="{C}" y="{top}" width="32" height="32"/>')
t(C + 42, top + 23, "AWS Cloud", 19, 600, "start")
# Region
rt, rb = 124, 348
out.append(f'  <rect x="{Rg}" y="{rt}" width="{RgR-Rg}" height="{rb-rt}" fill="none" stroke="#00A4A6" stroke-width="2" stroke-dasharray="3,3"/>')
out.append(f'  <image href="bundle:group/Region_32" x="{Rg}" y="{rt}" width="28" height="28"/>')
t(Rg + 36, rt + 21, "아시아 태평양(서울)", F1, 600, "start", "#00A4A6")
t(Rg + 36, rt + 40, "ap-northeast-2", F2, None, "start", "#00A4A6")

# router (5)
icon("resource/Amazon-VPC_Customer-Gateway", R, ym)
t(R, ym + H + 22, "온프레미스 라우터", F1)
t(R, ym + H + 42, "rtN · AS 65000", F1)
t(R, ym + H + 61, "Loopback1 10.200.0.1/32", F2)
badge(R - H, ym - H - 16, 5)
# router -> hosted connections (fork)
pl([(R + H + 4, ym - 8), (B, ym - 8), (B, y1), (D - H - 4, y1)])
pl([(R + H + 4, ym + 8), (B, ym + 8), (B, y2), (D - H - 4, y2)])
t(R + H + 10, ym - 16, "GigabitEthernet1.<VLAN1>", F2, None, "start")
t(R + H + 10, ym + 24, "GigabitEthernet2.<VLAN2>", F2, None, "start")
# hosted connections (1) with their transit VIFs (4)
for y, n, v in ((y1, 1, "VLAN1"), (y2, 2, "VLAN2")):
    icon("service/AWS-Direct-Connect", D, y)
    t(D, y + H + 22, f"hosted connection {n}", F1)
    t(D, y + H + 42, f"50 Mbps · VLAN <{v}>", F2)
    t(D, y + H + 61, f"전송 가상 인터페이스 {n}", F2)
    t(D, y + H + 80, "BGP + BFD · 169.254.x.x/29", F2)
    badge(D - H + 12, y - H - 16, 1)
    badge((D + H + C) / 2, y - 16, 4)
# hosted connections -> DX gateway (merge)
pl([(D + H + 4, y1), (X2, y1), (X2, ym - 8), (G - H - 4, ym - 8)])
pl([(D + H + 4, y2), (X2, y2), (X2, ym + 8), (G - H - 4, ym + 8)])
# Direct Connect gateway (2)
icon("resource/AWS-Direct-Connect_Gateway", G, ym)
t(G, ym + H + 22, "Direct Connect gateway", F1)
t(G, ym + H + 41, "AS 65300", F2)
badge(G - 24, ym - H - 16, 2)
# gateway association (3) and its allowed prefixes
pl([(G + H + 4, ym), (T - H - 4, ym)])
t(Rg + 12, 189, "게이트웨이 연결", F2, None, "start")
t(Rg + 12, 208, "허용된 접두사:", F2, None, "start")
t(Rg + 12, 227, "100.64.2.0/24, 10.1.1.0/24", F2, None, "start")
badge((Rg + T - H) / 2, ym - 16, 3)
# Transit Gateway
icon("service/AWS-Transit-Gateway", T, ym)
t(T, ym + H + 22, "Transit Gateway", F1)
t(T, ym + H + 41, "AS 65400", F2)

# BGP advertisement: router -> DX gateway
pl([(R, ym - H - 4), (R, ytop), (G, ytop), (G, ym - H - 4)], dash=True, arrow=True)
LX = 220
t(LX, yA1, "BGP 광고 (온프레미스 라우터 → AWS)", F2, 600)
t(LX, yA2, "172.20.N.0/24 · 10.200.0.1/32", F2)
# received routes: DX gateway -> router
pl([(G, ym + H + 50), (G, ybot), (R, ybot), (R, ym + H + 70)], dash=True, arrow=True)
t(LX, ybot + 16, "온프레미스 라우터가 받는 경로", F2, 600)
t(LX, ybot + 35, "= 허용된 접두사", F2, 600)
t(LX, ybot + 54, "100.64.2.0/24 · 10.1.1.0/24", F2)
t(LX, ybot + 73, "두 VIF 모두 같은 경로 (ECMP)", F2)
out.append("</svg>")
open(sys.argv[1], "w").write("\n".join(out) + "\n")
print("canvas", W, Hh, "min@900", round(min(F2, FB) * 900 / W, 2), "label@900", round(F1 * 900 / W, 2))

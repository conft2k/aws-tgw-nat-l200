import sys
from dg import D, L, M, S, INK, tw, marker, table

OUT = sys.argv[1]
d = D()
GREEN, RED, PURPLE = "#1D8102", "#D13212", "#8C4FFF"

d.text(8, 30, "DXGW 연결의 NAT system routes: 켬과 끔", 20, weight="700")
d.text(8 + tw("DXGW 연결의 NAT system routes: 켬과 끔", 20) + 24, 30,
       "1:1 NAT 규칙 172.20.N.0/24 → 100.64.1.0/24", M)

COLS = [("CIDR", 132), ("연결", 59), ("유형", 105), ("상태", 98)]
ADV1 = [("광고 172.20.N.0/24", M, INK, "500"), ("(또는 172.20.0.0/16)", M)]
ADV2 = [("광고 100.64.1.0/24", M, INK, "500"), ("+ 172.20.N.0/24", M, INK, "500")]


def panel(y0, title, adv, tables):
    """adv = advertisement caption lines under the router; tables = [(header, bg, rows)]."""
    px = 8
    # columns (x) ---------------------------------------------------------
    router_half = max(tw(s, f) for s, f, *_ in [("온프레미스 라우터", L)] + ADV1 + ADV2) / 2
    op_x = px + 6
    rcx = round(op_x + 9 + router_half)
    op_r = round(rcx + router_half + 9)
    dx_half = tw("AWS Direct Connect", L) / 2
    dxcx = round(op_r + 9 + dx_half)
    cl_x = round(dxcx + dx_half + 9)
    gw_half = tw("Direct Connect", L) / 2
    gwcx = round(cl_x + 9 + gw_half)
    rg_x = round(gwcx + gw_half + 9)
    tg_half = tw("Transit Gateway", L) / 2
    tgcx = round(rg_x + 10 + tg_half)
    tb_x = round(tgcx + tg_half + 18)
    tb_w = sum(c[1] for c in COLS)
    rg_r = tb_x + tb_w + 6
    cl_r = rg_r + 8
    p_r = cl_r + 8
    # rows (y) ------------------------------------------------------------
    op_y = cl_y = y0 + 36
    rg_y = cl_y + 36
    cy = rg_y + 34 + S / 2
    ty = rg_y + 34
    # TGW route table link: purple dashed, one elbow per extra table, drawn under the tables
    tops = [ty]
    for hdr, bg, rows in tables[:-1]:
        tops.append(tops[-1] + 34 * (len(rows) + 2) + 14)
    d.line(tgcx + S / 2 + 4, cy, tb_x, cy, stroke=PURPLE, sw=1.5, dash="4,3")
    for top in tops[1:]:
        d.poly([(tb_x - 13, cy), (tb_x - 13, top + 17), (tb_x, top + 17)], stroke=PURPLE, sw=1.5, dash="4,3")
    tb = ty
    for i, (hdr, bg, rows) in enumerate(tables):
        if i:
            tb += 14
        tb = table(d, tb_x, tb, COLS, rows, header=(hdr, bg, "#FFFFFF"))
    # nodes
    lab_bottom = d.node("resource/Amazon-VPC_Customer-Gateway", rcx, cy,
                        [("온프레미스 라우터", L), ("rtN", L), ("AS 65000", M)] + adv)
    op_b = lab_bottom + 4 + 10
    d.group("onprem", op_x, op_y, op_r - op_x, op_b - op_y, "온프레미스", "Pod N")
    d.node("service/AWS-Direct-Connect", dxcx, cy, [("AWS Direct Connect", L), ("transit VIF 2개", M)])
    d.node("resource/AWS-Direct-Connect_Gateway", gwcx, cy, [("Direct Connect", L), ("gateway", L), ("AS 65300", M)])
    tl = d.node("service/AWS-Transit-Gateway", tgcx, cy, [("Transit Gateway", L), ("AS 65400", M)])
    rg_b = max(tb, tl + 4) + 10
    cl_b = rg_b + 10
    d.group("region", rg_x, rg_y, rg_r - rg_x, rg_b - rg_y, "아시아 태평양(서울) ap-northeast-2")
    d.cloud(cl_x, cl_y, cl_r - cl_x, cl_b - cl_y)
    h = S / 2 + 4
    for a, b in ((rcx, dxcx), (dxcx, gwcx), (gwcx, tgcx)):
        d.line(a + h, cy, b - h, cy, dash="5,4", marker="arrow")
    d.text((dxcx + S / 2 + cl_x) / 2, cy - 8, "BGP", M, anchor="middle")
    p_b = max(cl_b, op_b) + 10
    d.rect(px, y0, p_r - px, p_b - y0, stroke="#7D8998", sw=1.5)
    d.text(px + 12, y0 + 21, title, L, weight="700")
    return p_r, p_b


r1, b1 = panel(46, "NAT system routes 켬 (기본값)",
               ADV1,
               [("온프레미스가 172.20.N.0/24(또는 /16) 광고 중", PURPLE,
                 [["100.64.1.0/24", "DXGW", "system", ("Active", GREEN, "700")]]),
                ("온프레미스가 겹치는 경로 광고 중단", RED,
                 [["100.64.1.0/24", "DXGW", "system", ("Blackhole", RED, "700")]])])
r2, b2 = panel(b1 + 16, "NAT system routes 끔",
               ADV2,
               [("NAT system routes 끔 + 온프레미스가 직접 광고", PURPLE,
                 [["100.64.1.0/24", "DXGW", "propagated", ("Active", GREEN, "700")],
                  ["172.20.N.0/24", "DXGW", "propagated", ("Active", GREEN, "700")]])])
W, H = max(r1, r2) + 8, b2 + 8
print("canvas", W, H, file=sys.stderr)
open(OUT, "w").write(d.svg(W, H, marker("arrow", INK)))

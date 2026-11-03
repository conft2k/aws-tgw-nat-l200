# 라우터 설정 생성기

[실습 1-4](lab1.md#lab1-4)에서 적은 값을 넣으면 라우터에 붙여 넣을 설정이 만들어집니다. 값은 이 브라우저 안에서만 쓰이고 어디로도 보내지지 않습니다.

## 값이 쓰이는 곳 { #map }

그림의 번호는 아래 입력 칸의 번호와 같습니다. 위쪽 회선이 **DX1**, 아래쪽 회선이 **DX2**입니다.

![라우터 설정 값 지도: 1번 Pod 번호는 LAN 172.20.N.0/24, DX1(위)은 2번 VLAN, 3번 라우터 쪽 IP, 4번 Amazon 쪽 IP, 5번 BGP 키, DX2(아래)는 6번부터 9번까지 같은 순서이다. 두 전송 가상 인터페이스는 Direct Connect gateway(AS 65300)와 Transit Gateway(AS 65400)로 이어진다](images/diagrams/router-config-map.png)

## 값 넣기 { #form }

DX1 값은 `tgw-nat-vif1`, DX2 값은 `tgw-nat-vif2`의 **Peerings** 탭에서 가져옵니다. 피어 IP는 `/29`를 붙인 채로 넣어도 됩니다.

<div class="gen-form">
  <fieldset class="gen-group gen-common">
    <legend>공통</legend>
    <label><span class="gen-badge">1</span><span class="gen-name">Pod 번호 N<small>실습 장비 페이지의 podN</small></span><input id="g-pod" inputmode="numeric" placeholder="89"></label>
  </fieldset>
  <fieldset class="gen-group gen-dx1">
    <legend>DX1 · <code>awsdx1_…</code> · <code>tgw-nat-vif1</code> · 라우터 GigabitEthernet1</legend>
    <label><span class="gen-badge">2</span><span class="gen-name">VLAN</span><input id="g-vlan1" inputmode="numeric" placeholder="189"></label>
    <label><span class="gen-badge">3</span><span class="gen-name">Your router peer IP<small>라우터 쪽 IP</small></span><input id="g-my1" placeholder="169.254.96.54/29"></label>
    <label><span class="gen-badge">4</span><span class="gen-name">Amazon router peer IP<small>AWS 쪽 IP</small></span><input id="g-aws1" placeholder="169.254.96.49/29"></label>
    <label><span class="gen-badge">5</span><span class="gen-name">BGP authentication key</span><input id="g-key1" autocomplete="off" spellcheck="false"></label>
  </fieldset>
  <fieldset class="gen-group gen-dx2">
    <legend>DX2 · <code>awsdx2_…</code> · <code>tgw-nat-vif2</code> · 라우터 GigabitEthernet2</legend>
    <label><span class="gen-badge">6</span><span class="gen-name">VLAN</span><input id="g-vlan2" inputmode="numeric" placeholder="289"></label>
    <label><span class="gen-badge">7</span><span class="gen-name">Your router peer IP<small>라우터 쪽 IP</small></span><input id="g-my2" placeholder="169.254.96.46/29"></label>
    <label><span class="gen-badge">8</span><span class="gen-name">Amazon router peer IP<small>AWS 쪽 IP</small></span><input id="g-aws2" placeholder="169.254.96.41/29"></label>
    <label><span class="gen-badge">9</span><span class="gen-name">BGP authentication key</span><input id="g-key2" autocomplete="off" spellcheck="false"></label>
  </fieldset>
</div>

## 만들어진 설정 { #output }

줄 앞의 번호는 그 줄에 들어간 값입니다. 입력 칸을 누르면 그 값이 들어가는 줄이 강조됩니다. 번호는 복사되지 않습니다.

<p><button id="g-copy" class="md-button md-button--primary" type="button">복사</button> <span id="g-msg" class="gen-msg" aria-live="polite"></span></p>

<pre id="g-out" class="gen-out"></pre>

<script>
(function () {
  const ids = ["pod", "vlan1", "my1", "aws1", "key1", "vlan2", "my2", "aws2", "key2"];
  const badge = { pod: 1, vlan1: 2, my1: 3, aws1: 4, key1: 5, vlan2: 6, my2: 7, aws2: 8, key2: 9 };
  const group = { pod: "common", vlan1: "dx1", my1: "dx1", aws1: "dx1", key1: "dx1", vlan2: "dx2", my2: "dx2", aws2: "dx2", key2: "dx2" };
  const el = (k) => document.getElementById("g-" + k);
  const ip = (v) => v.trim().replace(/\/\d+$/, "");
  const maskOf = (v) => {
    const m = v.trim().match(/\/(\d+)$/);
    const len = m ? parseInt(m[1], 10) : 29;
    const n = len === 0 ? 0 : (0xffffffff << (32 - len)) >>> 0;
    return [24, 16, 8, 0].map((s) => (n >>> s) & 255).join(".");
  };
  const isIp = (v) => /^\d{1,3}(\.\d{1,3}){3}$/.test(ip(v)) && ip(v).split(".").every((o) => +o <= 255);
  const toInt = (v) => ip(v).split(".").reduce((a, o) => a * 256 + +o, 0);
  const same29 = (a, b) => Math.floor(toInt(a) / 8) === Math.floor(toInt(b) / 8);
  const inRange = (v, lo, hi) => /^\d+$/.test(v) && +v >= lo && +v <= hi;
  const circ = (k) => "①②③④⑤⑥⑦⑧⑨"[badge[k] - 1];
  let focused = null;
  let text = "";

  function check(v) {
    const problems = [];
    if (v.pod && !inRange(v.pod, 1, 99)) problems.push(circ("pod") + " Pod 번호는 1–99");
    for (const n of ["1", "2"]) {
      if (v["vlan" + n] && !inRange(v["vlan" + n], 1, 4094)) problems.push(circ("vlan" + n) + " VLAN은 1–4094");
      for (const k of ["my" + n, "aws" + n]) if (v[k] && !isIp(v[k])) problems.push(circ(k) + " IP 형식");
      const a = v["my" + n], b = v["aws" + n];
      if (a && b && isIp(a) && isIp(b)) {
        if (ip(a) === ip(b)) problems.push(circ("my" + n) + circ("aws" + n) + " 두 IP가 같음");
        else if (!same29(a, b)) problems.push(circ("my" + n) + circ("aws" + n) + " 같은 인터페이스의 값인지 확인(/29가 다름)");
      }
    }
    if (v.vlan1 && v.vlan1 === v.vlan2) problems.push(circ("vlan1") + circ("vlan2") + " VLAN이 같음");
    return problems;
  }

  function render() {
    const v = Object.fromEntries(ids.map((k) => [k, el(k).value.trim()]));
    const missing = ids.filter((k) => !v[k]);
    const problems = check(v);
    const msg = el("msg");
    msg.classList.toggle("gen-warn", problems.length > 0);
    if (problems.length) msg.textContent = "확인하세요: " + problems.join(" · ");
    else if (missing.length) msg.textContent = "아직 비어 있는 값: " + missing.map(circ).join(" ");
    else msg.textContent = "모든 값을 넣었습니다.";
    ids.forEach((k) => el(k).classList.toggle("gen-filled", !!v[k]));

    const P = (k, ph) => v[k] || ph;
    const A = (n) => (v["aws" + n] ? ip(v["aws" + n]) : "<AWS_IP" + n + ">");
    const L = [];
    const add = (s, ...keys) => L.push({ s, keys });
    add("configure terminal");
    for (const n of ["1", "2"]) {
      add("interface GigabitEthernet" + n + "." + P("vlan" + n, "<VLAN" + n + ">"), "vlan" + n);
      add(" description DX" + n + " transit VIF");
      add(" encapsulation dot1Q " + P("vlan" + n, "<VLAN" + n + ">"), "vlan" + n);
      add(" ip address " + (v["my" + n] ? ip(v["my" + n]) + " " + maskOf(v["my" + n]) : "<MY_IP" + n + "> 255.255.255.248"), "my" + n);
      add(" bfd interval 300 min_rx 300 multiplier 3");
    }
    add("interface Loopback1");
    add(" description source that no NAT rule matches");
    add(" ip address 10.200.0.1 255.255.255.255");
    add("router bgp 65000");
    add(" bgp log-neighbor-changes");
    for (const n of ["1", "2"]) {
      add(" neighbor " + A(n) + " remote-as 65300", "aws" + n);
      add(" neighbor " + A(n) + " password " + P("key" + n, "<BGP_KEY" + n + ">"), "aws" + n, "key" + n);
      add(" neighbor " + A(n) + " fall-over bfd", "aws" + n);
    }
    add(" address-family ipv4");
    add("  network 172.20." + P("pod", "<POD>") + ".0 mask 255.255.255.0", "pod");
    add("  network 10.200.0.1 mask 255.255.255.255");
    add("  maximum-paths 2");
    for (const n of ["1", "2"]) add("  neighbor " + A(n) + " activate", "aws" + n);
    add(" exit-address-family");
    add("end");

    text = L.map((l) => l.s).join("\n") + "\n";
    const out = el("out");
    out.textContent = "";
    for (const l of L) {
      const row = document.createElement("span");
      row.className = "gen-line" + (focused && l.keys.includes(focused) ? " gen-hit" : "");
      const gut = document.createElement("span");
      gut.className = "gen-gutter";
      gut.setAttribute("aria-hidden", "true");
      for (const k of l.keys) {
        const b = document.createElement("span");
        b.className = "gen-badge gen-" + group[k];
        b.textContent = badge[k];
        gut.appendChild(b);
      }
      const code = document.createElement("span");
      code.className = "gen-code";
      code.textContent = l.s;
      row.append(gut, code);
      out.appendChild(row);
    }
  }

  ids.forEach((k) => {
    el(k).addEventListener("input", render);
    el(k).addEventListener("focus", () => { focused = k; render(); });
    el(k).addEventListener("blur", () => { focused = null; render(); });
  });
  el("copy").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(text);
      el("msg").classList.remove("gen-warn");
      el("msg").textContent = "복사했습니다. 라우터 웹 터미널에 붙여 넣으세요.";
    } catch (e) {
      const r = document.createRange();
      r.selectNodeContents(el("out"));
      const s = window.getSelection();
      s.removeAllRanges();
      s.addRange(r);
      el("msg").textContent = "아래 상자가 선택되었습니다. Ctrl+C로 복사하세요.";
    }
  });
  render();
})();
</script>

## 넣는 값 { #inputs }

| 번호 | 값 | 찾는 곳 |
|---|---|---|
| 1 | Pod 번호 N | 실습 장비 페이지(`podN`) |
| 2, 6 | VLAN | 실습 장비 페이지, 또는 전송 가상 인터페이스 상세의 **VLAN** |
| 3, 7 | Your router peer IP | 전송 가상 인터페이스 상세 → **Peerings** 탭 |
| 4, 8 | Amazon router peer IP | 전송 가상 인터페이스 상세 → **Peerings** 탭 |
| 5, 9 | BGP authentication key | 전송 가상 인터페이스 상세 → **Peerings** 탭 |

DX1(2–5)은 `awsdx1_…` 위에 만든 `tgw-nat-vif1`, DX2(6–9)는 `awsdx2_…` 위에 만든 `tgw-nat-vif2`의 값입니다. 두 인터페이스의 값을 섞으면 BGP가 올라오지 않습니다. 생성기는 같은 인터페이스의 두 피어 IP가 같은 `/29`에 있는지 확인해 알려 줍니다.

## 설정이 하는 일 { #explain }

| 부분 | 쓰는 값 | 하는 일 |
|---|---|---|
| `GigabitEthernet1.<VLAN1>`, `GigabitEthernet2.<VLAN2>` | 2·3, 6·7 | 전송 가상 인터페이스마다 하나씩 만드는 서브인터페이스. VLAN 번호와 라우터 쪽 IP, 회선 끊김을 빨리 알아채는 BFD를 설정 |
| `Loopback1` `10.200.0.1/32` | — | NAT 규칙에 없는 주소. 주소가 바뀌지 않는 경우를 확인할 때 씀 |
| `neighbor … remote-as 65300` | 4·5, 8·9 | Direct Connect gateway(AS 65300)와 BGP로 경로를 주고받음. BGP 키와 BFD를 함께 씀 |
| `network 172.20.N.0 …`, `network 10.200.0.1 …` | 1 | 온프레미스 LAN과 Loopback1을 AWS에 광고 |
| `maximum-paths 2` | — | 두 전송 가상 인터페이스로 받은 같은 경로를 함께 씀(ECMP) |

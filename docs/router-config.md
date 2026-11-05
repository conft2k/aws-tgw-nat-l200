# 4-1. 라우터 설정 생성기

[2-2-4](lab1.md#lab1-4)에서 적은 값을 넣으면 온프레미스 라우터(`rtN`)에 붙여 넣을 설정이 만들어집니다. 값은 이 브라우저 안에서만 쓰이고 어디로도 보내지지 않습니다.

## 4-1-1. 값이 쓰이는 곳 { #map }

그림의 번호는 아래 입력 칸의 번호와 같습니다. 위쪽 회선이 **DX1**, 아래쪽 회선이 **DX2**입니다.

![라우터 설정 값 지도: 공통 값은 1번 Pod 번호, 2번 온프레미스 대역 172.20.N.0/24, 3번 Loopback1 10.200.0.1/32, 4번 라우터 ASN 65000, 5번 Direct Connect gateway의 Amazon 쪽 ASN 65300이다. DX1(위)은 6번 라우터 인터페이스 GigabitEthernet1, 7번 VLAN, 8번 라우터 쪽 IP, 9번 Amazon 쪽 IP, 10번 BGP 키이고, DX2(아래)는 11번부터 15번까지 같은 순서이다. 두 전송 가상 인터페이스는 Direct Connect gateway와 Transit Gateway(AS 65400)로 이어진다](images/diagrams/router-config-map.png)

## 4-1-2. 값 넣기 { #form }

**미리 채움**이라고 적힌 칸에는 워크숍 값이 들어 있습니다. 워크숍에서는 Pod 번호와 DX1·DX2의 VLAN, 피어 IP, BGP 키만 넣으면 됩니다. 온프레미스 대역은 Pod 번호를 넣으면 자동으로 채워집니다.

DX1 값은 `tgw-nat-vif1`, DX2 값은 `tgw-nat-vif2`의 **Peerings** 탭에서 가져옵니다. 피어 IP는 `/29`를 붙인 채로 넣어도 됩니다.

<div class="gen-form">
  <fieldset class="gen-group gen-common">
    <legend>공통 · 온프레미스와 BGP</legend>
    <label><span class="gen-badge">1</span><span class="gen-name">Pod 번호 N<small>실습 장비 페이지의 podN</small></span><input id="g-pod" inputmode="numeric" placeholder="89"></label>
    <label><span class="gen-badge">2</span><span class="gen-name">온프레미스 대역<small>CIDR · AWS에 광고 · Pod 번호로 채움</small></span><input id="g-lan" placeholder="172.20.N.0/24" spellcheck="false"></label>
    <label><span class="gen-badge">3</span><span class="gen-name">Loopback1 주소<small>AWS에 광고 · 미리 채움 · 비우면 만들지 않음</small></span><input id="g-loop" value="10.200.0.1/32" data-default="10.200.0.1/32" spellcheck="false"></label>
    <label><span class="gen-badge">4</span><span class="gen-name">라우터 ASN<small>1-3의 BGP ASN · 미리 채움</small></span><input id="g-asn" inputmode="numeric" value="65000" data-default="65000"></label>
    <label><span class="gen-badge">5</span><span class="gen-name">Amazon 쪽 ASN<small>1-1의 Amazon-side ASN · 미리 채움</small></span><input id="g-amzasn" inputmode="numeric" value="65300" data-default="65300"></label>
  </fieldset>
  <fieldset class="gen-group gen-dx1">
    <legend>DX1 · <code>awsdx1_…</code> · <code>tgw-nat-vif1</code></legend>
    <label><span class="gen-badge">6</span><span class="gen-name">라우터 인터페이스<small>물리 인터페이스 이름 · 미리 채움</small></span><input id="g-if1" value="GigabitEthernet1" data-default="GigabitEthernet1" spellcheck="false"></label>
    <label><span class="gen-badge">7</span><span class="gen-name">VLAN</span><input id="g-vlan1" inputmode="numeric" placeholder="189"></label>
    <label><span class="gen-badge">8</span><span class="gen-name">Your router peer IP<small>라우터 쪽 IP</small></span><input id="g-my1" placeholder="169.254.96.54/29"></label>
    <label><span class="gen-badge">9</span><span class="gen-name">Amazon router peer IP<small>AWS 쪽 IP</small></span><input id="g-aws1" placeholder="169.254.96.49/29"></label>
    <label><span class="gen-badge">10</span><span class="gen-name">BGP authentication key</span><input id="g-key1" autocomplete="off" spellcheck="false"></label>
  </fieldset>
  <fieldset class="gen-group gen-dx2">
    <legend>DX2 · <code>awsdx2_…</code> · <code>tgw-nat-vif2</code></legend>
    <label><span class="gen-badge">11</span><span class="gen-name">라우터 인터페이스<small>물리 인터페이스 이름 · 미리 채움</small></span><input id="g-if2" value="GigabitEthernet2" data-default="GigabitEthernet2" spellcheck="false"></label>
    <label><span class="gen-badge">12</span><span class="gen-name">VLAN</span><input id="g-vlan2" inputmode="numeric" placeholder="289"></label>
    <label><span class="gen-badge">13</span><span class="gen-name">Your router peer IP<small>라우터 쪽 IP</small></span><input id="g-my2" placeholder="169.254.96.46/29"></label>
    <label><span class="gen-badge">14</span><span class="gen-name">Amazon router peer IP<small>AWS 쪽 IP</small></span><input id="g-aws2" placeholder="169.254.96.41/29"></label>
    <label><span class="gen-badge">15</span><span class="gen-name">BGP authentication key</span><input id="g-key2" autocomplete="off" spellcheck="false"></label>
  </fieldset>
</div>

## 4-1-3. 만들어진 설정 { #output }

줄 앞의 번호는 그 줄에 들어간 값입니다. 입력 칸을 누르면 그 값이 들어가는 줄이 강조됩니다. 번호는 복사되지 않습니다. 빈 줄은 읽기 쉽게 넣은 것으로, 붙여 넣어도 온프레미스 라우터(`rtN`)가 무시합니다.

<p><button id="g-copy" class="md-button md-button--primary" type="button">복사</button> <span id="g-msg" class="gen-msg" aria-live="polite"></span></p>

<pre id="g-out" class="gen-out"></pre>

<script>
(function () {
  const ids = ["pod", "lan", "loop", "asn", "amzasn", "if1", "vlan1", "my1", "aws1", "key1", "if2", "vlan2", "my2", "aws2", "key2"];
  const optional = ["pod", "loop"];
  const badge = Object.fromEntries(ids.map((k, i) => [k, i + 1]));
  const group = (k) => (/1$/.test(k) ? "dx1" : /2$/.test(k) ? "dx2" : "common");
  const el = (k) => document.getElementById("g-" + k);
  const circ = (k) => "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮"[badge[k] - 1];

  const addr = (v) => v.trim().replace(/\/\d+$/, "");
  const lenOf = (v, def) => {
    const m = v.trim().match(/\/(\d+)$/);
    return m ? parseInt(m[1], 10) : def;
  };
  const isIp = (v) => /^\d{1,3}(\.\d{1,3}){3}$/.test(addr(v)) && addr(v).split(".").every((o) => +o <= 255);
  const isPrefix = (v, def) => isIp(v) && lenOf(v, def) >= 0 && lenOf(v, def) <= 32;
  const toInt = (v) => addr(v).split(".").reduce((a, o) => a * 256 + +o, 0);
  const toIp = (n) => [24, 16, 8, 0].map((s) => (n >>> s) & 255).join(".");
  const maskInt = (len) => (len === 0 ? 0 : (0xffffffff << (32 - len)) >>> 0);
  const mask = (v, def) => toIp(maskInt(lenOf(v, def)));
  const netOf = (v, def) => toIp((toInt(v) & maskInt(lenOf(v, def))) >>> 0);
  const same29 = (a, b) => Math.floor(toInt(a) / 8) === Math.floor(toInt(b) / 8);
  const inRange = (v, lo, hi) => /^\d+$/.test(v) && +v >= lo && +v <= hi;
  const lanFromPod = (p) => (inRange(p, 1, 99) ? "172.20." + p + ".0/24" : "");

  let focused = null;
  let text = "";
  let lanManual = false;

  function check(v) {
    const p = [];
    if (v.pod && !inRange(v.pod, 1, 99)) p.push(circ("pod") + " Pod 번호는 1–99");
    if (v.lan && !isPrefix(v.lan, 24)) p.push(circ("lan") + " 대역 형식(예: 172.20.89.0/24)");
    else if (v.lan && netOf(v.lan, 24) !== addr(v.lan)) p.push(circ("lan") + " 대역의 시작 주소가 아님(" + netOf(v.lan, 24) + "/" + lenOf(v.lan, 24) + ")");
    if (v.loop && !isPrefix(v.loop, 32)) p.push(circ("loop") + " 주소 형식(예: 10.200.0.1/32)");
    for (const k of ["asn", "amzasn"]) if (v[k] && !inRange(v[k], 1, 4294967295)) p.push(circ(k) + " ASN은 숫자");
    if (v.asn && v.asn === v.amzasn) p.push(circ("asn") + circ("amzasn") + " 두 ASN이 같음");
    for (const n of ["1", "2"]) {
      const f = v["if" + n];
      if (f && /[\s.]/.test(f)) p.push(circ("if" + n) + " 인터페이스 이름만(.VLAN 없이)");
      else if (f && /^(gigabitethernet|gi)\s*4$/i.test(f)) p.push(circ("if" + n) + " 워크숍의 GigabitEthernet4는 실습 장비 연결용이라 쓰지 않음");
      if (v["vlan" + n] && !inRange(v["vlan" + n], 1, 4094)) p.push(circ("vlan" + n) + " VLAN은 1–4094");
      for (const k of ["my" + n, "aws" + n]) if (v[k] && !isIp(v[k])) p.push(circ(k) + " IP 형식");
      const a = v["my" + n], b = v["aws" + n];
      if (a && b && isIp(a) && isIp(b)) {
        if (addr(a) === addr(b)) p.push(circ("my" + n) + circ("aws" + n) + " 두 IP가 같음");
        else if (!same29(a, b)) p.push(circ("my" + n) + circ("aws" + n) + " 같은 인터페이스의 값인지 확인(/29가 다름)");
      }
    }
    if (v.if1 && v.vlan1 && (v.if1 + "." + v.vlan1).toLowerCase() === (v.if2 + "." + v.vlan2).toLowerCase())
      p.push(circ("if1") + circ("vlan1") + circ("if2") + circ("vlan2") + " 두 서브인터페이스가 같음");
    return p;
  }

  function render() {
    const v = Object.fromEntries(ids.map((k) => [k, el(k).value.trim()]));
    const missing = ids.filter((k) => !optional.includes(k) && !v[k]);
    const problems = check(v);
    const msg = el("msg");
    msg.classList.toggle("gen-warn", problems.length > 0);
    if (problems.length) msg.textContent = "확인하세요: " + problems.join(" · ");
    else if (missing.length) msg.textContent = "아직 비어 있는 값: " + missing.map(circ).join(" ");
    else {
      const changed = ids.filter((k) => el(k).dataset.default !== undefined && v[k] !== el(k).dataset.default);
      if (lanManual && v.lan !== lanFromPod(v.pod)) changed.unshift("lan");
      msg.textContent = changed.length
        ? "모든 값을 넣었습니다. " + changed.map(circ).join("") + " 워크숍 값과 다릅니다. 내 환경에 맞는 값인지 확인하세요."
        : "모든 값을 넣었습니다.";
    }

    const P = (k, ph) => v[k] || ph;
    const A = (n) => (v["aws" + n] ? addr(v["aws" + n]) : "<AWS_IP" + n + ">");
    const L = [];
    const add = (s, ...keys) => L.push({ s, keys });
    const gap = () => add("");
    add("configure terminal");
    for (const n of ["1", "2"]) {
      gap();
      add("interface " + P("if" + n, "<IF" + n + ">") + "." + P("vlan" + n, "<VLAN" + n + ">"), "if" + n, "vlan" + n);
      add(" description DX" + n + " transit VIF");
      add(" encapsulation dot1Q " + P("vlan" + n, "<VLAN" + n + ">"), "vlan" + n);
      add(" ip address " + (v["my" + n] ? addr(v["my" + n]) + " " + mask(v["my" + n], 29) : "<MY_IP" + n + "> 255.255.255.248"), "my" + n);
      add(" bfd interval 300 min_rx 300 multiplier 3");
    }
    if (v.loop) {
      gap();
      add("interface Loopback1");
      add(" description source that no NAT rule matches");
      add(" ip address " + addr(v.loop) + " " + mask(v.loop, 32), "loop");
    }
    gap();
    add("router bgp " + P("asn", "<MY_ASN>"), "asn");
    add(" bgp log-neighbor-changes");
    for (const n of ["1", "2"]) {
      gap();
      add(" neighbor " + A(n) + " remote-as " + P("amzasn", "<AMAZON_ASN>"), "aws" + n, "amzasn");
      add(" neighbor " + A(n) + " password " + P("key" + n, "<BGP_KEY" + n + ">"), "aws" + n, "key" + n);
      add(" neighbor " + A(n) + " fall-over bfd", "aws" + n);
    }
    gap();
    add(" address-family ipv4");
    add("  network " + (v.lan ? addr(v.lan) + " mask " + mask(v.lan, 24) : "<ONPREM_NET> mask <ONPREM_MASK>"), "lan");
    if (v.loop) add("  network " + netOf(v.loop, 32) + " mask " + mask(v.loop, 32), "loop");
    add("  maximum-paths 2");
    for (const n of ["1", "2"]) add("  neighbor " + A(n) + " activate", "aws" + n);
    add(" exit-address-family");
    gap();
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
        b.className = "gen-badge gen-" + group(k);
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

  el("pod").addEventListener("input", () => {
    if (!lanManual) el("lan").value = lanFromPod(el("pod").value.trim());
  });
  el("lan").addEventListener("input", () => {
    lanManual = el("lan").value.trim() !== "";
  });
  ids.forEach((k) => {
    el(k).addEventListener("input", render);
    el(k).addEventListener("focus", () => { focused = k; render(); });
    el(k).addEventListener("blur", () => { focused = null; render(); });
  });
  el("copy").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(text);
      el("msg").classList.remove("gen-warn");
      el("msg").textContent = "복사했습니다. 온프레미스 라우터(rtN) 터미널에 붙여 넣으세요.";
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

## 4-1-4. 넣는 값 { #inputs }

| 번호 | 값 | 찾는 곳 |
|---|---|---|
| 1 | Pod 번호 N | 실습 장비 페이지(`podN`) |
| 2 | 온프레미스 대역 | Pod 번호를 넣으면 `172.20.N.0/24`로 채워짐 |
| 3 | Loopback1 주소 | 워크숍 값 `10.200.0.1/32`가 미리 채워져 있음 |
| 4 | 라우터 ASN | 1-3에서 전송 가상 인터페이스에 넣은 **BGP ASN**. 워크숍 값 `65000`이 미리 채워져 있음 |
| 5 | Amazon 쪽 ASN | 1-1에서 Direct Connect gateway에 넣은 **Amazon-side ASN**. 워크숍 값 `65300`이 미리 채워져 있음 |
| 6, 11 | 라우터 인터페이스 | 워크숍 값 `GigabitEthernet1`, `GigabitEthernet2`가 미리 채워져 있음 |
| 7, 12 | VLAN | 실습 장비 페이지, 또는 전송 가상 인터페이스 상세의 **VLAN** |
| 8, 13 | Your router peer IP | 전송 가상 인터페이스 상세 → **Peerings** 탭 |
| 9, 14 | Amazon router peer IP | 전송 가상 인터페이스 상세 → **Peerings** 탭 |
| 10, 15 | BGP authentication key | 전송 가상 인터페이스 상세 → **Peerings** 탭 |

DX1(6–10)은 `awsdx1_…` 위에 만든 `tgw-nat-vif1`, DX2(11–15)는 `awsdx2_…` 위에 만든 `tgw-nat-vif2`의 값입니다. 두 인터페이스의 값을 섞으면 BGP가 올라오지 않습니다. 생성기는 같은 인터페이스의 두 피어 IP가 같은 `/29`에 있는지 확인해 알려 줍니다.

ASN은 BGP에서 서로를 알아보는 번호입니다. 만들어진 설정의 두 ASN이 콘솔에 넣은 값과 다르면 BGP가 올라오지 않습니다. 콘솔에 다른 값을 넣었다면 미리 채워진 값을 그 값으로 바꾸세요.

## 4-1-5. 설정이 하는 일 { #explain }

| 부분 | 쓰는 값 | 하는 일 |
|---|---|---|
| `GigabitEthernet1.<VLAN>`, `GigabitEthernet2.<VLAN>` | 6–8, 11–13 | 전송 가상 인터페이스마다 하나씩 만드는 서브인터페이스. VLAN 번호와 라우터 쪽 IP, 회선 끊김을 빨리 알아채는 BFD를 설정 |
| `Loopback1` `10.200.0.1/32` | 3 | NAT 규칙에 없는 주소. 주소가 바뀌지 않는 경우를 확인할 때 씀 |
| `router bgp 65000` | 4 | 온프레미스 라우터(`rtN`) 자신의 ASN으로 BGP를 켬 |
| `neighbor … remote-as 65300` | 5, 9·10, 14·15 | Direct Connect gateway(AS 65300)와 BGP로 경로를 주고받음. BGP 키와 BFD를 함께 씀 |
| `network 172.20.N.0 …`, `network 10.200.0.1 …` | 2, 3 | 온프레미스 대역과 Loopback1을 AWS에 광고 |
| `maximum-paths 2` | — | 두 전송 가상 인터페이스로 받은 같은 경로를 함께 씀(ECMP) |

## 4-1-6. 내 환경에서 다시 쓰기 { #reuse }

회선 2개에 전송 가상 인터페이스를 하나씩 두는 구성이라면 이 생성기를 그대로 쓸 수 있습니다. 미리 채워진 값을 내 환경 값으로 바꾸면 됩니다.

- 만들어지는 설정은 Cisco IOS XE 문법입니다. 다른 장비는 문법이 다릅니다.
- 온프레미스 대역(②)은 라우터의 라우팅 테이블에 **똑같은 대역**이 있어야 광고됩니다. 없으면 `network` 명령만으로는 광고되지 않습니다.
- Loopback1(③)은 이 워크숍의 시험용입니다. 필요 없으면 칸을 비웁니다. 그러면 관련 줄이 만들어지지 않습니다.
- BFD 값(300ms × 3)과 `maximum-paths 2`는 워크숍 값입니다. 내 환경의 기준에 맞는지 확인하세요.
- 운영 장비에 넣기 전에 만들어진 설정을 꼭 검토하세요.

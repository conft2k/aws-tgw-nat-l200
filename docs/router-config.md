# 라우터 설정 생성기

[실습 1-4](lab1.md#lab1-4)에서 적은 값을 넣으면 라우터에 붙여 넣을 설정이 만들어집니다. 값은 이 브라우저 안에서만 쓰이고 어디로도 보내지지 않습니다.

<div class="gen-grid">
  <label>Pod 번호 N<input id="g-pod" inputmode="numeric" placeholder="89"></label>
  <label>VIF 1 VLAN<input id="g-vlan1" inputmode="numeric" placeholder="189"></label>
  <label>VIF 2 VLAN<input id="g-vlan2" inputmode="numeric" placeholder="289"></label>
  <label>VIF 1 Your router peer IP<input id="g-my1" placeholder="169.254.96.54/29"></label>
  <label>VIF 1 Amazon router peer IP<input id="g-aws1" placeholder="169.254.96.49/29"></label>
  <label>VIF 1 BGP authentication key<input id="g-key1" autocomplete="off" spellcheck="false"></label>
  <label>VIF 2 Your router peer IP<input id="g-my2" placeholder="169.254.96.46/29"></label>
  <label>VIF 2 Amazon router peer IP<input id="g-aws2" placeholder="169.254.96.41/29"></label>
  <label>VIF 2 BGP authentication key<input id="g-key2" autocomplete="off" spellcheck="false"></label>
</div>

<p><button id="g-copy" class="md-button md-button--primary" type="button">복사</button> <span id="g-msg" class="gen-msg"></span></p>

<textarea id="g-out" class="gen-out" readonly spellcheck="false"></textarea>

<script>
(function () {
  const ids = ["pod", "vlan1", "vlan2", "my1", "aws1", "key1", "my2", "aws2", "key2"];
  const el = (k) => document.getElementById("g-" + k);
  const ip = (v) => v.trim().replace(/\/\d+$/, "");
  const maskOf = (v) => {
    const m = v.trim().match(/\/(\d+)$/);
    const len = m ? parseInt(m[1], 10) : 29;
    const n = len === 0 ? 0 : (0xffffffff << (32 - len)) >>> 0;
    return [24, 16, 8, 0].map((s) => (n >>> s) & 255).join(".");
  };
  const isIp = (v) => /^\d{1,3}(\.\d{1,3}){3}$/.test(ip(v)) && ip(v).split(".").every((o) => +o <= 255);
  function render() {
    const v = Object.fromEntries(ids.map((k) => [k, el(k).value.trim()]));
    const missing = ids.filter((k) => !v[k]);
    const bad = ["my1", "aws1", "my2", "aws2"].filter((k) => v[k] && !isIp(v[k]));
    const msg = el("msg");
    if (bad.length) msg.textContent = "IP 형식을 확인하세요: " + bad.join(", ");
    else if (missing.length) msg.textContent = "아직 비어 있는 값: " + missing.length + "개";
    else msg.textContent = "";
    const P = (k, ph) => v[k] || ph;
    const lines = [
      "configure terminal",
      "interface GigabitEthernet1." + P("vlan1", "<VLAN1>"),
      " description DX1 transit VIF",
      " encapsulation dot1Q " + P("vlan1", "<VLAN1>"),
      " ip address " + (v.my1 ? ip(v.my1) + " " + maskOf(v.my1) : "<MY_IP1> 255.255.255.248"),
      " bfd interval 300 min_rx 300 multiplier 3",
      "interface GigabitEthernet2." + P("vlan2", "<VLAN2>"),
      " description DX2 transit VIF",
      " encapsulation dot1Q " + P("vlan2", "<VLAN2>"),
      " ip address " + (v.my2 ? ip(v.my2) + " " + maskOf(v.my2) : "<MY_IP2> 255.255.255.248"),
      " bfd interval 300 min_rx 300 multiplier 3",
      "interface Loopback1",
      " description source that no NAT rule matches",
      " ip address 10.200.0.1 255.255.255.255",
      "router bgp 65000",
      " bgp log-neighbor-changes",
    ];
    for (const n of ["1", "2"]) {
      const a = v["aws" + n] ? ip(v["aws" + n]) : "<AWS_IP" + n + ">";
      lines.push(" neighbor " + a + " remote-as 65300");
      lines.push(" neighbor " + a + " password " + P("key" + n, "<BGP_KEY" + n + ">"));
      lines.push(" neighbor " + a + " fall-over bfd");
    }
    lines.push(" address-family ipv4");
    lines.push("  network 172.20." + P("pod", "<POD>") + ".0 mask 255.255.255.0");
    lines.push("  network 10.200.0.1 mask 255.255.255.255");
    lines.push("  maximum-paths 2");
    for (const n of ["1", "2"]) {
      lines.push("  neighbor " + (v["aws" + n] ? ip(v["aws" + n]) : "<AWS_IP" + n + ">") + " activate");
    }
    lines.push(" exit-address-family", "end");
    el("out").value = lines.join("\n") + "\n";
  }
  ids.forEach((k) => el(k).addEventListener("input", render));
  el("copy").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(el("out").value);
      el("msg").textContent = "복사했습니다. 라우터 웹 터미널에 붙여 넣으세요.";
    } catch (e) {
      el("out").select();
      el("msg").textContent = "아래 상자를 선택해 직접 복사하세요(Ctrl+C).";
    }
  });
  render();
})();
</script>

## 넣는 값 { #inputs }

| 값 | 찾는 곳 |
|---|---|
| Pod 번호 N | 참가자 정보 페이지(`podN`) |
| VIF 1·2 VLAN | 참가자 정보 페이지, 또는 전송 가상 인터페이스 상세의 **VLAN** |
| Your router peer IP, Amazon router peer IP, BGP authentication key | 전송 가상 인터페이스 상세 → **Peerings** 탭 |

피어 IP는 `/29`를 붙인 채로 넣어도 됩니다. 첫 번째 인터페이스는 `awsdx1_…`(라우터 `GigabitEthernet1`), 두 번째는 `awsdx2_…`(`GigabitEthernet2`)의 것입니다.

## 설정이 하는 일 { #explain }

| 부분 | 하는 일 |
|---|---|
| `GigabitEthernet1.<VLAN1>`, `GigabitEthernet2.<VLAN2>` | 전송 가상 인터페이스마다 하나씩 만드는 서브인터페이스. VLAN 번호와 라우터 쪽 IP, 회선 끊김을 빨리 알아채는 BFD를 설정 |
| `Loopback1` `10.200.0.1/32` | NAT 규칙에 없는 주소. 주소가 바뀌지 않는 경우를 확인할 때 씀 |
| `neighbor … remote-as 65300` | Direct Connect gateway(AS 65300)와 BGP로 경로를 주고받음. BGP 키와 BFD를 함께 씀 |
| `network 172.20.N.0 …`, `network 10.200.0.1 …` | 온프레미스 LAN과 Loopback1을 AWS에 광고 |
| `maximum-paths 2` | 두 전송 가상 인터페이스로 받은 같은 경로를 함께 씀(ECMP) |

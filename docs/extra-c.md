# 3-3. 지표와 로그로 확인하기

1:1 NAT(Network Address Translation)가 정말 주소를 바꿨는지 CloudWatch 지표와 Flow Logs로 확인합니다. [2-3-7](lab2.md#lab2-7)에서 통신이 되는 것을 확인한 뒤 진행합니다.

- **지표**: 연결마다 주소를 바꾼 패킷 수를 셉니다.
- **Flow Logs**: 어떤 주소 사이에 트래픽이 오갔는지 기록합니다.

지표와 로그는 몇 분 늦게 나타납니다. 그래서 먼저 온프레미스 VM(Virtual Machine, `vmN`) 터미널에서 트래픽을 만듭니다. `100.64.2.10`은 VPC-A EC2의 NAT 주소입니다([용어집](glossary.md)).

```bash
ping -c 200 100.64.2.10
```

ping은 1초에 하나씩 보내므로 3분 20초쯤 걸립니다. 끝에 `200 packets transmitted, 200 received, 0% packet loss`가 나오는지 확인합니다. 그다음 3~5분 기다립니다.

![지표와 로그가 기록하는 곳: DXGW 연결과 VPC-A 연결에서 PacketsInNAT·PacketsOutNAT(Transit Gateway 기준)가 늘어나고 VPC-B 연결은 0이다. TGW Flow Logs는 Transit Gateway 하나에 설정하고 기록은 연결·방향별로 남으며, 사전 테스트에서는 양 끝의 실제 주소가 남았다. VPC Flow Logs는 EC2 ENI와 Transit Gateway ENI에서 ENI 기준 방향으로 VPC 안에서 보이는 주소를 기록한다](images/diagrams/extra-c-observability.png)

| 보는 곳 | 내용 |
|---|---|
| **CloudWatch 지표** | NAT 규칙이 실제로 번역한 연결에서만 늘어납니다(VPC-B 연결은 0). |
| **TGW(Transit Gateway) Flow Logs** | 양 끝의 실제 주소를 남깁니다: `172.20.N.10` → `172.20.N.10`(사전 테스트에서 관찰). |
| **VPC Flow Logs** | VPC 안에서 보이는 주소를 남깁니다: `pkt-srcaddr` `100.64.1.10`. |
| **확인 방법** | 상대에게 보인 주소는 VPC Flow Logs나 패킷 캡처로 봅니다. |

그림의 선: 검은 실선 화살표는 요청, 초록 점선 화살표는 응답, 회색 점선 화살표는 로그 전송입니다.

TGW Flow Logs에는 온프레미스 VM과 VPC-A EC2 사이 트래픽이 양 끝의 실제 주소로 기록됩니다(`172.20.N.10 → 172.20.N.10`). 출발지는 NAT로 바꾸기 전, 목적지는 원래 주소로 되돌린 뒤의 주소입니다. 이 동작은 AWS 문서에 설명이 없고, 사전 테스트에서 이렇게 기록되는 것을 확인했습니다. 상대에게 어떤 주소로 보였는지는 VPC Flow Logs로 봅니다([3-3-2](#c2)).

## 3-3-1. NAT 지표 { #c1 }

1. **CloudWatch** 콘솔 → **Metrics** → **Classic metrics**를 엽니다. **Browse** 탭에서 **TransitGateway** → **Per-TransitGatewayAttachment Metrics**를 고릅니다.

    목록에 다른 Transit Gateway의 줄이 보이면, 검색창에 내 Transit Gateway ID(**VPC** 콘솔 → **Transit gateways**)를 넣어 내 연결만 남깁니다. 지운 리소스의 지표도 마지막 데이터가 들어온 뒤 약 2주 동안 목록에 보입니다.

2. 세 Transit Gateway 연결의 `PacketsInNAT`, `PacketsOutNAT`을 선택합니다.
3. **Graphed metrics** 탭에서 **Statistic**을 **Sum**으로 바꿉니다.
4. 그래프 종류를 **Number**로 바꿉니다. **Options** 탭의 **Value**에서 **Time range value**를 고릅니다(시간 범위 전체의 합을 보여 줍니다).
5. 오른쪽 위 시간 범위를 **Custom**으로 ping을 보낸 몇 분에 맞춥니다.

![CloudWatch 지표(Number): DXGW와 VPC-A 연결의 PacketsInNAT·PacketsOutNAT가 모두 200, VPC-B 연결의 PacketsInNAT·PacketsOutNAT는 0](images/console/extraC-01-nat-metrics.png){ .shot }

들어올 때와 나갈 때는 Transit Gateway를 기준으로 합니다.

| 지표 | 뜻 |
|---|---|
| `PacketsInNAT` | 그 연결로 Transit Gateway에 **들어올 때** 출발지 주소를 NAT 대역으로 바꾼(SNAT, Source Network Address Translation) 패킷 수 |
| `PacketsOutNAT` | 그 연결로 Transit Gateway에서 **나갈 때** 목적지 주소를 원래 대역으로 되돌린(DNAT, Destination Network Address Translation) 패킷 수 |
| `PacketDropCountBlackhole` | Blackhole 경로 때문에 버린 패킷 수([3-2-1](extra-b.md#b1)에서 늘어남) |

ping 하나는 네 지표에 하나씩 집계됩니다([4-2-1](concepts.md#how)).

- **요청**: DXGW(Direct Connect gateway) 연결 `PacketsInNAT`(출발지 `172.20.N.10` → `100.64.1.10`) → VPC-A 연결 `PacketsOutNAT`(목적지 `100.64.2.10` → `172.20.N.10`)
- **응답**: VPC-A 연결 `PacketsInNAT`(출발지 `172.20.N.10` → `100.64.2.10`) → DXGW 연결 `PacketsOutNAT`(목적지 `100.64.1.10` → `172.20.N.10`)

**결과**

- 다음 세 조건이 맞으면 DXGW 연결과 VPC-A 연결의 `PacketsInNAT`, `PacketsOutNAT`이 **모두 200**입니다.
    - ping 200개가 모두 성공했습니다(`0% packet loss`).
    - 시간 범위가 ping을 보낸 시간 전체를 덮습니다.
    - 시간 범위 안에 다른 트래픽이 없습니다.
- 시간 범위에 다른 실습 트래픽(확인용 ping, `curl` 등)이 들어가면 값이 200보다 커집니다. 사전 테스트에서는 확인용 ping 3개가 들어가 203이었습니다.
- VPC-B 연결의 NAT 지표는 **0**입니다. 규칙이 없으니 바꾼 것이 없습니다.

## 3-3-2. 두 Flow Logs 비교 { #c2 }

**CloudWatch** 콘솔 → **Logs** → **Log Analytics**를 엽니다. 위에 **Welcome to the new Log Analytics experience** 안내가 나오면 그대로 두고 진행합니다.

1. **Query scope**에서 **Log group** 옆의 **All**을 누르고 로그 그룹을 고릅니다. 쿼리 편집기 첫 줄이 고른 로그 그룹의 `SOURCE ...`로 바뀝니다.
2. 시간 범위를 **1h**로 둡니다.
3. 첫 줄(`SOURCE ...`)은 그대로 두고, 그 아래 줄을 지운 뒤 아래 쿼리를 붙여 넣습니다. 쿼리 안의 `N`을 내 Pod 번호로 바꾼 다음 **Run**을 누릅니다.

**TGW Flow Logs** — 로그 그룹 `/tgwnat/tgw-flow-logs`

```text
parse @message "* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *" as ver, rtype, acct, tgw, attachment, sacct, dacct, svpc, dvpc, ssub, dsub, seni, deni, saz, daz, pair, srcaddr, dstaddr, srcport, dstport, proto, packets, bytes, tstart, tend, status, iptype, nr, bh, mtu, ttl, flags, region, direction, s1, s2
| filter srcaddr = "172.20.N.10" and dstaddr = "172.20.N.10"
| display @timestamp, attachment, direction, srcaddr, dstaddr, packets
| sort @timestamp desc
| limit 10
```

![Log Analytics: TGW Flow Logs에서 srcaddr와 dstaddr가 모두 172.20.89.10인 기록](images/console/extraC-02-tgw-flow-logs.png){ .shot }

TGW Flow Logs는 Transit Gateway 하나에 설정 하나지만, 기록은 줄마다 나뉩니다.

- 한 줄은 연결 하나(`attachment`), 방향 하나(`direction`), 집계 구간 하나의 기록입니다. 이 실습의 집계 구간은 최대 60초입니다.
- 화면에는 연결 ID 두 개가 보입니다. DXGW 연결과 VPC-A 연결입니다. 어느 ID가 어느 연결인지는 **Transit gateway attachments**에서 ID를 보고 맞춥니다. 화면(Pod 89)에서는 `tgw-attach-019edf6bfc5c552ec`가 DXGW 연결, `tgw-attach-09f9236b10b2535a8`가 VPC-A 연결입니다.
- 한 연결에 `ingress`와 `egress`가 모두 있습니다. 요청과 응답이 그 연결을 서로 반대 방향으로 지나기 때문입니다. 요청과 응답 모두 주소가 `172.20.N.10`이라 주소만으로는 둘을 구분할 수 없습니다.
- `packets`는 그 구간의 패킷 수입니다. ping은 1초에 하나씩이라 꽉 찬 구간은 60 안팎입니다(화면의 60, 59). ping이 구간 중간에 시작하거나 끝나면 60보다 작습니다(화면의 54).

**VPC Flow Logs** — 로그 그룹 `/tgwnat/vpc-flow-logs`

```text
parse @message "* * * * * * * * * * * * * * * * * * * *" as ver, vpc, eni, srcaddr, dstaddr, pkt_srcaddr, pkt_dstaddr, srcport, dstport, proto, packets, bytes, flags, iptype, tstart, tend, action, status, direction, path
| filter pkt_srcaddr = "100.64.1.10" or pkt_dstaddr = "100.64.1.10"
| display @timestamp, eni, direction, srcaddr, dstaddr, pkt_srcaddr, pkt_dstaddr, action
| sort @timestamp desc
| limit 10
```

이 로그 그룹에는 VPC-A와 VPC-B의 기록이 함께 들어 있습니다. 결과는 `srcaddr`, `dstaddr`로 나눠 봅니다.

- `srcaddr`나 `dstaddr`가 `10.1.1.x`이면 VPC-B의 기록입니다. 이 과제에서는 보지 않습니다.
- `srcaddr`나 `dstaddr`가 `172.20.N.10`이고 반대쪽이 `100.64.1.10`이면 VPC-A EC2의 ENI(Elastic Network Interface)입니다.
- `srcaddr`나 `dstaddr`가 Transit Gateway 서브넷(`172.20.N.224/28`, `172.20.N.240/28`)의 주소이면 Transit Gateway의 ENI입니다.

VPC Flow Logs의 `direction`은 기록한 ENI를 기준으로 합니다. 지표의 들어올 때·나갈 때(Transit Gateway 기준)와 다릅니다.

- **요청**: Transit Gateway의 ENI에서 나가고(`egress`), VPC-A EC2의 ENI로 들어옵니다(`ingress`).
- **응답**: VPC-A EC2의 ENI에서 나가고(`egress`), Transit Gateway의 ENI로 들어옵니다(`ingress`).

![Log Analytics: VPC Flow Logs에서 VPC-A EC2의 ENI가 100.64.1.10과 172.20.89.10 사이 트래픽을 기록](images/console/extraC-03-vpc-flow-logs.png){ .shot }

화면 읽는 법(Pod 89):

- `eni-08a82e9d2ec788943`은 VPC-A EC2의 ENI입니다. 상대가 `100.64.1.10`으로 보입니다. `ingress` 줄은 `100.64.1.10` → `172.20.89.10`, `egress` 줄은 그 반대 방향입니다.
- `eni-0a8ef51a60bb5fdcd`는 Transit Gateway의 ENI(`172.20.89.233`)입니다. `egress` 줄은 `srcaddr`에, `ingress` 줄은 `dstaddr`에 이 ENI 자신의 주소가 들어갑니다.
- 이 화면은 VPC-A EC2에서 `100.64.1.10`으로 ping을 보내 찍었습니다. 위의 ping(온프레미스 VM → `100.64.2.10`)을 보내면 어느 줄이 요청이고 어느 줄이 응답인지만 바뀌고, 화면에 보이는 줄의 모양은 같습니다. ENI ID는 Pod마다 다릅니다.

**결과**

- **TGW Flow Logs**는 온프레미스 VM(`vmN`)과 VPC-A EC2 사이 트래픽을 `172.20.N.10 → 172.20.N.10`처럼 **양 끝의 실제 주소**로 남깁니다. 출발지는 바뀌기 전, 목적지는 되돌린 뒤의 주소입니다. 두 주소를 함께 단 패킷이 실제로 지나간 구간은 없습니다. 이 내용은 사전 테스트에서 관찰한 것이고 문서에는 설명이 없습니다.
- **VPC Flow Logs**는 VPC 안에서 보이는 주소를 남깁니다. 기록은 ENI(EC2나 Transit Gateway가 VPC 안에서 쓰는 네트워크 인터페이스)마다 남습니다.
    - VPC-A EC2의 ENI 기록에는 상대가 `100.64.1.10`으로 보입니다.
    - Transit Gateway의 ENI 기록에는 그 ENI 자신의 주소가 들어갑니다. 이 예에서는 `egress`이면 `srcaddr`에, `ingress`이면 `dstaddr`에 들어갑니다. 패킷의 실제 출발지와 목적지는 `pkt_srcaddr`, `pkt_dstaddr`로 봅니다.
- 그래서 "상대에게 어떤 주소로 보였나"는 VPC Flow Logs나 패킷 캡처로 확인합니다.

# 4-2. 1:1 NAT 개념과 제약

이 워크숍에서는 온프레미스 VM(Virtual Machine)과 VPC-A EC2가 같은 주소 `172.20.N.10`을 씁니다. `N`은 내 Pod 번호입니다(Pod 89이면 `172.20.89.10`). 주소가 같으면 Transit Gateway는 그 주소로 가는 패킷을 한쪽으로만 보냅니다. 그래서 응답이 엉뚱한 곳으로 가거나, 다른 쪽에는 아예 닿지 못합니다([2-3-2](lab2.md#lab2-2)).

Transit Gateway 1:1 NAT(Network Address Translation)는 장비의 실제 주소를 그대로 둡니다. 대신 Transit Gateway를 지날 때 서로 다른 주소(NAT 대역)로 보이게 합니다. 온프레미스 VM은 `100.64.1.10`으로, VPC-A EC2는 `100.64.2.10`으로 보입니다.

이 페이지에서는 주소를 바꾸는 방식과 필요한 경로(4-2-1), 지켜야 할 조건(4-2-2), 바꾸거나 끌 때 주의할 점(4-2-3), 설계할 때 생각할 점(4-2-4)을 정리합니다. 공식 문서([1:1 NAT](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat.html), [How it works](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat-how-it-works.html), [Routing](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat-routing.html), [Configure](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat-configure.html))를 바탕으로 쉽게 정리했습니다.

규칙에는 대역 두 개를 넣습니다. 콘솔의 **Source CIDR**은 바꾸기 전의 실제 대역(원래 대역), **NAT CIDR**은 상대에게 보이는 대역(NAT 대역)입니다([용어 풀이](glossary.md)).

![1:1 NAT 규칙은 Transit Gateway의 DXGW 연결과 VPC-A 연결에 각각 있다. 그 연결로 Transit Gateway에 들어오는 패킷은 출발지 172.20.N.0/24를 NAT 대역(DXGW 연결 100.64.1.0/24, VPC-A 연결 100.64.2.0/24)으로 바꾸고(SNAT), 그 연결로 나가는 패킷은 목적지 NAT 대역을 172.20.N.0/24로 되돌린다(DNAT). VPC-B 연결에는 규칙이 없다](images/diagrams/concept-snat-dnat.png)

## 4-2-1. 어떻게 동작하나 { #how }

1:1 NAT는 두 가지 일로 나뉩니다.

1. **주소 바꾸기**: Transit Gateway 연결의 **Enable NAT Gateway support**를 켜고 1:1 NAT 규칙(원래 대역 → NAT 대역)을 넣으면, 그 연결을 지나는 패킷의 주소를 바꿉니다.
2. **NAT 대역으로 가는 경로 만들기**: 바뀐 주소로 오는 패킷을 어느 연결로 보낼지 Transit Gateway 라우팅 테이블에 경로가 있어야 합니다.
    - 예를 들어 VPC-A EC2는 온프레미스 VM에 `100.64.1.10`으로 보냅니다. 그래서 `100.64.1.0/24` → DXGW(Direct Connect gateway) 연결 경로가 필요합니다. 온프레미스 라우터는 이 대역을 광고하지 않습니다.
    - **NAT system routes**를 켜 두면 Transit Gateway가 이 경로를 **System** 유형으로 자동으로 만듭니다.
    - 끄면 온프레미스가 BGP(Border Gateway Protocol)로 광고하거나(**Propagated**) 정적 경로를 직접 넣어야(**Static**) 합니다.

NAT system routes를 꺼도 주소 변환은 계속됩니다. 경로를 누가 만드느냐만 바뀝니다.

**Enable NAT Gateway support**는 Transit Gateway 연결(attachment)에서 1:1 NAT를 켜는 설정입니다. 이름에 NAT Gateway가 들어가지만 VPC의 NAT 게이트웨이 리소스와는 관계가 없습니다. 이 설정을 켜야 그 연결의 1:1 NAT 규칙이 동작합니다. 켜면 연결의 **1:1 NAT** 탭에 **NAT Gateway support: Enabled**로 보입니다.

**규칙이 적용되는 곳과 방향**

규칙은 그 규칙을 둔 Transit Gateway 연결을 지나는 패킷에만 적용됩니다. 들어옴과 나감은 그 연결에서 Transit Gateway를 기준으로 봅니다.

- 그 연결로 Transit Gateway에 **들어오는** 패킷: 출발지가 원래 대역 안에 있으면 NAT 대역으로 바꿉니다(SNAT, Source Network Address Translation). 목적지는 따지지 않습니다.
- 그 연결로 Transit Gateway에서 **나가는** 패킷: 목적지가 NAT 대역 안에 있으면 원래 대역으로 되돌립니다(DNAT, Destination Network Address Translation).

요청과 응답 모두 같은 규칙을 따릅니다. 온프레미스 VM이 VPC-A EC2(`100.64.2.10`)로 보내면 주소가 이렇게 바뀝니다.

| 패킷 | 지나는 곳 | 바뀌는 주소 |
|---|---|---|
| 요청 | DXGW 연결로 들어올 때(SNAT) | 출발지 `172.20.N.10` → `100.64.1.10` |
| 요청 | VPC-A 연결로 나갈 때(DNAT) | 목적지 `100.64.2.10` → `172.20.N.10` |
| 응답 | VPC-A 연결로 들어올 때(SNAT) | 출발지 `172.20.N.10` → `100.64.2.10` |
| 응답 | DXGW 연결로 나갈 때(DNAT) | 목적지 `100.64.1.10` → `172.20.N.10` |

그래서 연결마다 규칙 하나가 양쪽 방향을 모두 처리합니다. 단계별 흐름은 [2-3-7](lab2.md#lab2-7)에 있습니다.

규칙은 Transit Gateway 연결(attachment)의 설정입니다. Direct Connect gateway나 게이트웨이 연결(gateway association)이 주소를 바꾸는 것이 아닙니다. "DXGW 연결"은 Direct Connect gateway를 Transit Gateway에 붙인 Transit Gateway 연결을 뜻합니다.

**1:1로 바꿉니다**

원래 대역과 NAT 대역은 접두사 길이가 같아야 합니다. 앞의 네트워크 부분만 바뀌고, 호스트 부분(호스트 비트)과 포트는 그대로입니다. 이 실습은 `/24`라서 마지막 숫자가 그대로입니다. 그래서 온프레미스 VM `172.20.N.10`은 늘 `100.64.1.10`으로, VPC-A EC2 `172.20.N.10`은 늘 `100.64.2.10`으로 보입니다.

**연결을 기억하지 않습니다(stateless)**

Transit Gateway는 연결을 기억하지 않고 패킷마다 규칙만 보고 주소를 바꿉니다. 그래서 어느 쪽에서 먼저 통신을 시작해도 똑같이 동작합니다.

**자세한 동작**

| 항목 | 설명 |
|---|---|
| 주소 종류 | IPv4만 됩니다 |
| 적용 중 | 바꾸는 동안에도 연결은 **available** 상태를 유지합니다. NAT 상태는 enabling → enabled, 규칙은 activated가 됩니다 |
| VPC 연결의 NAT system routes | 항상 켜져 있어 바꿀 수 없습니다 |
| VPC 연결의 경로 | 규칙의 원래 대역이 VPC 대역과 똑같으면, Transit Gateway가 VPC 대역 경로(**Propagated**)를 지우고 NAT 대역 경로(**System**)를 대신 만듭니다 |
| VPC 대역의 일부만 바꿀 때 | 원래 대역이 VPC 대역과 다르면(예: `/16` VPC 안의 `/24`) 경로가 생기지 않습니다. NAT 대역 정적 경로를 직접 추가해야 합니다 |
| DXGW 연결의 NAT system routes | 켜고 끌 수 있습니다(기본값 켬). BGP를 쓰는 Site-to-Site VPN 연결도 같습니다 |
| DXGW 연결의 System 경로 상태 | 온프레미스가 원래 대역과 겹치는 경로를 광고하는 동안만 **Active**입니다. 광고가 사라지면 **Blackhole**이 됩니다([3-2-1](extra-b.md#b1)) |
| System 경로가 생기는 곳 | 그 연결이 전파(propagation)하는 라우팅 테이블에만 생깁니다 |
| DXGW 연결에서 끌 때 | 온프레미스 라우터가 NAT 대역을 광고합니다([추가 과제 3-2](extra-b.md)). 사전 테스트에서 관찰한 것: 원래 대역 광고도 계속 필요했습니다([3-2-2](extra-b.md#b2)) |
| 경로 우선순위 | 같은 대역이면 정적(Static) > System > 접두사 목록(Prefix list) > Propagated 순서로 쓰입니다. 접두사 목록 경로는 라우팅 테이블에서 관리형 접두사 목록을 참조해 만든 경로입니다 |

**제대로 바뀌었는지 확인하기**

- **설정**: 두 연결의 **1:1 NAT** 탭에 **NAT Gateway support: Enabled**, 규칙 상태 **Activated**가 보입니다.
- **주소**: 양쪽에서 상대의 NAT 주소로 보냅니다. 받는 쪽에서 상대가 각각 `100.64.1.10`(온프레미스 VM), `100.64.2.10`(VPC-A EC2)으로 보입니다([2-3-7](lab2.md#lab2-7)).
- **포트**: 출발지 포트를 `40000`으로 정해 보내면(`curl --local-port 40000`) 받는 쪽에도 `40000`으로 보입니다.
- **지표**: `PacketsInNAT`(들어올 때 바꾼 수), `PacketsOutNAT`(나갈 때 되돌린 수)이 규칙이 쓰인 연결에 기록됩니다([추가 과제 3-3](extra-c.md)).

## 4-2-2. 지켜야 할 조건 { #limits }

| 조건 | 내용 |
|---|---|
| 대역 크기 | 원래 대역과 NAT 대역의 접두사 길이(예: /24)가 같아야 합니다 |
| NAT 대역 | 사설 주소(RFC 1918, RFC는 Request for Comments) 또는 `100.64.0.0/10`만 쓸 수 있습니다 |
| 원래 대역 | 멀티캐스트(224.0.0.0/4), 링크 로컬(169.254.0.0/16)은 안 됩니다 |
| 같은 연결 안 | 규칙끼리 대역이 겹치면 안 됩니다 |
| 다른 연결 사이의 원래 대역 | 겹쳐도 됩니다. 이 겹침이 1:1 NAT로 풀려는 문제입니다(이 실습: 온프레미스와 VPC-A 모두 `172.20.N.0/24`) |
| 다른 연결 사이의 NAT 대역 | 겹쳐도 **검사하지 않습니다**. 통신할 다른 네트워크의 실제 대역이나 다른 NAT 대역과 충돌하지 않게 직접 정합니다(이 실습: 온프레미스 `100.64.1.0/24`, VPC-A `100.64.2.0/24`) |
| 규칙 없이 켜기 | 안 됩니다. 끌 때는 규칙을 남긴 채 **NAT Gateway support**만 끕니다 |
| appliance mode | appliance mode가 켜진 VPC 연결에는 NAT를 켤 수 없습니다. appliance mode는 한 흐름의 양방향 트래픽이 같은 가용 영역을 지나게 하는 VPC 연결 설정입니다(방화벽 같은 장비를 둘 때 씀) |
| 안 되는 연결 | Cloud WAN peering·route table 연결, Network Function, Client VPN. Network Function은 AWS Network Firewall을 Transit Gateway에 직접 붙일 때 생기는 연결로, 콘솔에 유형이 **Network function**으로 보입니다([공식 문서](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nf-fw.html)) |
| 바꾸는 중 | enabling·disabling 중에는 다시 바꿀 수 없습니다 |
| 한도 | 연결당 규칙 50개, Transit Gateway당 1,000개 |
| 권한 | `ec2:ModifyTransitGatewayAttachmentNatConfiguration`, `ec2:GetTransitGatewayAttachmentNatConfiguration`(`Describe*` 권한에 들어 있지 않음) |

## 4-2-3. 바꾸거나 끌 때 { #change }

- 저장하면 화면의 규칙 목록 전체가 기존 규칙을 대신합니다. 지운 규칙은 잠시 deleting으로 보일 수 있습니다.
- 끄면 주소 바꾸기가 멈추고 규칙은 deactivated로 남습니다. 다시 켜면 activated가 됩니다.
- 켜고 끄거나 규칙을 바꿀 때 잠깐 패킷이 버려질 수 있습니다. 문서는 유지 보수 시간에 바꾸고, 상대가 쓰는 주소는 변경이 끝난 뒤에 바꾸라고 권합니다.
- 이 실습처럼 VPC 연결에서 규칙의 원래 대역이 VPC 대역과 같으면, Transit Gateway의 VPC 대역 경로가 NAT 대역 경로로 바뀝니다. 그래서 Transit Gateway를 거쳐 그 VPC의 실제 주소로 접근하던 다른 네트워크는 더 이상 닿지 못합니다. 이후에는 NAT 주소(예: `100.64.2.10`)를 써야 합니다.
- 원래 대역이 VPC 대역의 일부이면 VPC 대역 경로는 남습니다. 하지만 그 일부 대역에서 나가는 패킷의 출발지는 NAT 주소로 바뀝니다. 그래서 상대 쪽의 경로와 보안 그룹이 NAT 대역을 받아들여야 합니다.
- 상대 쪽 설정은 미리 준비해 둡니다. 그리고 **NAT Gateway support: Enabled**와 규칙 상태 **Activated**를 확인한 뒤에 상대가 NAT 주소를 쓰게 바꿉니다.

## 4-2-4. 설계할 때 생각할 점 { #design }

- **DNS**: 1:1 NAT는 패킷의 주소만 바꾸고, DNS 응답에 담긴 주소는 바꾸지 않습니다. 상대 네트워크가 쓰는 DNS가 실제 주소를 돌려준다면, NAT 주소를 돌려주도록 레코드나 DNS 설정을 따로 준비해야 합니다(추론, 문서에서 DNS 설명은 찾지 못함).
- **원래 경로**: NAT 뒤에도 온프레미스가 광고한 원래 경로는 Transit Gateway에 남습니다([3-1-3](extra-a.md#a3)).
- **UDP**: 사전 테스트에서 UDP(User Datagram Protocol)도 TCP(Transmission Control Protocol), ICMP(Internet Control Message Protocol)와 같은 방식으로 바뀌는 것을 확인했습니다.
- **pending 상태**: 문서에 나오지 않지만, 사전 테스트에서 규칙을 처음 저장한 직후 API 응답에 잠시 pending이 보였습니다. 콘솔에서는 바로 activated로 보였습니다.

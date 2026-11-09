# 1-3. 용어 풀이

워크숍에 자주 나오는 말을 쉽게 풀었습니다. 콘솔에 보이는 영어 이름을 함께 적었습니다.

## 1-3-1. 연결 관련

| 용어 | 콘솔 이름 | 뜻 |
|---|---|---|
| Pod | — | 참가자마다 배정된 온프레미스 라우터와 Linux VM 묶음 |
| Pod 번호 N | PodNumber | 내 Pod의 번호. 실습 장비 페이지(`podN`)에서 확인합니다. 주소와 이름의 `N`을 이 번호로 바꿔 읽습니다. Pod 89라면 `rt89`, `vm89`, `172.20.89.10`입니다. CloudFormation 스택의 **PodNumber** 파라미터에도 이 번호를 넣습니다 |
| 온프레미스 | — | 회사 데이터센터처럼 AWS 밖에 있는 네트워크. 이 워크숍에서는 여러분의 Pod(온프레미스 라우터와 온프레미스 VM) |
| 온프레미스 라우터 | — | Pod의 라우터(`rtN`) |
| 온프레미스 VM | — | Pod의 Linux VM(`vmN`, `172.20.N.10`) |
| 온프레미스 대역 | — | 온프레미스 VM이 있는 네트워크 대역. 이 워크숍에서는 `172.20.N.0/24`이고, AWS에 BGP로 광고합니다 |
| hosted connection(호스팅 연결) | Hosted connection | Direct Connect 파트너가 만들어 여러분 계정에 넘겨 준 회선. 수락해야 쓸 수 있습니다. VLAN 번호는 파트너가 정합니다 |
| VLAN | VLAN | 한 회선에서 여러 통로를 나누는 번호. hosted connection마다 정해져 있습니다 |
| ASN | ASN | BGP에서 자율 시스템(AS, 한 조직이 관리하는 네트워크)을 구분하는 번호. 이 워크숍은 온프레미스 라우터 65000, Direct Connect gateway 65300, Transit Gateway 65400을 씁니다 |
| 전송 가상 인터페이스(transit VIF) | Transit virtual interface | hosted connection 위에 만드는 논리 인터페이스. 이 위에서 온프레미스 라우터와 AWS가 BGP로 경로를 주고받습니다. 이 워크숍은 2개를 만듭니다 |
| Direct Connect 게이트웨이(DXGW) | Direct Connect gateway | 전송 가상 인터페이스와 Transit Gateway를 이어 주는 AWS 리소스 |
| 게이트웨이 연결 | Gateway association | DXGW 쪽에서 DXGW와 Transit Gateway를 잇는 설정. 온프레미스에 광고할 대역(허용된 접두사)을 여기서 정합니다. 주소를 바꾸지는 않습니다 |
| 허용된 접두사 | Allowed prefixes | 게이트웨이 연결에 적은 대역. 적은 그대로 온프레미스 라우터에 광고됩니다 |
| Transit Gateway 연결(attachment) | Transit gateway attachment | VPC나 DXGW를 Transit Gateway에 붙인 것. 1:1 NAT 설정과 규칙은 이 연결마다 둡니다 |
| DXGW 연결 | Transit gateway attachment(**Resource type**: **Direct Connect Gateway**) | DXGW를 Transit Gateway에 붙인 Transit Gateway 연결. 게이트웨이 연결을 만들면 생깁니다. 온프레미스 쪽 1:1 NAT 규칙은 여기에 둡니다 |
| VPC-A 연결 | Transit gateway attachment(`tgwnat-attach-vpc-a`) | VPC-A를 Transit Gateway에 붙인 Transit Gateway 연결 |
| BGP | — | 라우터끼리 "이 대역은 나에게 보내라"고 경로를 알려 주는 방법. 알려 주는 것을 **광고**라고 합니다 |
| BFD | — | 회선이 끊긴 것을 BGP보다 빠르게 알아채는 기능. BGP와 함께 씁니다 |

## 1-3-2. 1:1 NAT 관련

1:1 NAT는 두 가지 일로 나뉩니다. **주소 바꾸기**는 **Enable NAT Gateway support**와 규칙이 맡습니다. **NAT 대역으로 가는 경로 만들기**는 라우팅 테이블의 일이고, [NAT system routes](#1-3-3)를 켜 두면 Transit Gateway가 자동으로 만듭니다. 자세한 동작은 [4-2-1](concepts.md#how)에 있습니다.

| 용어 | 콘솔 이름 | 뜻 |
|---|---|---|
| 1:1 NAT | 1:1 NAT | 대역을 크기(접두사 길이)가 같은 다른 대역으로 한 주소씩 짝지어 바꾸는 기능. 온프레미스의 `172.20.N.10`은 `100.64.1.10`으로, VPC-A의 `172.20.N.10`은 `100.64.2.10`으로 바뀝니다 |
| 호스트 비트 | — | 주소에서 대역 안의 개별 호스트를 구분하는 뒷부분. 1:1 NAT는 앞의 네트워크 부분만 바꾸고 호스트 비트와 포트는 그대로 둡니다. 이 실습은 `/24`라서 마지막 숫자(`.10`)가 그대로입니다 |
| NAT Gateway support | Enable NAT Gateway support | Transit Gateway 연결에서 1:1 NAT를 켜는 설정. 이 설정을 켜야 그 연결의 규칙이 동작합니다. 이름에 NAT Gateway가 들어가지만 VPC의 NAT 게이트웨이 리소스와는 관계가 없습니다 |
| 규칙 | Rule | **Rule number**, 원래 대역, NAT 대역으로 된 한 줄. 그 규칙을 둔 Transit Gateway 연결을 지나는 패킷에만 적용됩니다 |
| 원래 대역, 원래 주소 | Source CIDR | 바뀌기 전의 실제 주소. 이 워크숍에서는 `172.20.N.0/24` |
| NAT 대역, NAT 주소 | NAT CIDR | 바뀐 뒤의 주소. 이 워크숍에서는 `100.64.1.0/24`(온프레미스), `100.64.2.0/24`(VPC-A) |
| 출발지 주소 바꾸기(SNAT) | — | 규칙을 둔 연결로 Transit Gateway에 **들어오는** 패킷의 출발지가 원래 대역에 있으면 NAT 주소로 바꾸는 것. 예: DXGW 연결로 들어올 때 `172.20.N.10` → `100.64.1.10` |
| 목적지 주소 되돌리기(DNAT) | — | 규칙을 둔 연결로 Transit Gateway에서 **나가는** 패킷의 목적지가 그 규칙의 NAT 대역에 있으면 원래 주소로 되돌리는 것. 예: VPC-A 연결로 나갈 때 `100.64.2.10` → `172.20.N.10` |
| 상태 없음 | Stateless | 연결을 기억하지 않고 패킷마다 규칙만 보고 주소를 바꾸는 방식. 그래서 어느 쪽에서 먼저 통신을 시작해도 똑같이 동작합니다 |

요청과 응답 모두 같은 규칙을 따릅니다. 온프레미스 VM이 VPC-A EC2에 보내는 예입니다.

- **요청**: DXGW 연결로 들어올 때 출발지 `172.20.N.10` → `100.64.1.10`(SNAT). VPC-A 연결로 나갈 때 목적지 `100.64.2.10` → `172.20.N.10`(DNAT).
- **응답**: VPC-A 연결로 들어올 때 출발지 `172.20.N.10` → `100.64.2.10`(SNAT). DXGW 연결로 나갈 때 목적지 `100.64.1.10` → `172.20.N.10`(DNAT).

## 1-3-3. 라우팅 테이블 관련

| 용어 | 콘솔 이름 | 뜻 |
|---|---|---|
| 전파 경로 | Propagated | 연결된 VPC나 온프레미스(BGP 광고)에게서 자동으로 배운 경로 |
| 정적 경로 | Static | 라우팅 테이블에 사람이 직접 넣은 경로. 같은 대역이면 다른 유형보다 먼저 쓰입니다 |
| System 경로 | System | NAT system routes가 켜져 있을 때 Transit Gateway가 NAT 대역으로 가는 길로 스스로 만든 경로 |
| Blackhole | Blackhole | 갈 곳이 없어 패킷을 버리는 경로 상태. 예: DXGW 연결의 System 경로는 온프레미스가 원래 대역과 겹치는 경로를 광고하지 않으면 Blackhole이 됩니다 |
| NAT system routes | NAT system routes | NAT 대역(예: `100.64.1.0/24`)으로 오는 패킷을 그 연결로 보내는 경로를 Transit Gateway가 **System** 유형으로 자동으로 만들게 하는 설정. 주소 변환을 켜고 끄는 설정은 아닙니다 |
| ECMP | — | Equal-Cost Multi-Path. 같은 목적지로 가는 **비용이 같은** 경로 여러 개를 함께 써서 트래픽을 나눠 보내는 방식. 이 워크숍에서는 두 전송 가상 인터페이스로 받은 같은 경로를 함께 씁니다 |

**NAT system routes**를 꺼도 주소 변환은 계속됩니다. 경로를 누가 만드느냐만 바뀝니다. 끄면 온프레미스가 BGP로 광고하거나(**Propagated**) 정적 경로를 직접 넣어야(**Static**) 합니다. VPC 연결은 항상 켜져 있고, DXGW 연결과 BGP를 쓰는 Site-to-Site VPN 연결만 켜고 끌 수 있습니다. 자세한 조건은 [2-3-4의 설명 상자](lab2.md#lab2-4)에 있습니다.

## 1-3-4. 그 밖에

| 용어 | 콘솔 이름 | 뜻 |
|---|---|---|
| CloudFormation 스택 | Stack | 템플릿 파일 하나로 여러 AWS 리소스를 한 번에 만들고 지우는 단위 |
| EC2 Instance Connect Endpoint | EC2 Instance Connect Endpoint | 인터넷 주소가 없는 EC2에 브라우저로 접속하게 해 주는 엔드포인트 |
| 보안 그룹 | Security group | EC2에 들어오고 나가는 트래픽을 허용하는 규칙 모음 |
| ENI | Network interface | EC2나 Transit Gateway가 VPC 안에서 쓰는 네트워크 인터페이스 |
| Flow Logs | Flow logs | 어떤 주소 사이에 트래픽이 오갔는지 남기는 기록. Transit Gateway용과 VPC용이 있습니다 |
| Loopback | Loopback | 라우터 안의 가상 인터페이스. 회선과 상관없이 늘 켜져 있습니다 |
| Loopback1 | Loopback1 | 온프레미스 라우터에 만든 Loopback(`10.200.0.1`). NAT 규칙의 원래 대역 밖이라 주소가 바뀌지 않는 경우를 확인할 때 씁니다 |
| Null0 | Null0 | 패킷을 버리는 가상 인터페이스. 여기서는 BGP로 광고할 경로를 만들 때만 씁니다 |

# 용어 풀이

워크숍에 자주 나오는 말을 쉽게 풀었습니다. 콘솔에 보이는 영어 이름을 함께 적었습니다.

## 연결 관련

| 용어 | 콘솔 이름 | 뜻 |
|---|---|---|
| 온프레미스 | — | 회사 데이터센터처럼 AWS 밖에 있는 네트워크. 이 워크숍에서는 여러분의 Pod(라우터와 Linux VM) |
| hosted connection | Hosted connection | Direct Connect 파트너가 만들어 여러분 계정에 넘겨 준 회선. 수락해야 쓸 수 있습니다. VLAN 번호는 파트너가 정합니다 |
| 전송 가상 인터페이스 | Transit virtual interface (transit VIF) | hosted connection 위에 만드는 논리 인터페이스. 이 위에서 온프레미스 라우터와 AWS가 BGP로 경로를 주고받습니다 |
| Direct Connect 게이트웨이(DXGW) | Direct Connect gateway | 전송 가상 인터페이스와 Transit Gateway를 이어 주는 AWS 리소스 |
| 게이트웨이 연결 | Gateway association | DXGW와 Transit Gateway를 잇는 설정. 온프레미스에 광고할 대역(허용된 접두사)을 여기서 정합니다 |
| 허용된 접두사 | Allowed prefixes | 게이트웨이 연결에 적은 대역. 적은 그대로 온프레미스 라우터에 광고됩니다 |
| Transit Gateway 연결 | Transit gateway attachment | VPC나 DXGW를 Transit Gateway에 붙인 것. 1:1 NAT 규칙은 이 연결마다 둡니다 |
| BGP | — | 라우터끼리 "이 대역은 나에게 보내라"고 경로를 알려 주는 방법. 알려 주는 것을 **광고**라고 합니다 |
| BFD | — | 회선이 끊겼는지 빠르게 알아채는 기능. BGP와 함께 씁니다 |

## 1:1 NAT 관련

| 용어 | 콘솔 이름 | 뜻 |
|---|---|---|
| 1:1 NAT | 1:1 NAT | 대역을 다른 대역으로 한 주소씩 짝지어 바꾸는 기능. `172.20.N.10`은 항상 `100.64.1.10`처럼 같은 자리의 주소로 바뀝니다 |
| 원래 대역, 원래 주소 | Source CIDR | 바뀌기 전의 실제 주소. 이 워크숍에서는 `172.20.N.0/24` |
| NAT 대역, NAT 주소 | NAT CIDR | 바뀐 뒤의 주소. 이 워크숍에서는 `100.64.1.0/24`(온프레미스), `100.64.2.0/24`(VPC-A) |
| 출발지 주소 바꾸기(SNAT) | — | Transit Gateway로 **들어오는** 패킷의 보낸 쪽 주소를 NAT 주소로 바꾸는 것 |
| 목적지 주소 되돌리기(DNAT) | — | Transit Gateway에서 **나가는** 패킷의 받는 쪽 NAT 주소를 원래 주소로 되돌리는 것 |
| 상태 없음 | Stateless | 연결을 기억하지 않고 패킷마다 규칙대로 바꾸는 방식. 그래서 어느 쪽에서 먼저 보내도 똑같이 동작합니다 |

## 라우팅 테이블 관련

| 용어 | 콘솔 이름 | 뜻 |
|---|---|---|
| 전파 경로 | Propagated | 연결된 VPC나 온프레미스에게서 자동으로 배운 경로 |
| System 경로 | System | 1:1 NAT 때문에 Transit Gateway가 스스로 만든 경로 |
| Blackhole | Blackhole | 갈 곳이 없어 패킷을 버리는 경로 상태 |
| NAT system routes | NAT system routes | NAT 대역 경로(System 경로)를 Transit Gateway가 만들게 할지 정하는 설정 |
| ECMP | — | 같은 경로가 둘 있을 때 둘에 나눠 보내는 것. 이 워크숍에서는 전송 가상 인터페이스 2개를 함께 씁니다 |

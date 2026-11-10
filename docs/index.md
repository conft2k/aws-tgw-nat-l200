# 1-1. 소개

회사 네트워크(온프레미스)와 AWS의 VPC가 **같은 IP 대역**을 쓰면, 둘을 연결해도 서로 통신할 수 없습니다. 주소를 바꾸려면 많은 시간이 듭니다.

이 워크숍에서는 Transit Gateway의 **1:1 NAT(Network Address Translation)**로 이 문제를 풉니다. 주소는 그대로 두고, Transit Gateway를 지날 때만 다른 주소로 바꿔 보이게 합니다.

| 항목 | 내용 |
|---|---|
| 대상 | VPC, Transit Gateway, Direct Connect를 들어 본 분 |
| 레벨 | 200 |
| 시간 | 3시간(발표 1시간, 실습 2시간) |
| 준비물 | 웹 브라우저. 참가자마다 AWS 계정 1개와 실습용 온프레미스 장비(Pod)를 드립니다 |
| 리전 | 아시아 태평양(서울) `ap-northeast-2` |

모르는 용어는 [용어 풀이](glossary.md)를 보세요.

## 1-1-1. 왜 1:1 NAT가 필요한가요 { #why }

사설 IP 대역(RFC 1918, RFC는 Request for Comments)이 서로 겹치는 일은 드물지 않습니다. AWS 문서는 다음과 같은 경우를 예로 듭니다.

- 기업 인수·합병으로 두 회사의 네트워크를 이을 때
- 협력사(서드 파티) 네트워크와 연결할 때
- 다른 클라우드와 연결할 때
- 팀마다 IP 대역을 따로 정해 쓰다가 나중에 서로 이을 때

두 네트워크가 같은 대역을 쓰면 같은 Transit Gateway에 붙여도 서로 통신할 수 없습니다. 1:1 NAT가 없을 때는 둘 중 하나를 골라야 했습니다.

| 방법 | 어려운 점 |
|---|---|
| 한쪽 네트워크의 주소를 바꾸기 | 그 네트워크의 서버와 장비 주소, 그 주소를 쓰는 설정을 모두 바꿔야 합니다 |
| NAT 장비 두기 | 트래픽이 지나는 여러 지점에 NAT 장비를 배포하고 직접 관리해야 합니다 |

Transit Gateway 1:1 NAT를 쓰면 Transit Gateway가 직접 주소를 바꿉니다. 따로 배포하거나 관리할 NAT 장비가 없고, VPC의 NAT 게이트웨이를 만들 필요도 없습니다. Transit Gateway 연결마다 대역 대 대역 규칙을 넣으면, Transit Gateway는 그 연결을 지나는 트래픽 가운데 규칙에 맞는 IPv4 주소만 양방향으로 바꿉니다. 기존 네트워크의 주소는 그대로 둡니다.

AWS 문서가 드는 활용 사례는 세 가지입니다.

| 사례 | 내용 |
|---|---|
| 겹치는 IP 대역 | 위와 같이 대역이 겹치는 네트워크를 주소를 바꾸지 않고 연결합니다. 이 워크숍이 다루는 사례입니다 |
| 내부 주소 숨기기 | 협력사나 다른 사업부가 VPC의 애플리케이션에 접속할 때, 상대에게는 바뀐 주소만 보이고 내부 주소는 드러나지 않습니다 |
| IPv4 주소 부족 | 사설 대역이 모자랄 때 CGNAT(Carrier-Grade NAT) 대역을 NAT 대역으로 써서 쓸 수 있는 주소를 늘립니다 |

대역이 겹치는 네트워크를 이을 때 AWS 문서가 권하는 방법은 **겹치는 네트워크마다 각자의 NAT 대역으로 바꾸는 것**입니다. 그래서 이 실습은 온프레미스와 VPC-A 양쪽에 규칙을 넣습니다.

대역이 똑같으면 한쪽만 바꿔서는 통신이 되지 않습니다. 규칙이 없는 쪽에서 보면 상대에게 보내는 응답의 목적지가 자기 대역 안의 주소입니다. VPC는 그 패킷을 Transit Gateway로 보내지 않고 VPC 안에서 처리합니다.

NAT 대역은 CGNAT 대역(RFC 6598, `100.64.0.0/10`)처럼 따로 떼어 둔 주소 블록에서, 겹치는 네트워크마다 하나씩 나눠 줍니다. NAT 대역은 Transit Gateway나 연결된 다른 네트워크 어디에서도 쓰지 않는 대역이어야 합니다.

1:1 NAT는 IPv4만 바꾸고 포트는 바꾸지 않습니다. 지원하는 연결 종류와 그 밖의 조건은 [4-2-2. 지켜야 할 조건](concepts.md#limits)에 있습니다. 원문은 [1:1 NAT in AWS Transit Gateway](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat.html)와 [How 1:1 NAT works](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat-how-it-works.html)를 보세요.

## 1-1-2. 워크숍의 목표 { #goal }

이 워크숍은 IP 대역이 겹치는 온프레미스와 VPC를 이어야 하는 분이, 주소를 바꾸지 않고 Transit Gateway 1:1 NAT로 연결할 수 있는지 직접 판단할 수 있도록 만들었습니다. 실제 Direct Connect 회선과 온프레미스 라우터로 운영 환경과 같은 구성을 만들어 봅니다.

워크숍을 마치면 다음을 할 수 있습니다.

1. Direct Connect로 온프레미스를 Transit Gateway에 연결합니다(온프레미스 → Direct Connect → Direct Connect gateway → Transit Gateway → VPC).
2. 같은 대역을 쓰면 어떤 문제가 생기는지 직접 보고 설명합니다.
3. 콘솔에서 1:1 NAT를 설정하고, 온프레미스와 VPC-A가 NAT 주소로 통신하는 것을 확인합니다.
4. 양쪽 서버가 기록한 상대 주소로 주소가 바뀐 것을 확인합니다.
5. 실제 환경에 적용할 때 정할 것(NAT 대역, NAT 대역으로 가는 경로를 만드는 방법, 보안 그룹)을 설명합니다.
6. NAT 경로를 바꿔 보고 지표와 Flow Logs로 동작을 관측합니다(추가 과제).

## 1-1-3. 시나리오

여러분의 Pod 번호를 **N**이라고 하겠습니다(예: 89).

![워크숍 구성도: 왼쪽의 Pod N 온프레미스 라우터(rtN)에서 전송 가상 인터페이스 2개가 AWS Direct Connect를 지나 Direct Connect gateway에 닿고, Direct Connect gateway가 오른쪽의 Transit Gateway에 연결된다. Transit Gateway에서 위로 VPC-A, 아래로 VPC-B(NAT 없음)가 연결된다. DXGW 연결과 VPC-A 연결에 1:1 NAT 규칙이 있고, Transit Gateway 라우팅 테이블에 NAT 대역의 system 경로가 있다](images/architecture.png)

그림에서 DXGW(Direct Connect gateway) 쪽과 VPC-A 쪽에 적힌 1:1 NAT 규칙은 둘 다 Transit Gateway 연결의 설정입니다. 라우팅 테이블의 system 경로는 NAT 대역으로 가는 경로입니다.

그림의 태그는 누가 만드는지를 뜻합니다.

- **콘솔에서 직접**: 실습하면서 AWS 콘솔에서 직접 만듭니다([2-2](lab1.md), [2-3](lab2.md)).
- **CloudFormation**: 실습 스택이 미리 배포합니다. 태그 붙은 VPC는 안의 리소스까지 배포합니다([2-1-3](lab0.md#lab0-3)).

그림의 구성은 다음과 같습니다.

- 온프레미스 대역은 `172.20.N.0/24`입니다. 온프레미스 라우터가 이 대역을 AWS에 광고합니다([2-2-5](lab1.md#lab1-5)).
- AWS의 VPC-A도 **똑같이** `172.20.N.0/24`를 씁니다. 이 겹침 때문에 생기는 문제는 [2-3-2](lab2.md#lab2-2)에서 확인합니다.
- 온프레미스 라우터(`rtN`)는 Direct Connect로 AWS에 연결됩니다([2-2](lab1.md)).
- 온프레미스 라우터에는 시험용 주소 **Loopback1**(`10.200.0.1`)도 만들어 AWS에 광고합니다. Loopback1은 라우터 안의 가상 인터페이스이고, 이 주소는 어느 대역과도 겹치지 않습니다. 다음 두 가지를 확인할 때 출발지로 씁니다.
    - NAT를 넣기 전: VPC-A와 겹치는 온프레미스 대역 대신 이 주소로 보내, VPC-B까지 가는 기본 연결을 확인합니다([2-2-6](lab1.md#lab1-6)).
    - NAT를 넣은 뒤: 이 주소는 바뀌지 않는 것을 확인합니다([3-1-4](extra-a.md#a4)).
- 비교를 위해 VPC-B(`10.1.1.0/24`)도 있습니다. VPC-B 연결에는 NAT 규칙을 넣지 않습니다([3-1](extra-a.md)).

1:1 NAT를 적용하면 서로 이렇게 보입니다.

| 네트워크 | 실제 주소 | 상대에게 보이는 주소 | 다루는 실습 |
|---|---|---|---|
| 온프레미스 | `172.20.N.0/24` | `100.64.1.0/24` | [2-3-4](lab2.md#lab2-4) |
| VPC-A | `172.20.N.0/24` | `100.64.2.0/24` | [2-3-5](lab2.md#lab2-5) |
| VPC-B | `10.1.1.0/24` | 그대로 | [3-1-1](extra-a.md#a1) |
| 온프레미스 라우터 Loopback1 | `10.200.0.1` | 그대로 | [3-1-4](extra-a.md#a4) |

앞의 네트워크 부분(`172.20.N`)만 바뀌고, 마지막 숫자(호스트 비트)와 포트는 그대로입니다. 예를 들어 온프레미스 VM(Virtual Machine, `vmN`)과 VPC-A EC2는 둘 다 `172.20.N.10`을 씁니다. 하지만 온프레미스 VM은 VPC-A EC2를 `100.64.2.10`으로 봅니다. VPC-A EC2는 온프레미스 VM을 `100.64.1.10`으로 봅니다.

1:1 NAT는 두 가지 일로 나뉩니다.

- **주소 바꾸기**: Transit Gateway 연결(attachment)에서 **Enable NAT Gateway support**를 켜고 1:1 NAT 규칙(원래 대역 → NAT 대역)을 넣습니다. 이 실습에서는 DXGW 연결과 VPC-A 연결에 넣습니다([2-3-4](lab2.md#lab2-4), [2-3-5](lab2.md#lab2-5)). DXGW 연결은 Direct Connect gateway를 Transit Gateway에 붙인 Transit Gateway 연결입니다. Direct Connect gateway나 게이트웨이 연결(gateway association)이 주소를 바꾸는 것이 아닙니다.
- **NAT 대역으로 가는 경로**: 바뀐 주소로 온 패킷을 어느 연결로 보낼지, Transit Gateway 라우팅 테이블에 경로가 있어야 합니다. 예를 들어 `100.64.2.10`으로 가는 패킷은 `100.64.2.0/24` → VPC-A 경로를 따라 VPC-A 연결로 갑니다. 이 실습에서는 **NAT system routes**가 켜져 있어, Transit Gateway가 이 경로를 **System** 유형으로 자동으로 만듭니다([2-3-6](lab2.md#lab2-6)).

자세한 동작은 [4-2-1. 어떻게 동작하나](concepts.md#how)를 보세요.

온프레미스 VM이 VPC-A EC2에 접속하면 주소가 이렇게 바뀝니다.

1. 온프레미스 VM은 VPC-A EC2의 NAT 주소 `100.64.2.10`으로 보냅니다.
2. DXGW 연결로 Transit Gateway에 들어올 때 출발지 `172.20.N.10`이 `100.64.1.10`으로 바뀝니다(SNAT, Source Network Address Translation).
3. VPC-A 연결로 나갈 때 목적지 `100.64.2.10`이 실제 주소 `172.20.N.10`으로 되돌아갑니다(DNAT, Destination Network Address Translation).
4. 응답은 같은 규칙으로 반대로 바뀝니다. VPC-A 연결로 들어올 때 출발지가 `100.64.2.10`으로 바뀌고, DXGW 연결로 나갈 때 목적지가 `172.20.N.10`으로 되돌아갑니다.

이 흐름은 [2-3-7. 통신해 보기](lab2.md#lab2-7)에서 직접 확인합니다.

VPC-B와 Loopback1이 그대로인 이유는 서로 다릅니다.

- **VPC-B**: VPC-B 연결에 규칙이 없어서 VPC-B 주소는 바뀌지 않습니다. 하지만 온프레미스 VM이 VPC-B로 보내는 패킷도 DXGW 연결로 들어올 때 출발지가 `100.64.1.10`으로 바뀝니다([3-1-1](extra-a.md#a1)).
- **Loopback1**: `10.200.0.1`은 DXGW 연결 규칙의 원래 대역(`172.20.N.0/24`) 밖에 있어서 바뀌지 않습니다([3-1-4](extra-a.md#a4)).

## 1-1-4. 진행 순서

| 시간 | 구분 | 내용 |
|---|---|---|
| 0:00–1:00 | 발표 | Transit Gateway와 사용 패턴, 새 기능과 1:1 NAT, 실습 안내 |
| 1:00–1:10 | [실습 2-1](lab0.md) | 로그인, hosted connection 수락, 스택 배포 시작 |
| 1:10–1:40 | [실습 2-2](lab1.md) | Direct Connect 연결과 온프레미스 라우터 설정 |
| 1:40–2:10 | [실습 2-3](lab2.md) | 문제 확인 → 1:1 NAT 적용 → 결과 확인 |
| 2:10–2:45 | [추가 과제 3-1–3-3](extra-a.md) | 한쪽 NAT, NAT system routes, 지표와 Flow Logs |
| 2:45–3:00 | [추가 과제 3-4](extra-d.md) | 리소스 정리 |

스택 배포는 약 6분 걸립니다. 기다리지 말고 실습 2-2를 시작하세요. 실습 2-2에는 스택이 끝나기 전에 할 수 있는 단계가 먼저 있습니다.

추가 과제 3-4(리소스 정리)는 시간이 모자라도 꼭 마지막에 합니다.

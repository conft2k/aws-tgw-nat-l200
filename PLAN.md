# 워크샵 계획: AWS Transit Gateway 1:1 NAT로 겹치는 온프레미스 대역 연결하기 (L200)

> 상태: **초안(검토 전)** · 작성 2026-11-03 · 근거: lab-aws-tgw-nat 테스트 결과(2026-11-03, T0–T9, T8R)

이 문서는 워크샵 콘텐츠를 쓰기 전에 목표, 과제, 진행 방식을 정하는 계획서입니다. 확정되면 이 계획에 따라 GitHub Pages 사이트를 만듭니다.

## 1. 개요

| 항목 | 내용 |
|---|---|
| 대상 | VPC, Transit Gateway, Direct Connect의 기본 개념을 아는 AWS 고객(네트워크·클라우드 엔지니어) |
| 레벨 | L200. 라우터 설정과 BGP 명령은 단계별로 그대로 따라 할 수 있게 제공합니다 |
| 소요 시간 | 약 4시간(쉬는 시간 제외) |
| 형식 | 참가자마다 독립된 Pod(라우터 VM, Linux VM)와 AWS 테스트 계정 1개 |
| 언어 | 한국어 |
| 게시 | GitHub Pages(공개 저장소 `ws-aws-tgw-nat-l200`) |

## 2. 시나리오

온프레미스 LAN(`172.20.N.0/24`, N은 Pod 번호)과 AWS의 VPC-A가 **같은 대역**을 씁니다. 온프레미스는 Direct Connect(Transit VIF 2개 → Direct Connect gateway → Transit Gateway)로 AWS에 연결됩니다. 주소를 바꾸지 않고 둘을 통신시키기 위해 Transit Gateway 1:1 NAT로 **양쪽을 모두 번역**합니다. NAT를 걸지 않는 대조군 VPC-B(`10.1.1.0/24`)도 함께 둡니다.

![워크샵 구성: 온프레미스 Pod의 라우터가 Transit VIF 2개로 Direct Connect gateway와 Transit Gateway에 연결된다. DXGW 연결은 172.20.x.0/24를 100.64.1.0/24로, VPC-A 연결은 172.20.x.0/24를 100.64.2.0/24로 바꾸고, VPC-B는 NAT 없이 연결된다](images/lab-architecture.svg)

구성도의 `x`는 참가자 Pod 번호(N)입니다. 워크샵 사이트에는 참가자 시점으로 다시 그린 구성도를 넣습니다.

| 네트워크 | 실제 대역 | 상대에게 보이는 대역 |
|---|---|---|
| 온프레미스 Pod LAN | 172.20.N.0/24 | 100.64.1.0/24(DXGW 연결의 NAT 규칙) |
| VPC-A | 172.20.N.0/24 | 100.64.2.0/24(VPC-A 연결의 NAT 규칙) |
| VPC-B(대조군) | 10.1.1.0/24 | 그대로 |

## 3. 학습 목표

워크샵을 마치면 참가자는 다음을 할 수 있습니다.

1. Direct Connect hosted connection을 수락하고, Transit VIF와 Direct Connect gateway를 만들어 Transit Gateway에 연결할 수 있습니다.
2. 온프레미스 라우터에서 BGP·BFD를 설정하고, AWS 콘솔과 라우터 양쪽에서 세션과 경로를 확인할 수 있습니다.
3. 겹치는 CIDR이 Transit Gateway 라우팅에서 어떤 문제를 일으키는지 직접 재현하고 라우팅 테이블에서 원인을 찾을 수 있습니다.
4. 콘솔에서 1:1 NAT 규칙을 두 연결(DXGW, VPC)에 설정하고, 상태 변화와 `system` 경로를 확인할 수 있습니다.
5. 양쪽 끝에서 상대가 어떤 주소로 보이는지 확인하고, 1:1 매핑(호스트 비트·포트 유지)을 설명할 수 있습니다.
6. NAT를 걸지 않은 VPC와의 상호작용, 남아 있는 원래 경로가 만드는 함정을 설명할 수 있습니다.
7. `NatSystemRouteSupport`의 두 모드가 온프레미스 BGP 광고와 어떻게 맞물리는지 설명하고, 운영 시 주의점을 알 수 있습니다.
8. CloudWatch 지표와 Flow Logs로 NAT 동작을 관측하고, 각 로그가 어떤 주소를 기록하는지 구분할 수 있습니다.

## 4. 진행 원칙

- **CloudFormation은 바탕만 깝니다.** VPC 2개, 서브넷, VPC 라우팅 테이블, 보안 그룹, EC2 2대(응답 서버 포함), EC2 Instance Connect Endpoint, Transit Gateway와 VPC 연결 2개, Flow Logs는 스택 하나로 배포합니다.
- **핵심 동작은 모두 AWS 콘솔에서 직접 합니다.** 다음은 콘솔에서 만들고 확인합니다.
  - hosted connection 수락, Direct Connect gateway, Transit VIF 2개, DXGW와 TGW 연결, 허용된 접두사
  - 1:1 NAT 설정(켜기, 규칙, `NatSystemRouteSupport`)
  - TGW 라우팅 테이블, CloudWatch 지표, CloudWatch Logs Insights
  - EC2 접속(콘솔의 EC2 Instance Connect, EICE 경유)
- 온프레미스 라우터와 Linux VM은 DX Lab 포털(Guacamole)의 웹 터미널로 접속합니다. 라우터 설정은 참가자의 값(Pod 번호, VLAN, BGP 주소와 키)을 채워 넣는 템플릿으로 제공합니다.
- 과제마다 **확인 포인트**(무엇이 보이면 성공인지)를 두고, 기대와 다르면 볼 곳(문제 해결 팁)을 함께 둡니다.
- 테스트에서 확인한 사실과 공식 문서 내용만 씁니다. 문서와 다르게 동작한 내용(아래 과제 7)은 출처와 함께 "이 랩에서 관찰된 동작"으로 표시합니다.

## 5. 과제

| # | 과제 | 참가자가 하는 일 | 확인 포인트 | 시간 | 근거 테스트 |
|---|---|---|---|---|---|
| 0 | 시작하기 | 워크숍 페이지에서 내 Pod·계정·hosted connection 확인, 콘솔 로그인, Guacamole로 라우터·VM 접속, CloudFormation 스택 배포(Pod 번호 입력) | 스택 `CREATE_COMPLETE`, 라우터·VM 프롬프트 | 20분 | — |
| 1 | Direct Connect 연결 | hosted connection 2개 수락 → `available` 확인, Direct Connect gateway 생성(ASN 65300), Transit VIF 2개 생성(VLAN은 hosted connection 값, BGP 주소·키 확인), 라우터에 서브인터페이스·BFD·BGP 설정 | VIF `available`·BGP `up`(콘솔), `show ip bgp summary` Established | 50분 | T0 |
| 2 | Transit Gateway에 연결 | DXGW와 TGW 연결, 허용된 접두사(VPC-A NAT 대역, VPC-B) 설정, TGW 라우팅 테이블 확인, 라우터 Loopback에서 VPC-B로 ping | 라우터가 `10.1.1.0/24`·`100.64.2.0/24`를 받음, VPC-B 응답 서버가 출발지를 그대로 봄 | 20분 | T0 |
| 3 | 겹치는 대역 문제 재현 | NAT 없이 VM에서 VPC-A·VPC-B로 통신, TGW 라우팅 테이블에서 `172.20.N.0/24`가 VPC-A만 가리키는 것 확인, VPC-A EC2에서 tcpdump | VM → VPC-B 실패, 응답이 VPC-A로 감 | 20분 | T1 |
| 4 | 1:1 NAT 적용 | 콘솔 **Manage 1:1 NAT**로 DXGW 연결(`172.20.N.0/24` → `100.64.1.0/24`)과 VPC-A 연결(`172.20.N.0/24` → `100.64.2.0/24`)에 규칙 설정, 상태 변화 관찰, 라우팅 테이블의 `system` 경로 확인 | `Enabled`·`Activated`, `system` 경로 2개 | 25분 | T2 |
| 5 | 양방향 통신과 1:1 매핑 | VM ↔ VPC-A ICMP·TCP·UDP, 응답 서버가 보여 주는 상대 주소 확인, 호스트 비트(.1, .20)와 고정 출발지 포트 확인 | VPC-A는 `100.64.1.10`, 온프레미스는 `100.64.2.10`으로 봄. 마지막 옥텟·포트 유지 | 30분 | T3, T4, T5 |
| 6 | NAT 없는 VPC와 원래 경로 | VM ↔ VPC-B, VPC-B → 두 NAT 대역, VPC-B → 원래 주소(`172.20.N.10`), Loopback 출발지 | 목적지와 상관없이 SNAT, 원래 주소로 보내면 VPC-A가 아니라 온프레미스로 감 | 20분 | T6, T7 |
| 7 | 경로 설치 옵션(`NatSystemRouteSupport`) | `enable`에서 라우터 광고를 바꿔 `system` 경로의 active·blackhole 확인(/24 철회, /16 요약). `disable`로 바꾸고 NAT 대역을 라우터에서 광고 | blackhole과 복구, `disable`에서 `propagated` NAT 경로 | 30분 | T8, T8R |
| 8 | 관측 | CloudWatch에서 연결별 `PacketsInNAT`·`PacketsOutNAT`·폐기 지표, Logs Insights로 TGW Flow Logs(양 끝의 실제 주소)와 VPC Flow Logs(`pkt-srcaddr`) 비교 | 번역이 일어난 연결마다 NAT 지표 증가, 두 로그의 주소 차이 | 20분 | T9, T3 |
| 9 | 정리 | NAT 끄기, DXGW 연결·VIF·DXGW 삭제, 스택 삭제, 라우터 설정 되돌리기 | 남은 리소스 없음 | 15분 | — |

합계 약 4시간 10분입니다. 과제 7·8은 시간이 부족하면 강사 시연으로 바꿀 수 있습니다.

### 과제 7의 주의 사항(테스트에서 관찰된 동작)

[Routing behavior for 1:1 NAT](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat-routing.html)는 `NatSystemRouteSupport=disable`이면 온프레미스가 원래 CIDR을 광고할 필요가 없다고 설명합니다. 그런데 이 랩의 Direct Connect gateway 연결에서는 원래 대역 광고를 멈추자 AWS → 온프레미스 통신이 끊겼습니다(4번 반복해 4번 모두 재현). 워크샵에서는 이를 다음 중 하나로 다룹니다(9절 결정 2).

- (a) 참가자가 직접 원래 대역 광고를 멈춰 손실을 확인하고, 다시 광고해 복구하는 선택 과제
- (b) 주의 상자로만 설명하고 참가자는 원래 대역 광고를 유지

## 6. CloudFormation 스택(참가자 계정)

| 리소스 | 내용 |
|---|---|
| 파라미터 | Pod 번호 N(→ VPC-A `172.20.N.0/24`), NAT 대역 2개(기본 `100.64.1.0/24`, `100.64.2.0/24`) |
| Transit Gateway | ASN 65400, 기본 라우팅 테이블 연결·전파 켬 |
| VPC-A | `172.20.N.0/24`. 앱 서브넷 `/26`, TGW 서브넷 `/28` 2개(2a, 2c). EC2 `172.20.N.10`(보조 IP `.20`). 라우팅 테이블에 `100.64.1.0/24`, `10.1.1.0/24` → TGW |
| VPC-B | `10.1.1.0/24`. 같은 구조, EC2 `10.1.1.10`. 라우팅 테이블에 `100.64.1.0/24`, `100.64.2.0/24`, `172.20.N.0/24`, `10.200.0.1/32` → TGW |
| EC2 | t4g.micro AL2023 2대, 응답 서버(TCP 8080은 본 클라이언트 주소를 돌려줌, UDP 9000은 에코), tcpdump·ncat |
| 접속 | VPC마다 EICE 1개, SSH는 EICE 보안 그룹에서만. 공인 IP 없음 |
| dnf | S3 gateway endpoint(AL2023 저장소만 허용) |
| 로그 | TGW Flow Logs, VPC Flow Logs(`pkt-srcaddr`·`pkt-dstaddr` 포함) → CloudWatch Logs, 전송용 IAM 역할 |

- 테스트 랩의 `infra/base.yaml`을 바탕으로 만듭니다. 계정 ID, 내부 이름은 넣지 않습니다.
- VPC 라우팅 테이블과 보안 그룹은 NAT 대역을 미리 포함합니다. 과제 4에서 왜 필요한지 설명합니다(상대가 NAT 대역으로 보이므로).
- 템플릿 전달 방식은 9절 결정 3에서 정합니다.

## 7. 사이트 구성

- MkDocs Material, GitHub Actions로 GitHub Pages(`https://conft2k.github.io/ws-aws-tgw-nat-l200/`)에 게시합니다.
- 페이지: 소개(시나리오·구성도·목표) → 사전 준비 → 과제 0–9 → 부록(라우터 설정 템플릿, 문제 해결, 1:1 NAT 개념과 제약 요약, 참고 문서).
- 구성도는 skill-aws-arch-diagram(공식 AWS 아이콘)으로 그립니다. 흐름을 ASCII 그림으로 그리지 않습니다.
- 콘솔 화면 안내는 메뉴 이름을 텍스트로 적습니다. 스크린샷은 9절 결정 4에서 정합니다.
- 라우터 설정·명령은 참가자 값을 `<POD>`, `<VLAN1>` 같은 자리 표시자로 두고, 각 값을 어디서 찾는지 표로 안내합니다.

## 8. 사전 준비와 위험

| 항목 | 내용 |
|---|---|
| 참가자 배정 | 관리자가 DX Lab 포털에서 Pod와 AWS 계정을 할당하면 hosted connection 2개(VLAN 100+N, 200+N)가 그 계정에 주문 상태로 만들어집니다. 참가자는 워크숍 페이지에서 자기 값을 찾습니다 |
| 계정 권한 | 참가자 계정에서 Direct Connect, VPC, EC2, CloudFormation, IAM 역할 생성(Flow Logs), CloudWatch를 쓸 수 있어야 합니다 |
| 리전 | ap-northeast-2(서울). 1:1 NAT를 이 리전에서 쓸 수 있는지는 행사 전에 다시 확인합니다 |
| 한도 | EICE는 계정·리전당 5개(조정 불가)이며 이 스택이 2개를 씁니다. TGW·VPC 기본 한도 안 |
| 비용 | TGW 연결 3개 시간당 요금과 데이터 처리, EC2 2대, Flow Logs. NAT 기능 요금은 행사 전에 확인해 사전 준비 페이지에 적습니다 |
| 라우터 | Pod의 라우터는 LAN 인터페이스만 설정된 상태에서 시작합니다(스냅샷 복원). 참가자가 VIF 서브인터페이스, BGP, Loopback을 추가합니다 |
| 시계 | 라우터와 VM의 시계는 NTP로 맞춰져 있지 않을 수 있습니다. 시각 비교는 AWS 쪽 기록을 기준으로 안내합니다 |
| 정리 | 참가자는 과제 9에서 자기 리소스를 지웁니다. hosted connection 회수와 Pod 복원은 관리자가 합니다 |

## 9. 결정이 필요한 항목

1. **저장소 이름과 레벨**: `ws-aws-tgw-nat-l200`(대상이 네트워킹 기본 이해를 가진 고객이므로 L200). 라우터·BGP 설정 비중을 고려해 L300으로 할지
2. **과제 7의 원래 대역 철회**: 5절 (a) 선택 과제로 직접 확인 / (b) 주의 상자로만 설명
3. **템플릿 전달**: 사이트에서 YAML을 내려받아 콘솔에서 업로드(추가 인프라 없음) / S3에 올려 바로 배포 링크(Quick-create) 제공
4. **콘솔 스크린샷**: 넣지 않음(텍스트 안내만, 콘솔 변경에 강함) / 주요 화면만 넣음
5. **콘솔 언어**: 영어 콘솔 기준으로 메뉴 이름 표기 / 한국어 콘솔 기준
6. **소요 시간**: 4시간 그대로 / 3시간으로 줄이고 과제 7·8을 시연으로

## 참고

- 테스트 계획과 결과: lab-aws-tgw-nat(비공개) `test-plan.md`, `results/README.md`
- [1:1 NAT in AWS Transit Gateway](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat.html)
- [How 1:1 NAT works](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat-how-it-works.html)
- [Routing behavior for 1:1 NAT](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat-routing.html)
- [Configure 1:1 NAT](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat-configure.html)
- [Hosted Direct Connect connections](https://docs.aws.amazon.com/directconnect/latest/UserGuide/hosted_connection.html)

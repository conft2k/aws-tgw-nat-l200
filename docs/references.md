# 4-4. 참고 문서

## 4-4-1. AWS Transit Gateway 1:1 NAT

- [1:1 NAT in AWS Transit Gateway](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat.html) — 1:1 NAT 개요
- [How 1:1 NAT works](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat-how-it-works.html) — 출발지·목적지 주소가 바뀌는 방식
- [Routing behavior for 1:1 NAT](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat-routing.html) — **NAT system routes**와 NAT 대역으로 가는 경로가 만들어지는 방식
- [Configure 1:1 NAT](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-nat-configure.html) — Transit Gateway 연결에서 1:1 NAT를 켜고 규칙을 넣는 방법
- [CloudWatch metrics for transit gateways](https://docs.aws.amazon.com/vpc/latest/tgw/transit-gateway-cloudwatch-metrics.html) — Transit Gateway와 연결의 지표. 워크숍에서 본 지표는 [3-3](extra-c.md)에 있습니다
- [Transit Gateway Flow Logs](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-flow-logs.html) — Transit Gateway를 지난 트래픽의 기록
- [Transit Gateway quotas](https://docs.aws.amazon.com/vpc/latest/tgw/transit-gateway-quotas.html) — Transit Gateway의 할당량

!!! warning "NAT system routes를 끈 경우의 원래 대역 광고"
    Routing behavior for 1:1 NAT와 How 1:1 NAT works는 NAT system routes를 끄면 원래 대역 대신 NAT 대역을 광고하라고 설명합니다. 하지만 사전 테스트(2026-11-03)에서는 원래 대역 광고를 멈추자 AWS → 온프레미스 방향 통신이 끊겼습니다. 실습에서는 원래 대역 광고를 계속 유지하세요. 자세한 내용은 [추가 과제 3-2-2](extra-b.md#b2)에 있습니다.

## 4-4-2. AWS Direct Connect

용어의 뜻은 [1-3. 용어 풀이](glossary.md)에 있습니다.

- [Hosted connections](https://docs.aws.amazon.com/directconnect/latest/UserGuide/hosted_connection.html) — hosted connection(호스팅 연결). Direct Connect 파트너가 만들어 여러분 계정에 넘겨 준 회선
- [Transit virtual interfaces](https://docs.aws.amazon.com/directconnect/latest/UserGuide/WorkingWithVirtualInterfaces.html) — 전송 가상 인터페이스(transit VIF). hosted connection 위에서 온프레미스 라우터와 AWS가 BGP로 경로를 주고받는 인터페이스
- [Direct Connect gateways and transit gateway associations](https://docs.aws.amazon.com/directconnect/latest/UserGuide/direct-connect-transit-gateways.html) — Direct Connect 게이트웨이(DXGW)와 Transit Gateway를 잇는 게이트웨이 연결
- [Allowed prefixes](https://docs.aws.amazon.com/directconnect/latest/UserGuide/allowed-to-prefixes.html) — 허용된 접두사. 게이트웨이 연결에 적은 대역으로, 적은 그대로 온프레미스 라우터에 광고됩니다

## 4-4-3. 그 밖에

- [EC2 Instance Connect Endpoint](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-using-eice.html) — 인터넷 주소가 없는 VPC-A EC2에 브라우저로 접속할 때 쓰는 엔드포인트
- [VPC Flow Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html) — VPC 안에서 보이는 주소로 트래픽을 남기는 기록

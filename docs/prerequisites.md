# 1-2. 사전 준비

## 1-2-1. 받는 것

워크숍 운영자가 참가자마다 다음을 준비해 둡니다.

| 항목 | 내용 |
|---|---|
| AWS 계정 | 실습용 계정 1개와 콘솔 로그인 정보 |
| 온프레미스 Pod | 온프레미스 라우터(`rtN`, Cisco)와 온프레미스 VM(`vmN`, Linux). 온프레미스 대역은 `172.20.N.0/24` |
| hosted connection 2개 | 여러분 계정에 **수락 대기**(Ordering) 상태로 들어와 있습니다 |
| 실습 장비 페이지 | 내 Pod 정보를 보고, 온프레미스 라우터와 온프레미스 VM의 터미널을 여는 페이지(링크는 운영자가 드립니다) |

실습 장비 페이지는 아래처럼 보입니다. hosted connection 2개(DX1, DX2)와 각각의 VLAN, 내 온프레미스 라우터와 온프레미스 VM이 보입니다.

![실습 장비 페이지: DX1·DX2 hosted connection(VLAN 189, 289)과 pod89의 온프레미스 라우터 rt89, 온프레미스 VM vm89](images/portal/lab0-portal-pod.png){ .shot }

## 1-2-2. 내 값 적어 두기 { #notes }

실습에서 계속 쓰는 값입니다. 미리 적어 두면 편합니다.

| 값 | 예 | 찾는 곳 |
|---|---|---|
| Pod 번호 N | `89` | 실습 장비 페이지(`podN`) |
| DX1 VLAN | `189` | 실습 장비 페이지 |
| DX2 VLAN | `289` | 실습 장비 페이지 |
| 전송 가상 인터페이스 1·2의 IP와 BGP 키 | `169.254.…` | 실습 2-2에서 만든 뒤 콘솔에서 확인 |

## 1-2-3. 브라우저 준비

- 따로 설치할 프로그램은 없습니다. 콘솔, 웹 터미널, VPC-A EC2와 VPC-B EC2 접속 모두 브라우저에서 합니다.
- 콘솔 언어를 **English**로 바꾸면 이 안내와 화면이 같습니다. 콘솔 오른쪽 위 톱니바퀴 아이콘(**Unified Settings**) → **Language**에서 바꿉니다.
- 콘솔 오른쪽 위 리전을 **Asia Pacific (Seoul)** 로 맞춥니다. Direct Connect 콘솔에는 **Global**로 보이지만 괜찮습니다.

## 1-2-4. 꼭 지켜 주세요

!!! danger "hosted connection은 지우지 마세요"
    콘솔에서 지울 수는 있지만, 지우면 여러분이 다시 만들 수 없습니다. 실습이 끝나도 그대로 두세요. 운영자가 회수합니다.

!!! warning "온프레미스 라우터(`rtN`)의 GigabitEthernet4는 건드리지 마세요"
    `GigabitEthernet4`는 온프레미스 대역(`172.20.N.0/24`)과 웹 터미널이 연결되는 인터페이스입니다. 실습에서는 `GigabitEthernet1`, `GigabitEthernet2`에 설정을 추가하기만 합니다.

## 1-2-5. 비용

실습 계정에 다음 요금이 발생합니다. 계정과 비용은 운영자가 관리합니다.

- hosted connection 2개의 포트 요금(수락한 때부터 운영자가 회수할 때까지)과 Direct Connect 데이터 전송
- Transit Gateway 연결 3개의 시간당 요금과 데이터 처리
- EC2 2대(VPC-A EC2, VPC-B EC2), CloudWatch Logs 저장과 조회
- 1:1 NAT 기능 자체의 요금은 확인 중입니다

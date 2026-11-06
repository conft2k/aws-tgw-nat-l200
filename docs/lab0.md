# 2-1. 시작하기 (10분)

오래 걸리는 두 가지를 먼저 시작해 둡니다. hosted connection 수락과 스택 배포입니다. 준비가 끝나기를 기다리지 않고 실습 2-2로 넘어갑니다.

## 2-1-1. 웹 터미널 열어 보기 { #lab0-1 }

1. 실습 장비 페이지를 엽니다. 내 Pod 번호, DX1·DX2 VLAN을 [적어 둡니다](prerequisites.md#notes).
2. 온프레미스 라우터(`rtN`)를 누릅니다. 웹 터미널에 `rtN#`이 보이면 됩니다.
3. 왼쪽 위 홈 아이콘으로 돌아와 온프레미스 VM(`vmN`)도 엽니다. `labuser@vmN:~$`가 보이면 됩니다.

!!! tip "탭을 여러 개 쓰세요"
    온프레미스 라우터, 온프레미스 VM, AWS 콘솔을 브라우저 탭으로 따로 열어 두면 오가기 편합니다.

## 2-1-2. hosted connection 수락 { #lab0-2 }

1. AWS 콘솔에 로그인합니다. 오른쪽 위 리전을 **Asia Pacific (Seoul)** 로 맞춥니다.
2. **Direct Connect** 콘솔 → 왼쪽 메뉴 **Connections**를 엽니다.
3. 이름이 `awsdx1_…`, `awsdx2_…`인 hosted connection 2개가 보입니다. 상태는 **Ordering**입니다.

    ![Connections 목록: awsdx1_189와 awsdx2_289 두 hosted connection이 Ordering 상태이고, Accept hosted connection 버튼은 아직 회색이다](images/console/lab0-hc-01-ordering.png){ .shot }

4. `awsdx1_…` 줄 왼쪽의 확인란을 선택하고 **Accept hosted connection**을 누릅니다.
5. 확인 창에서 **Confirm**을 누릅니다.

    ![Accept hosted connection 확인 창: Cancel과 Confirm 버튼](images/console/lab0-hc-02-accept-dialog.png){ .shot }

6. `awsdx2_…`도 같은 방법으로 수락합니다.

**성공 확인**: 두 연결의 상태가 **Pending**으로 바뀝니다. 몇 분 뒤 **Available**이 됩니다(사전 테스트 시 3~6분). 기다리지 말고 다음으로 넘어갑니다.

![Connections 목록: 두 hosted connection이 Pending 상태](images/console/lab0-hc-03-pending.png){ .shot }

## 2-1-3. 스택 배포 { #lab0-3 }

스택은 실습에 필요한 바탕을 만듭니다. Transit Gateway, VPC 2개, EC2 2대(VPC-A EC2, VPC-B EC2), EC2 접속용 엔드포인트, 로그 설정입니다. 핵심인 Direct Connect 연결과 1:1 NAT는 이어지는 실습에서 직접 만듭니다.

1. 템플릿 파일을 내려받습니다: [tgw-nat-workshop.yaml](assets/tgw-nat-workshop.yaml){ download }
2. **CloudFormation** 콘솔 → **Create stack** → **With new resources (standard)** 를 누릅니다.
3. **Upload a template file** → **Choose file**로 내려받은 파일을 고르고 **Next**를 누릅니다.

    ![Create stack 화면: Upload a template file이 선택되어 있고 tgw-nat-workshop.yaml이 올라가 있다](images/console/lab0-cfn-01-upload.png){ .shot }

4. **Stack name**에 `tgw-nat-workshop`을 넣습니다. **Parameters**의 **PodNumber**에 내 Pod 번호를 넣고 **Next**를 누릅니다. 다른 값은 그대로 둡니다.

    ![Parameters 영역: PodNumber에 89가 들어가 있다](images/console/lab0-cfn-02-parameters.png){ .shot }

5. 다음 화면 맨 아래 **Capabilities**에서 **I acknowledge that AWS CloudFormation might create IAM resources.** 를 선택하고 **Next**를 누릅니다. 로그를 저장하는 데 필요한 권한(IAM 역할)을 만들기 때문입니다.

    ![Capabilities 상자: IAM 확인란이 선택되어 있다](images/console/lab0-cfn-03-ack.png){ .shot }

6. 마지막 화면에서 **Submit**을 누릅니다.

**성공 확인**: 스택 상태가 **CREATE_IN_PROGRESS**입니다. 약 6분 뒤 **CREATE_COMPLETE**가 됩니다.

![스택 이벤트: tgw-nat-workshop이 CREATE_IN_PROGRESS](images/console/lab0-cfn-05-in-progress.png){ .shot }

여기까지 하고 [실습 2-2](lab1.md)로 넘어갑니다.

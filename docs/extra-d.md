# 3-4. 리소스 정리 (약 13분)

실습이 끝나면 직접 만든 리소스를 지웁니다. 아래 **순서대로** 지워야 합니다. 앞의 리소스가 남아 있으면 다음 삭제가 실패합니다. 시간은 사전 테스트 때 잰 값입니다.

!!! danger "hosted connection은 지우지 마세요"
    **Connections**의 hosted connection 2개는 그대로 둡니다. 운영자가 회수합니다.

## 3-4-1. 1:1 NAT 끄기 (약 1분) { #d1 }

두 Transit Gateway 연결(DXGW, VPC-A)의 **Manage 1:1 NAT**에서 **Enable NAT Gateway support**를 해제하고 **Save changes**를 누릅니다. 규칙은 남아 있어도 됩니다.

![Manage NAT rules 화면: Enable NAT Gateway support 확인란이 해제되어 있다](images/console/extraD-01-nat-off-dxgw.png){ .shot }

**성공 확인**: **1:1 NAT** 탭에 **Disabled**, 규칙은 **Deactivated**가 보입니다.

## 3-4-2. 게이트웨이 연결 끊기 (약 2분) { #d2 }

1. **Direct Connect gateways** → 게이트웨이 ID → **Gateway associations** 탭으로 갑니다.
2. 게이트웨이 연결을 고르고 **Disassociate**를 누릅니다. 확인 창에서 다시 **Disassociate**를 누릅니다.

![Disassociate 확인 창](images/console/extraD-02-disassociate.png){ .shot }

**성공 확인**: 목록에서 게이트웨이 연결이 사라집니다. 이 연결이 남아 있으면 스택이 Transit Gateway를 지우지 못합니다.

## 3-4-3. 전송 가상 인터페이스 지우기 (약 4분) { #d3 }

**Virtual interfaces**에서 `tgw-nat-vif1`을 고르고 **Delete**를 누릅니다. 확인 창에서 다시 **Delete**를 누릅니다. `tgw-nat-vif2`도 같은 방법으로 지웁니다.

![전송 가상 인터페이스 Delete 확인 창](images/console/extraD-03-delete-vif.png){ .shot }

**성공 확인**: 두 인터페이스의 상태가 **Deleted**가 됩니다.

## 3-4-4. Direct Connect gateway 지우기 { #d4 }

두 인터페이스가 지워진 뒤 **Direct Connect gateways**에서 게이트웨이를 고르고 **Delete**를 누릅니다. 바로 지워집니다.

## 3-4-5. 스택 지우기 (약 3분) { #d5 }

1. **CloudFormation** → `tgw-nat-workshop` → **Delete stack**을 누릅니다.
2. 확인 창의 입력란에 스택 이름 `tgw-nat-workshop`을 그대로 입력하고 **Delete stack**을 누릅니다.

![Delete stack 확인 창: 스택 이름을 입력하는 칸이 있다](images/console/extraD-05-delete-stack.png){ .shot }

**성공 확인**: 스택이 목록에서 사라집니다(**DELETE_COMPLETE**). Transit Gateway, VPC, VPC-A EC2와 VPC-B EC2, 로그도 함께 지워집니다.

## 3-4-6. 마무리 { #d6 }

- 온프레미스 라우터(`rtN`)와 온프레미스 VM(`vmN`)에 추가한 설정은 그대로 두어도 됩니다. 운영자가 Pod를 처음 상태로 되돌립니다.
- **Connections**에 hosted connection 2개가 **Available**로 남아 있으면 정리가 끝난 것입니다.

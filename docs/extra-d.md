# 추가 과제 D. 리소스 정리 (약 15분 예상)

실습이 끝나면 직접 만든 리소스를 지웁니다. 아래 **순서대로** 지워야 합니다. 앞의 리소스가 남아 있으면 다음 삭제가 실패합니다. 걸리는 시간은 예상치입니다.

!!! danger "hosted connection은 지우지 마세요"
    **Connections**의 hosted connection 2개는 그대로 둡니다. 운영자가 회수합니다.

1. **1:1 NAT 끄기**: 두 Transit Gateway 연결(DXGW, VPC-A)의 **Manage 1:1 NAT**에서 **Enable NAT Gateway support**를 해제하고 저장합니다. 규칙은 남아 있어도 됩니다(상태가 **Deactivated**로 바뀝니다).
2. **게이트웨이 연결 끊기**: **Direct Connect gateways** → 게이트웨이 ID → **Gateway associations** 탭에서 연결을 고르고 **Disassociate**를 누릅니다. 상태가 **disassociated**가 될 때까지 기다립니다. 이 연결이 남아 있으면 스택이 Transit Gateway를 지우지 못합니다.
3. **전송 가상 인터페이스 지우기**: **Virtual interfaces**에서 `tgw-nat-vif1`, `tgw-nat-vif2`를 하나씩 고르고 **Delete**를 누릅니다.
4. **Direct Connect gateway 지우기**: 두 인터페이스가 지워진 뒤 게이트웨이를 고르고 **Delete**를 누릅니다.
5. **스택 지우기**: **CloudFormation** → `tgw-nat-workshop` → **Delete**를 누릅니다. 로그도 함께 지워집니다.
6. **라우터**: 추가한 설정은 그대로 두어도 됩니다. 운영자가 Pod를 처음 상태로 되돌립니다.

**성공 확인**: Direct Connect gateway와 전송 가상 인터페이스가 없고, 스택은 **DELETE_COMPLETE**입니다. hosted connection 2개는 남아 있습니다.

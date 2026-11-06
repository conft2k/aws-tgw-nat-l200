# 4-4. 문제 해결

| 이럴 때 | 볼 곳 | 해결 |
|---|---|---|
| hosted connection이 계속 **Ordering** | **Connections** | **Accept hosted connection**으로 수락했는지 확인 |
| 전송 가상 인터페이스를 만들 때 **Connection** 목록에 hosted connection이 없음 | **Connections** | hosted connection이 **Available**이 될 때까지 기다림. 이미 인터페이스가 있는 hosted connection에는 더 만들 수 없음 |
| 전송 가상 인터페이스를 잘못 만듦 | **Virtual interfaces** | 하나만 만들 수 있으므로 지우고 다시 만듦 |
| 스택이 **ROLLBACK** | 스택 **Events** | IAM 확인란을 선택했는지, 같은 이름의 스택이 남아 있지 않은지 확인 |
| BGP가 `Active`나 `Idle` | 온프레미스 라우터(`rtN`) 터미널의 `show ip bgp summary`, 인터페이스 **Peerings** 탭 | VLAN, IP, BGP 키가 콘솔 값과 같은지 확인. 첫 번째 인터페이스는 `GigabitEthernet1`, 두 번째는 `GigabitEthernet2`. 붙여 넣을 때 `%` 오류가 없었는지 확인 |
| BGP는 연결됐는데 경로를 못 받음 | **Gateway associations** 탭 | 게이트웨이 연결이 **associated**인지, 허용된 접두사를 넣었는지 확인 |
| 온프레미스 라우터의 Loopback1 → VPC-B 실패 | 온프레미스 라우터(`rtN`) 터미널의 `show ip bgp` | `10.1.1.0/24`를 받았는지, `10.200.0.1/32`를 광고하는지 확인 |
| NAT 설정이 저장되지 않음 | **Manage NAT rules** 화면의 빨간 글씨 | 빈 규칙 줄을 **Remove**. 대역 입력란은 목록에서 **Use "…"** 를 고름. enabling·disabling 중이면 끝날 때까지 기다림 |
| NAT 뒤에도 온프레미스 VM(`vmN`) → `100.64.2.10` 실패 | **1:1 NAT** 탭, 라우팅 테이블 | 두 연결 모두 **Enabled**·**Activated**인지, `100.64.2.0/24` System 경로가 있는지 확인 |
| NAT 뒤 VPC-A → `100.64.1.10` 실패 | 라우팅 테이블 | `100.64.1.0/24` System 경로가 **Active**인지. **Blackhole**이면 온프레미스 라우터가 `172.20.N.0/24`를 광고하는지 확인 |
| 온프레미스 VM에서 `curl`은 되는데 반대 방향이 안 됨 | 온프레미스 VM(`vmN`) 터미널 | 웹 서버를 띄웠는지 확인: `pkill -f 'http.server 8080'; python3 -m http.server 8080 &` |
| 웹 서버를 띄울 때 `Address already in use`, 또는 상대 쪽 `curl`이 `HTTP 000` | 온프레미스 VM(`vmN`) 터미널 | 끊긴 웹 터미널에서 띄운 서버가 남아 있음. `pkill -f 'http.server 8080'` 뒤 다시 실행 |
| VPC-A EC2나 VPC-B EC2 터미널이 끊김 | — | 최대 1시간 유지. **Connect**로 다시 접속 |
| 온프레미스 VM의 `nc -u`가 답 없이 끝남 | — | `(echo hello; sleep 1) \| nc -u -w 2 …` 형태로 보냄 |
| 지표나 로그가 비어 있음 | 시간 범위 | 몇 분 늦게 나타남. 시간 범위를 **1h**로 두고 다시 조회 |

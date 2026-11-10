# 4-3. 문제 해결

표에서 "라우팅 테이블"은 Transit Gateway 라우팅 테이블입니다. **VPC** 콘솔 → **Transit gateway route tables** → 라우팅 테이블 ID → **Routes** 탭에서 봅니다([2-3-6](lab2.md#lab2-6)). 경로 유형(**System**, **Propagated**)과 **Blackhole**의 뜻은 [용어 풀이](glossary.md#1-3-3)에 있습니다.

`<이웃 주소>`에는 두 전송 가상 인터페이스의 **Amazon router peer IP**를 `/29` 없이 하나씩 넣습니다. `show ip bgp summary | begin Neighbor`의 첫 칸에도 보입니다.

| 이럴 때 | 볼 곳 | 해결 |
|---|---|---|
| hosted connection이 계속 **Ordering** | **Connections** | **Accept hosted connection**으로 수락했는지 확인 |
| 전송 가상 인터페이스를 만들 때 **Connection** 목록에 hosted connection이 없음 | **Connections** | hosted connection이 **Available**이 될 때까지 기다림. 이미 인터페이스가 있는 hosted connection에는 더 만들 수 없음 |
| 전송 가상 인터페이스를 잘못 만듦 | **Virtual interfaces** | 하나만 만들 수 있으므로 지우고 다시 만듦 |
| **Submit**을 누르자 오류가 나고 스택이 만들어지지 않음 | 화면 위쪽 오류 메시지 | **Capabilities**의 IAM 확인란을 선택했는지, 같은 이름(`tgw-nat-workshop`)의 스택이 남아 있지 않은지 확인 |
| 스택이 **ROLLBACK_IN_PROGRESS**나 **ROLLBACK_COMPLETE** | 스택 **Events** 탭 | 시간순으로 가장 먼저 난 **CREATE_FAILED** 이벤트의 **Status reason**을 읽고 원인을 고침. 그다음 **ROLLBACK_COMPLETE** 스택을 지우고 [2-1-3](lab0.md#lab0-3)처럼 다시 만듦 |
| BGP(Border Gateway Protocol)가 `Active`나 `Idle` | 온프레미스 라우터(`rtN`) 터미널의 `show ip bgp summary`, 인터페이스 **Peerings** 탭 | VLAN(Virtual LAN), IP, BGP 키가 콘솔 값과 같은지 확인. 첫 번째 인터페이스는 `GigabitEthernet1`, 두 번째는 `GigabitEthernet2`. 붙여 넣을 때 `%` 오류가 없었는지 확인 |
| BGP는 연결됐는데 경로를 못 받음 | **Gateway associations** 탭 | 게이트웨이 연결이 **associated**인지, 허용된 접두사를 넣었는지 확인 |
| 온프레미스 라우터의 Loopback1 → VPC-B 실패 | 온프레미스 라우터(`rtN`) 터미널의 `show ip bgp \| begin Network` | `10.1.1.0/24`를 받았는지 확인. 없으면 바로 위 행처럼 **Gateway associations** 탭을 확인 |
| `10.1.1.0/24`는 받았는데 Loopback1 → VPC-B 실패 | 온프레미스 라우터(`rtN`) 터미널의 `show ip bgp neighbors <이웃 주소> advertised-routes` | 두 AWS 이웃 각각에 실행해 목록에 `10.200.0.1/32`가 있는지 확인. 없으면 [2-2-5](lab1.md#lab1-5)의 설정을 다시 붙여 넣음 |
| NAT(Network Address Translation) 설정이 저장되지 않음 | **Manage NAT rules** 화면의 빨간 글씨 | 빈 규칙 줄을 **Remove**. 대역 입력란은 목록에서 **Use "…"** 를 고름. enabling·disabling 중이면 끝날 때까지 기다림 |
| NAT 뒤에도 온프레미스 VM(Virtual Machine, `vmN`) → `100.64.2.10` 실패 | **VPC** 콘솔 → **Transit gateway attachments**에서 DXGW(Direct Connect gateway) 연결(**Resource type**이 **Direct Connect Gateway**)과 `tgwnat-attach-vpc-a`를 각각 열고 **1:1 NAT** 탭 | 두 연결 모두 **NAT Gateway support: Enabled**, 규칙 상태 **Activated**인지 확인. **Enabling**이면 잠시 뒤 새로 고침. 규칙 값은 [2-3-4](lab2.md#lab2-4), [2-3-5](lab2.md#lab2-5)와 비교 |
| 두 연결의 NAT 설정은 맞는데 온프레미스 VM → `100.64.2.10` 실패 | 라우팅 테이블의 `100.64.2.0/24`, `100.64.1.0/24` | 요청이 쓰는 `100.64.2.0/24`가 **System**·**Active**이고 VPC를 가리키는지 확인. 응답이 쓰는 `100.64.1.0/24`도 **Active**인지 확인. **Blackhole**이면 아래 **NAT system routes** 켬 행을 봄 |
| NAT 뒤 VPC-A EC2 → `100.64.1.10` 실패(**NAT system routes** 켬, 기본값) | 라우팅 테이블의 `100.64.1.0/24`, 온프레미스 라우터(`rtN`) 터미널의 `show ip bgp neighbors <이웃 주소> advertised-routes` | 정상이면 **System**·**Active**이고 Direct Connect Gateway를 가리킴. **Blackhole**이면 두 이웃의 광고 목록에 `172.20.N.0/24`나 이와 겹치는 대역이 있는지 확인. System 경로는 이 광고가 있는 동안만 **Active**([3-2-1](extra-b.md#b1)) |
| NAT 뒤 VPC-A EC2 → `100.64.1.10` 실패(**NAT system routes** 끔, [3-2-2](extra-b.md#b2)) | 라우팅 테이블의 `100.64.1.0/24`, 온프레미스 라우터(`rtN`) 터미널의 `show ip bgp neighbors <이웃 주소> advertised-routes` | 정상이면 **Propagated**·**Active**. 경로가 없으면 두 이웃의 광고 목록에 `100.64.1.0/24`가 있는지 확인 |
| **NAT system routes**를 끈 뒤 `100.64.1.0/24`는 **Propagated**·**Active**인데 VPC-A EC2 → `100.64.1.10`만 실패 | 온프레미스 라우터(`rtN`) 터미널의 `show ip bgp neighbors <이웃 주소> advertised-routes` | 두 이웃의 광고 목록에 `172.20.N.0/24`가 있는지 확인하고, 없으면 다시 광고. 이 워크숍에서는 끈 상태에서도 원래 대역 광고를 유지함. 사전 테스트에서 원래 대역 광고를 멈추자 이 방향만 끊겼기 때문. 공식 문서 설명과 다른 관찰이며, 자세한 내용은 [3-2-2](extra-b.md#b2) |
| VPC-A EC2 → `100.64.1.10`의 `curl`이 `HTTP 000` | VPC-A EC2 터미널의 `ping -c 4 100.64.1.10` | `HTTP 000`은 HTTP 응답을 받지 못했다는 뜻. 원인은 경로일 수도, 웹 서버일 수도 있음. ping도 실패하면 먼저 위의 `100.64.1.10` 경로 행을 보고, 경로가 정상이면 온프레미스 VM(`vmN`)이 켜져 있는지 확인. ping이 되면 경로는 정상이므로 다음 행을 봄 |
| VPC-A EC2 → `100.64.1.10`의 ping은 되는데 `curl`이 `HTTP 000` | 온프레미스 VM(`vmN`) 터미널 | 웹 서버를 띄웠는지 확인. 웹 터미널이 끊겼다가 다시 열렸다면 전에 띄운 서버가 포트를 잡은 채 응답하지 못함. `pkill -f 'http.server 8080'; python3 -m http.server 8080 &`로 다시 띄움. 그래도 안 되면 VPC-A EC2에서 `curl -v http://100.64.1.10:8080/`로 오류를 봄. `Connection refused`면 서버가 포트를 열었는지와 온프레미스 VM 방화벽의 거부 설정을 확인. `Connected to`가 나오기 전에 시간이 초과되면 TCP(Transmission Control Protocol) 8080이 중간에서 막히지 않았는지 확인하고, 연결된 뒤 응답이 없으면 서버 상태를 확인 |
| 웹 서버를 띄울 때 `Address already in use` | 온프레미스 VM(`vmN`) 터미널 | 끊긴 웹 터미널에서 띄운 서버가 남아 있음. `pkill -f 'http.server 8080'` 뒤 다시 실행 |
| VPC-A EC2나 VPC-B EC2 터미널이 끊김 | — | 최대 1시간 유지. **Connect**로 다시 접속 |
| 온프레미스 VM의 `nc -u`가 답 없이 끝남 | 온프레미스 VM(`vmN`) 터미널 | [2-3-7](lab2.md#lab2-7)의 명령을 그대로 보냄: `(echo hello; sleep 1) \| nc -u -w 2 100.64.2.10 9000; echo` |
| NAT 지표가 비어 있음 | **CloudWatch** → **Metrics** → **Classic metrics**([3-3-1](extra-c.md#c1)) | 지표는 몇 분 늦게 나타남. 온프레미스 VM에서 `ping -c 200 100.64.2.10`으로 트래픽을 만들고 3~5분 기다린 뒤, 오른쪽 위 시간 범위를 ping을 보낸 몇 분에 맞춰 다시 조회 |
| Flow Logs 조회 결과가 비어 있음 | **CloudWatch** → **Logs** → **Log Analytics**([3-3-2](extra-c.md#c2)) | 로그도 몇 분 늦게 나타남. 트래픽을 만들고 3~5분 기다림. **Log group**이 쿼리에 맞는지(`/tgwnat/tgw-flow-logs`, `/tgwnat/vpc-flow-logs`), 시간 범위가 **1h**인지, 쿼리의 `N`을 내 Pod 번호로 바꿨는지 확인 |

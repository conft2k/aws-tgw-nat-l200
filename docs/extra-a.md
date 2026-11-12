# 3-1. Transit Gateway NAT의 동작 특성

[실습 2-3](lab2.md)을 마친 뒤에 합니다. Transit Gateway의 1:1 NAT(Network Address Translation)에서 눈여겨볼 동작 두 가지를 NAT 규칙이 없는 VPC-B로 확인합니다.

- **규칙은 연결에서 동작합니다.** 규칙을 둔 연결로 들어오는 패킷은 출발지가 규칙의 원래 대역에 있으면 목적지와 상관없이 출발지가 바뀝니다. 그래서 규칙이 없는 VPC-B로 가는 패킷도 바뀝니다(3-1-1).
- **원래 경로는 남습니다.** NAT를 켜도 온프레미스가 광고한 `172.20.N.0/24` 경로가 Transit Gateway에 남습니다. 그래서 VPC-A의 원래 주소로 보내면 VPC-A가 아니라 온프레미스로 갑니다(3-1-3).

<figure markdown="span">
  ![세 흐름을 실선(요청)과 점선(응답)으로 그린 그림. A1(초록): 온프레미스 VM이 VPC-B로 보내면 Transit Gateway의 DXGW 연결이 출발지를 100.64.1.10으로 바꾼다. A2(파랑): VPC-B가 NAT 주소로 보내면 받는 쪽 Transit Gateway 연결이 목적지를 원래 주소로 되돌리고, 응답의 출발지를 NAT 주소로 바꿔 돌려보낸다. A3(주황 요청, 빨강 응답): VPC-B가 원래 주소 172.20.N.10으로 보내면 남아 있는 172.20.N.0/24 경로를 따라 온프레미스 VM에 도착하지만, 응답이 100.64.1.10에서 온 것으로 보여 ping은 세지 않고(추론) TCP SYN-ACK는 보안 그룹이 거부한다](images/diagrams/extra-a-vpcb-and-original-route.png)
  <figcaption>그림 7. VPC-B에서 본 세 가지 흐름(A1·A2·A3)</figcaption>
</figure>

| 흐름 | 경로 | 내용 |
|---|---|---|
| A1 | 온프레미스 VM(Virtual Machine) → VPC-B `10.1.1.10` | VPC-B에는 NAT 규칙이 없어도 DXGW(Direct Connect gateway) 연결의 규칙이 출발지 `172.20.N.10`을 `100.64.1.10`으로 바꿉니다(SNAT, Source Network Address Translation). VPC-B EC2는 `100.64.1.10`을 봅니다. |
| A2 | VPC-B → `100.64.2.10` · `100.64.1.10` | 요청은 출발지 `10.1.1.10`이 그대로이고, 받는 쪽 연결이 목적지만 원래 주소로 되돌립니다(DNAT, Destination Network Address Translation). 응답은 출발지가 NAT 주소로 바뀌어(SNAT) 돌아오므로 성공합니다. |
| A3 | VPC-B → `172.20.N.10` (원래 주소) | 남아 있는 원래 경로를 따라 VPC-A가 아니라 온프레미스 VM에 도착합니다. 응답이 다른 주소(`100.64.1.10`)에서 와서 ping과 curl이 실패합니다. |

## 3-1-1. 온프레미스 → VPC-B { #a1 }

온프레미스 VM(`vmN`) 터미널에서 실행합니다.

```bash
curl http://10.1.1.10:8080/
```

**결과**: `vpc-b-ec2 saw 100.64.1.10:<포트>`입니다.

**왜 그럴까요?** VPC-B에는 규칙이 없지만, 온프레미스 VM의 패킷은 DXGW 연결을 지나며 출발지가 `100.64.1.10`으로 바뀝니다(SNAT). DXGW 연결의 규칙은 목적지가 어디든 원래 대역(`172.20.N.0/24`)에서 온 패킷을 바꿉니다. 그래서 [2-3-2. 문제 확인](lab2.md#lab2-2)에서 VPC-A로 잘못 가던 응답이 이제 온프레미스 VM으로 돌아옵니다.

## 3-1-2. VPC-B → NAT 주소 { #a2 }

1. 온프레미스 VM(`vmN`) 터미널에서 웹 서버를 백그라운드로 실행합니다. [2-3-7](lab2.md#lab2-7)과 같은 명령입니다: `pkill -f 'http.server 8080'; python3 -m http.server 8080 &`
2. VPC-B EC2(`tgwnat-vpc-b-ec2`)에 [2-3-1](lab2.md#lab2-1)처럼 접속해 실행합니다.

    ```bash
    curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://100.64.1.10:8080/
    curl http://100.64.2.10:8080/
    ```

**결과**

- 둘 다 성공합니다.
- VPC-A의 응답은 `vpc-a-ec2 saw 10.1.1.10:<포트>`입니다. 온프레미스 VM 웹 서버 기록의 맨 앞 주소도 `10.1.1.10`입니다.

**왜 성공할까요?** VPC-B 연결에는 규칙이 없어 출발지 `10.1.1.10`은 그대로입니다. 받는 쪽 연결(VPC-A 연결, DXGW 연결)이 목적지 NAT 주소를 원래 주소 `172.20.N.10`으로 되돌리고(DNAT), 응답의 출발지는 다시 NAT 주소로 바꿉니다(SNAT). 보낸 주소에서 응답이 오므로 정상적으로 주고받습니다. 3-1-3에서는 응답이 다른 주소에서 옵니다.

## 3-1-3. VPC-B → 원래 주소 `172.20.N.10` { #a3 }

3-1-2에서 백그라운드로 실행한 온프레미스 VM의 웹 서버는 그대로 둡니다.

1. 온프레미스 VM(`vmN`) 터미널에서 패킷을 지켜봅니다.

    ```bash
    sudo tcpdump -ni ens192 'icmp or tcp port 8080'
    ```

2. VPC-B EC2 터미널에서 원래 주소로 보냅니다.

    ```bash
    ping -c 3 -W 1 172.20.N.10
    curl -s -m 5 http://172.20.N.10:8080/; echo "curl-rc=$?"
    ```

![VPC-B EC2 터미널: 172.20.89.10으로 ping 3개 모두 손실, curl은 시간 초과(curl-rc=28)](images/console/extraA-01-vpcb-to-original.png){ .shot }

**결과(실패처럼 보이지만 맞습니다)**

- VPC-B에서는 ping이 0/3, curl이 시간 초과(`curl-rc=28`)입니다.
- 그런데 온프레미스 VM의 tcpdump에는 `10.1.1.10 > 172.20.N.10` 요청이 **도착**하고, 응답도 나갑니다.

**왜 그럴까요?**

- Transit Gateway 라우팅 테이블에 온프레미스의 원래 경로 `172.20.N.0/24`가 남아 있습니다([2-3-6](lab2.md#lab2-6)). 그래서 원래 주소로 보내면 VPC-A가 아니라 **온프레미스**로 갑니다.
- 온프레미스 VM의 응답은 DXGW 연결을 지나며 출발지가 `100.64.1.10`으로 바뀝니다. VPC-B가 보낸 목적지(`172.20.N.10`)와 응답의 출발지가 달라서, VPC-B에서는 응답을 받지 못한 것처럼 보입니다.

!!! warning "실제 환경에서 주의할 점"
    NAT를 건 VPC의 원래 주소로는 다른 네트워크가 보내지 않게 하세요. 의도하지 않은 곳(이 실습에서는 온프레미스)으로 갈 수 있습니다.

??? note "(선택) 응답은 VPC-B 어디에서 버려질까요?"
    ICMP(Internet Control Message Protocol)와 TCP(Transmission Control Protocol)는 VPC-B EC2의 보안 그룹에서 다르게 처리됩니다.

    - **TCP**: 보안 그룹은 나간 요청을 기억하고, 그 응답은 인바운드 규칙과 관계없이 허용합니다.
        - 요청은 `10.1.1.10:<curl의 임시 포트>` → `172.20.N.10:8080`입니다.
        - SYN(synchronize)-ACK(acknowledgment)는 `100.64.1.10:8080` → `10.1.1.10:<curl의 임시 포트>`로 옵니다. 출발지가 요청의 목적지와 달라 응답으로 인식되지 않습니다.
        - 그래서 새로 들어오는 트래픽으로 인바운드 규칙을 봅니다. 규칙의 TCP 8080은 VPC-B EC2 쪽 목적지 포트입니다. SYN-ACK의 목적지 포트는 curl의 임시 포트라 맞는 규칙이 없어 거부됩니다(**REJECT**).
    - **ICMP**: 인바운드 규칙이 `100.64.1.0/24`의 ICMP를 모두 허용합니다. 그래서 응답으로 인식되지 않아도 보안 그룹에서 막히지 않습니다.
        - 응답은 VPC-B EC2까지 실제로 도착합니다(아래 tcpdump). 그런데도 ping이 0/3인 것은 보낸 주소와 다른 주소에서 온 응답을 ping이 성공으로 세지 않기 때문으로 보입니다(추론).

    TCP 거부는 VPC Flow Logs로 확인할 수 있습니다. 사전 테스트에서 이 **REJECT** 기록을 확인했습니다. 로그는 몇 분 늦게 나타나므로 3~5분 기다린 뒤 [3-3-2](extra-c.md#c2)와 같은 방법으로 로그 그룹 `/tgwnat/vpc-flow-logs`에서 아래 쿼리를 실행합니다.

    ```text
    parse @message "* * * * * * * * * * * * * * * * * * * *" as ver, vpc, eni, srcaddr, dstaddr, pkt_srcaddr, pkt_dstaddr, srcport, dstport, proto, packets, bytes, flags, iptype, tstart, tend, action, status, direction, path
    | filter srcaddr = "100.64.1.10" and dstaddr = "10.1.1.10" and action = "REJECT"
    | display @timestamp, srcaddr, srcport, dstaddr, dstport, proto, action
    | sort @timestamp desc
    | limit 10
    ```

    - `proto`가 `6`(TCP), `srcport`가 `8080`인 기록이 이 실습에서 예상하는 TCP 응답(SYN-ACK)의 거부 기록입니다. `dstport`는 curl의 임시 포트입니다. 이 쿼리는 TCP 플래그(`flags`)를 표시하지 않습니다. 개별 패킷이 SYN-ACK인지까지 보려면 온프레미스 VM의 tcpdump에서 `Flags [S.]`를 확인합니다.
    - 보안 그룹이 ICMP를 허용하므로 `proto`가 `1`(ICMP)인 기록은 나오지 않습니다.
    - 사전 테스트(Pod 89)에서 이 쿼리를 실행하면 `srcport` `8080`, `dstport` `58660`(curl의 임시 포트)인 REJECT 기록 2건이 나왔고, ICMP 기록은 없었습니다.

    VPC-B EC2에 무엇이 도착하는지는 VPC-B EC2 터미널의 tcpdump로 직접 볼 수 있습니다. 온프레미스 VM의 웹 서버가 떠 있는 상태에서 실행합니다.

    ```bash
    sudo timeout 15 tcpdump -nli ens5 'icmp or tcp port 8080' &
    ping -c 3 -W 2 172.20.N.10
    curl -s -m 5 -o /dev/null -w 'HTTP %{http_code}\n' http://172.20.N.10:8080/
    ```

    `curl` 옵션은 [2-3-7](lab2.md#lab2-7)과 같고, `-m 5`는 5초 안에 끝나지 않으면 멈춥니다. 응답을 받지 못하면 `HTTP 000`이 나옵니다. 서버가 보낸 상태 코드가 아니라 응답이 없었다는 뜻입니다.

    사전 테스트(Pod 89)에서 나온 출력의 일부입니다.

    ```text
    IP 10.1.1.10 > 172.20.89.10: ICMP echo request, id 30932, seq 1, length 64
    IP 100.64.1.10 > 10.1.1.10: ICMP echo reply, id 30932, seq 1, length 64
    IP 10.1.1.10.58660 > 172.20.89.10.webcache: Flags [S], seq 432682825, ...
    IP 10.1.1.10.58660 > 172.20.89.10.webcache: Flags [S], seq 432682825, ...
    ```

    - ICMP 응답(`echo reply`)은 출발지가 `100.64.1.10`으로 바뀐 채 VPC-B EC2에 도착합니다.
    - TCP는 `Flags [S]`(SYN)만 다시 보내집니다. 응답(SYN-ACK)은 보안 그룹에서 거부되어 EC2까지 오지 않습니다.

끝나면 tcpdump는 **Ctrl+C**, 백그라운드로 실행한 온프레미스 VM의 웹 서버는 `kill %1`로 멈춥니다.

## 3-1-4. 규칙에 없는 출발지 { #a4 }

온프레미스 라우터(`rtN`) 터미널에서 Loopback1(`10.200.0.1`)을 출발지로 VPC-B에 보냅니다.

```text
telnet 10.1.1.10 8080 /source-interface Loopback1
```

`Open`이 나오면 아래 줄을 넣고 Enter를 **두 번** 누릅니다. 응답 없이 바로 끊기면 [2-2-6](lab1.md#lab1-6)의 안내를 보세요.

```text
GET / HTTP/1.0
```

**결과**: `vpc-b-ec2 saw 10.200.0.1:<포트>`입니다.

**왜 그럴까요?** 규칙의 원래 대역(`172.20.N.0/24`)에 없는 출발지는 DXGW 연결을 지나도 바뀌지 않습니다.

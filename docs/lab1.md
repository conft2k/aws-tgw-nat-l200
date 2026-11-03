# 실습 1. Direct Connect 연결 (25분)

온프레미스 라우터를 AWS의 Transit Gateway까지 연결합니다. 아직 NAT는 걸지 않습니다.

아래 그림의 번호 순서로 만듭니다. ①(hosted connection 수락)은 실습 0에서 이미 했습니다.

![Direct Connect 연결 구성: 라우터의 서브인터페이스 2개가 hosted connection 2개와 전송 가상 인터페이스 2개를 거쳐 Direct Connect gateway와 Transit Gateway에 연결된다. 라우터는 172.20.N.0/24와 10.200.0.1/32를 광고하고, 허용된 접두사 100.64.2.0/24와 10.1.1.0/24를 받는다](images/diagrams/lab1-dx-build.png)

시작하기 전에 확인합니다.

- 실습 0의 hosted connection 2개가 **Available**인가요?
- 스택 `tgw-nat-workshop`이 **CREATE_COMPLETE**인가요? 아직이면 1-1과 1-3을 먼저 하고, 스택이 끝나면 1-2를 합니다.

## 1-1. Direct Connect gateway 만들기 { #lab1-1 }

1. **Direct Connect** 콘솔 → **Direct Connect gateways** → **Create Direct Connect gateway**를 누릅니다.
2. **Name**에 `tgw-nat-dxgw`, **Amazon-side ASN**에 `65300`을 넣고 **Create Direct Connect gateway**를 누릅니다.

![Create Direct Connect gateway 화면: Name tgw-nat-dxgw, Amazon-side ASN 65300](images/console/lab1-dxgw-02-create.png){ .shot }

ASN은 BGP에서 쓰는 번호입니다. 이 워크숍은 라우터 65000, Direct Connect gateway 65300, Transit Gateway 65400으로 서로 다르게 씁니다.

## 1-2. Transit Gateway와 연결하기 { #lab1-2 }

게이트웨이 연결은 몇 분 걸리므로 일찍 시작해 둡니다.

1. **Direct Connect gateways** 목록에서 방금 만든 게이트웨이의 ID를 누릅니다(목록에는 이름 대신 ID가 보입니다).
2. **Gateway associations** 탭 → **Associate gateway**를 누릅니다.
3. **Gateway**에서 스택이 만든 Transit Gateway(`tgwnat-tgw`)를 고릅니다.
4. **Allowed prefixes**에 아래 두 줄을 넣고 **Associate gateway**를 누릅니다.

    ```text
    100.64.2.0/24
    10.1.1.0/24
    ```

![Associate gateway 화면: Gateway는 tgwnat-tgw, Allowed prefixes는 100.64.2.0/24와 10.1.1.0/24](images/console/lab1-assoc-02-form.png){ .shot }

허용된 접두사는 온프레미스 라우터에 **그대로 광고**됩니다. 그래서 VPC-A의 실제 대역(`172.20.N.0/24`)은 넣지 않습니다. 온프레미스와 같은 대역이라 받아도 쓸 수 없기 때문입니다. 대신 VPC-A가 NAT 뒤에 보일 대역 `100.64.2.0/24`를 넣습니다.

**성공 확인**: 상태가 **associating**에서 약 3분 뒤 **associated**가 됩니다.

## 1-3. 전송 가상 인터페이스 2개 만들기 { #lab1-3 }

hosted connection마다 하나씩 만듭니다.

1. **Virtual interfaces** → **Create virtual interface**를 누릅니다.
2. **Virtual interface type**에서 **Transit**을 고릅니다.
3. 아래 값을 넣습니다.

    | 항목 | 첫 번째 | 두 번째 |
    |---|---|---|
    | Virtual interface name | `tgw-nat-vif1` | `tgw-nat-vif2` |
    | Connection | `awsdx1_…` | `awsdx2_…` |
    | Direct Connect gateway | `tgw-nat-dxgw` | `tgw-nat-dxgw` |
    | VLAN | 자동으로 채워짐 | 자동으로 채워짐 |
    | BGP ASN | `65000` | `65000` |

4. **Additional settings**는 그대로 둡니다. 라우터와 주고받을 IP와 BGP 키는 AWS가 만들어 줍니다.
5. **Create virtual interface**를 누릅니다. 두 번째도 같은 방법으로 만듭니다.

![Create virtual interface 화면: Connection awsdx1_189, Direct Connect gateway tgw-nat-dxgw, VLAN 189(자동, 회색), BGP ASN 65000](images/console/lab1-vif1-01-form.png){ .shot }

hosted connection 하나에는 전송 가상 인터페이스를 하나만 만들 수 있습니다. 잘못 만들었으면 지우고 다시 만듭니다.

**성공 확인**: 두 인터페이스의 상태가 **Pending** 또는 **Down**입니다. 라우터 설정을 마치면 **Available**이 됩니다.

## 1-4. BGP 값 확인 { #lab1-4 }

1. **Virtual interfaces**에서 `tgw-nat-vif1`의 ID를 누릅니다.
2. **Peerings** 탭에서 세 값을 적습니다: **BGP authentication key**, **Your router peer IP**, **Amazon router peer IP**.
3. `tgw-nat-vif2`도 같은 값을 적습니다.

![Peerings 탭(라우터 설정 뒤 화면): BGP ASN 65000, BGP 키(가림), Your router peer IP 169.254.96.54/29, Amazon router peer IP 169.254.96.49/29, BGP status Up](images/console/lab1-vif-05-peering.png){ .shot }

위 화면은 라우터 설정을 마친 뒤의 모습입니다. 지금은 **BGP status**가 **Down**이어도 괜찮습니다.

## 1-5. 라우터 설정 { #lab1-5 }

1. [라우터 설정 생성기](router-config.md)를 새 탭으로 엽니다.
2. 페이지 위 그림에서 각 값이 어디에 쓰이는지 번호로 확인합니다. Pod 번호는 ①에 넣습니다. LAN 대역(②)은 자동으로 채워집니다. Loopback1, ASN, 라우터 인터페이스는 워크숍 값이 미리 채워져 있습니다. ASN(④⑤)이 1-1, 1-3에서 넣은 값과 같은지만 봅니다. `tgw-nat-vif1` 값은 DX1(⑦–⑩), `tgw-nat-vif2` 값은 DX2(⑫–⑮) 칸에 넣습니다. 설정이 만들어지면 **복사**를 누릅니다.
3. 라우터 `rtN` 웹 터미널에 붙여 넣습니다. `%`로 시작하는 오류가 없으면 됩니다.

설정이 하는 일은 [라우터 설정 생성기](router-config.md#explain) 페이지에 설명해 두었습니다.

??? tip "콘솔의 Sample configuration"
    전송 가상 인터페이스의 **Actions** → **Sample configuration**에서도 라우터 설정 예시를 내려받을 수 있습니다. 다만 이 실습의 라우터 종류가 목록에 없어 손볼 곳이 많습니다. 그래서 생성기를 씁니다.

## 1-6. 연결 확인 { #lab1-6 }

라우터에서 실행합니다.

```text
show ip bgp summary | begin Neighbor
show ip bgp | begin Network
```

![라우터 웹 터미널: BGP 이웃 2개가 각각 경로 2개를 받았고, 10.1.1.0/24와 100.64.2.0/24가 두 경로로 보인다](images/portal/lab1-rt-bgp.png){ .shot }

**성공 확인**

- 두 이웃의 마지막 칸이 숫자 `2`입니다. `Active`나 `Idle`이면 [문제 해결](troubleshooting.md)을 보세요.
- `10.1.1.0/24`와 `100.64.2.0/24`를 받았습니다. 1-2에서 넣은 허용된 접두사입니다.
- 콘솔의 두 전송 가상 인터페이스가 **Available**, **BGP status**가 **Up**입니다.

이제 VPC-B까지 통신해 봅니다. Loopback1은 라우터 안의 가상 인터페이스입니다. 주소 `10.200.0.1`은 NAT 규칙의 원래 대역에 없으므로 바뀌지 않습니다.

```text
ping 10.1.1.10 source Loopback1 repeat 5
telnet 10.1.1.10 8080 /source-interface Loopback1
```

`telnet`이 연결되면 `GET / HTTP/1.0`을 입력하고 Enter를 두 번 누릅니다.

**성공 확인**: ping이 `!!!!!`이고, 응답에 `vpc-b-ec2 saw 10.200.0.1:<포트>`가 보입니다. VPC-B가 보낸 쪽 주소를 바뀌지 않은 그대로 봤다는 뜻입니다.

## 1-7. 라우팅 테이블 보기 { #lab1-7 }

**VPC** 콘솔 → **Transit gateway route tables** → 라우팅 테이블 ID → **Routes** 탭을 엽니다.

![Transit Gateway 라우팅 테이블: 10.1.1.0/24(VPC), 10.200.0.1/32(Direct Connect Gateway), 172.20.89.0/24(VPC) 세 경로가 Propagated](images/console/lab1-tgw-rt-01-before-nat.png){ .shot }

`172.20.N.0/24`가 VPC-A 하나만 가리킵니다. 온프레미스도 같은 대역을 광고했지만 보이지 않습니다. 같은 대역이면 VPC의 경로가 우선하기 때문입니다. 실습 2에서 이 때문에 생기는 문제를 확인합니다.

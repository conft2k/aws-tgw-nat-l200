# 구성도 생성 스크립트

`docs/images/**/*.draft.svg`는 이 폴더의 스크립트가 좌표를 계산해 만든 파일입니다. 사이트에 보이는 `.svg`와 `.png`는 그 draft를 skill-aws-arch-diagram의 `export.py`로 내보낸 결과입니다. 문구나 위치를 고칠 때는 draft를 직접 고치지 말고 스크립트를 고친 뒤 다시 만듭니다. draft만 고치면 다음에 스크립트로 다시 만들 때 그 수정이 사라집니다.

## 사용법

```bash
tools/diagrams/build.sh --check          # 스크립트 결과가 저장소의 draft와 같은지 확인(파일은 바꾸지 않음)
tools/diagrams/build.sh extra-b          # 하나만 다시 만들기: draft → check_layout → SVG + PNG(가로 2배)
tools/diagrams/build.sh                  # 10개 모두
```

- 필요한 것: `~/.claude/skills/skill-aws-arch-diagram`(다른 곳이면 `SKILL_DIR`로 지정), `uv`
- 고치기 전에 `--check`가 모두 `same`인지 먼저 봅니다. `differs`가 있으면 누군가 draft를 직접 고친 것이니, 그 수정을 스크립트에 먼저 옮깁니다.
- `check_layout.py`가 TGW 라우팅 표 안의 CIDR(`100.64.1.0/24` 등)을 "CIDR OFF HEADER"로 알리는 것은 알려진 오탐입니다. 나머지 경고는 고칩니다.

## 스크립트

| 이름 | 스크립트 | 구성도 | 쓰는 페이지 |
|---|---|---|---|
| `architecture` | `architecture.py` | `images/architecture` | 1-1 |
| `concept-snat-dnat` | `concept_snat_dnat.py` | `images/diagrams/concept-snat-dnat` | 2-3, 4-2 |
| `lab1-dx-build` | `lab1_dx_build.py` | `images/diagrams/lab1-dx-build` | 2-2 |
| `lab2-overlap-problem` | `lab2_overlap.py` | `images/diagrams/lab2-overlap-problem` | 2-3 |
| `lab2-packet-walk` | `lab2_packet_walk.py` | `images/diagrams/lab2-packet-walk` | 2-3 |
| `extra-a` | `extra_a.py` | `images/diagrams/extra-a-vpcb-and-original-route` | 3-1 |
| `extra-b` | `extra_b.py` | `images/diagrams/extra-b-nat-system-routes` | 3-2 |
| `extra-c` | `extra_c.py` | `images/diagrams/extra-c-observability` | 3-3 |
| `observed` | `observed.py` | `images/diagrams/observed-loss-location` | 4-3 |
| `router-config-map` | `router_config_map.py` | `images/diagrams/router-config-map` | 4-1 |

`lib.py`(architecture, extra-a, extra-c)와 `dg.py`(extra-b, observed)는 공통 도우미입니다. 나머지는 스크립트 하나에 다 들어 있습니다. 각 스크립트는 실행할 때 900px 폭에서의 가장 작은 글자 크기 같은 값을 출력합니다.

## 그릴 때 지킨 규칙

- 사이트 본문 폭 900px에서 가장 작은 글자가 12px 이상이 되게 합니다(캔버스 폭 1,200px 이하).
- 온프레미스는 왼쪽에 두고, 폭이 모자라면 아래에 둡니다(extra-a, extra-c).
- TGW 라우팅 표는 컨테이너와 겹쳐도 되지만 맨 위에 그리고, TGW 바로 옆에 두며, 보라색 점선(`#8C4FFF`, 1.5px, `4 3`)으로 TGW와 잇습니다.
- 설명 글상자는 그림에 넣지 않고 페이지 본문의 그림 아래에 씁니다.

# AWS Transit Gateway 1:1 NAT 워크숍 (L200)

온프레미스와 AWS VPC가 같은 IP 대역을 쓸 때, Direct Connect와 AWS Transit Gateway 1:1 NAT로 양쪽을 번역해 연결하는 과정을 직접 따라 하는 워크숍입니다.

- 워크숍 사이트: https://ws.nettfc.net/aws-tgw-nat-l200/
- 진행 계획과 사전 테스트 기록: [PLAN.md](PLAN.md)

## 구성

| 경로 | 내용 |
|---|---|
| `docs/` | 사이트 본문(MkDocs Material). `docs/assets/tgw-nat-workshop.yaml`은 참가자용 CloudFormation 템플릿 |
| `docs/images/` | 구성도와 콘솔·웹 터미널 스크린샷. 계정 ID는 `111122223333`, BGP 키와 hosted connection ID는 가렸습니다. 그 밖의 리소스 ID는 사전 테스트 계정의 값입니다 |
| `tools/console.py` | 콘솔 사전 테스트와 스크린샷용 Playwright 스크립트 |
| `tools/diagrams/` | 구성도 10개의 생성 스크립트(스크립트 9개). 고치는 방법은 [`tools/diagrams/README.md`](tools/diagrams/README.md) |

## 다른 리전에서 진행할 때

사이트의 예제 화면은 아시아 태평양(서울) `ap-northeast-2` 기준이고, 참가자는 강사가 안내한 리전에 스택을 배포합니다. 템플릿은 리전 이름을 고정하지 않지만, 서울이 아닌 리전에서 진행하기 전에 강사가 다음을 확인합니다.

- 테스트 EC2(`t4g.micro`)와 EC2 Instance Connect Endpoint는 리전의 첫째 AZ에, Transit Gateway 연결 서브넷은 첫째·둘째 AZ에 만들어집니다. AZ를 고르는 파라미터는 없습니다. 첫째 AZ에서 `t4g.micro`를 쓸 수 없거나 계정의 기본 서브넷 구성 때문에 AZ가 하나만 잡히면, 각 서브넷의 `AvailabilityZone` 식을 쓸 AZ 이름으로 바꾼 템플릿을 나눠 줍니다.
- hosted connection과 전송 가상 인터페이스는 회선이 연결된 Direct Connect 위치의 리전에 속합니다. Direct Connect gateway는 글로벌 리소스라 다른 리전의 Transit Gateway에도 연결할 수 있습니다.

## 페이지 번호

사이트는 묶음(`1.`), 페이지(`1-1.`), 페이지 안 소제목(`1-1-1.`) 순서로 번호를 붙입니다. 파일 이름은 번호와 다르니 아래 표를 보세요. 순서와 번호는 `mkdocs.yml`의 `nav`와 각 페이지 제목에서 정합니다.

| 묶음 | 페이지 | 파일 |
|---|---|---|
| 1. 시작하기 전에 | 1-1. 소개 | `docs/index.md` |
| | 1-2. 사전 준비 | `docs/prerequisites.md` |
| | 1-3. 용어 풀이 | `docs/glossary.md` |
| 2. 실습 | 2-1. 시작하기 | `docs/lab0.md` |
| | 2-2. Direct Connect 연결 | `docs/lab1.md` |
| | 2-3. 1:1 NAT 적용 | `docs/lab2.md` |
| 3. 추가 과제 | 3-1. NAT 없는 VPC와 원래 경로 | `docs/extra-a.md` |
| | 3-2. 경로 설치 옵션 | `docs/extra-b.md` |
| | 3-3. 지표와 Flow Logs | `docs/extra-c.md` |
| | 3-4. 리소스 정리 | `docs/extra-d.md` |
| 4. 부록 | 4-1. 라우터 설정 생성기 | `docs/router-config.md` |
| | 4-2. 1:1 NAT 개념과 제약 | `docs/concepts.md` |
| | 4-3. 문제 해결 | `docs/troubleshooting.md` |
| | 4-4. 참고 문서 | `docs/references.md` |

## 로컬에서 보기

```bash
uv run --with mkdocs-material==9.8.0 mkdocs serve
```

## 라이선스

[MIT](LICENSE)

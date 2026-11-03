# AWS Transit Gateway 1:1 NAT 워크숍 (L200)

온프레미스와 AWS VPC가 같은 IP 대역을 쓸 때, Direct Connect와 AWS Transit Gateway 1:1 NAT로 양쪽을 번역해 연결하는 과정을 직접 따라 하는 워크숍입니다.

- 워크숍 사이트: https://conft2k.github.io/ws-aws-tgw-nat-l200/
- 진행 계획과 사전 테스트 기록: [PLAN.md](PLAN.md)

## 구성

| 경로 | 내용 |
|---|---|
| `docs/` | 사이트 본문(MkDocs Material). `docs/assets/tgw-nat-workshop.yaml`은 참가자용 CloudFormation 템플릿 |
| `docs/images/` | 구성도와 콘솔·웹 터미널 스크린샷. 계정 ID는 `111122223333`, BGP 키와 hosted connection ID는 가렸습니다. 그 밖의 리소스 ID는 사전 테스트 계정의 값입니다 |
| `tools/console.py` | 콘솔 사전 테스트와 스크린샷용 Playwright 스크립트 |

## 로컬에서 보기

```bash
uv run --with mkdocs-material==9.8.0 mkdocs serve
```

## 라이선스

[MIT](LICENSE)

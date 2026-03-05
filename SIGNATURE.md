# Terraforming Engine — 서명·검증

- **공식 릴리스**: GPG 서명된 Git 태그 또는 GitHub Releases로 배포.
- 태그 검증: `git tag -v v0.1.0`
- 외부 의존성 없음(표준 라이브러리만). 동일 커밋에서 재현 가능 빌드.

## 해시 기록 (블록체인·감사용)

- 배포 시점 커밋 해시: 로컬에서 `git rev-parse HEAD` 로 확인.
- 푸시 후 해당 SHA를 복사해 블록체인 또는 감사 로그에 기록.
- 원격: `https://github.com/qquartsco-svg/Terraforming.git` (main).

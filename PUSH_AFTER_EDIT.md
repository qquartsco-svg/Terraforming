# 수정 후 반드시 GitHub 푸시까지 완료

**규칙**: 이 리포(Terraforming_Engine)를 수정하면 **커밋 + GitHub 푸시**까지 해서 완료한다.

## 한 번에 실행

```bash
cd /Users/jazzin/Desktop/00_BRAIN/ENGINE_HUB/Terraforming_Engine
bash setup_git_and_push.sh
```

- 이미 `.git`이 있으면: `git add -A` → `commit` → `push origin main`
- `.git`이 없으면: `git init` → 첫 커밋 → `remote add` → `push`

푸시 후 터미널에 출력되는 **커밋 해시**를 블록체인/감사용으로 기록하면 된다.

#!/bin/bash
# Terraforming_Engine — 수정 후 반드시 실행. GitHub 푸시까지 완료.
# 사용법:
#   cd /Users/jazzin/Desktop/00_BRAIN/ENGINE_HUB/Terraforming_Engine
#   bash setup_git_and_push.sh
# 또는: bash push_to_github.sh  (동일)

set -e
cd "$(dirname "$0")"

if [ -d .git ]; then
  git add -A
  git status --short
  if git diff --cached --quiet; then
    echo "변경 없음. 푸시 생략."
    git rev-parse HEAD 2>/dev/null && exit 0
    exit 0
  fi
  git commit -m "Terraforming Engine: 수정 반영 — $(date +%Y-%m-%d)"
  git remote get-url origin 2>/dev/null || git remote add origin https://github.com/qquartsco-svg/Terraforming.git
  git push -u origin main
else
  echo "git init 수행..."
  git init
  git branch -M main
  git add -A
  git commit -m "Terraforming Engine: 초기 반영 (PlanetSnapshot, EdenAssessment, Plan, HDR 어댑터, README 서사 보강)"
  git remote add origin https://github.com/qquartsco-svg/Terraforming.git
  git push -u origin main
fi

echo ""
echo "커밋 해시 (블록체인/감사용):"
git rev-parse HEAD

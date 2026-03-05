#!/bin/bash
# Terraforming_Engine 폴더에서 git 초기화 후 GitHub 푸시
# 사용법: 이 스크립트를 ENGINE_HUB/Terraforming_Engine 안에 두고
#   cd /Users/jazzin/Desktop/00_BRAIN/ENGINE_HUB/Terraforming_Engine
#   bash setup_git_and_push.sh

set -e
cd "$(dirname "$0")"

if [ -d .git ]; then
  echo "이미 .git 있음. add/commit/push 만 수행."
  git add -A
  git status --short
  git diff --cached --quiet && { echo "변경 없음."; exit 0; }
  git commit -m "Terraforming Engine: PlanetSnapshot 표준, EdenAssessment/TerraformingPlan 구조, SIGNATURE"
  git remote get-url origin 2>/dev/null || git remote add origin https://github.com/qquartsco-svg/Terraforming.git
  git push -u origin main
else
  echo "git init 수행..."
  git init
  git branch -M main
  git add -A
  git commit -m "Terraforming Engine: PlanetSnapshot 표준 확정, EdenAssessment/TerraformingPlan 구조, SIGNATURE 해시 기록"
  git remote add origin https://github.com/qquartsco-svg/Terraforming.git
  git push -u origin main
fi

echo ""
echo "커밋 해시 (블록체인/감사용):"
git rev-parse HEAD

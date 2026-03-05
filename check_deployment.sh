#!/bin/bash
# Terraforming Engine 배포 구조 점검.
# 리포 루트에서 실행: bash check_deployment.sh
# 성립 시 0, 실패 시 1 반환하고 원인 출력.

set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"
FAIL=0

echo "=== Terraforming Engine 배포 점검 ==="

# 1) terraforming_engine/ 패키지 폴더 존재
if [ ! -d "terraforming_engine" ]; then
  echo "FAIL: terraforming_engine/ 폴더가 없습니다. 루트에 flat으로만 있으면 안 됩니다."
  FAIL=1
else
  echo "OK: terraforming_engine/ 존재"
fi

# 2) 필수 하위 디렉터리
for sub in joe_engine moe_engine cherubim_engine; do
  if [ ! -d "terraforming_engine/$sub" ]; then
    echo "FAIL: terraforming_engine/$sub/ 없음 (pipeline에서 import 대상 필요)"
    FAIL=1
  fi
done
[ $FAIL -eq 0 ] && echo "OK: joe_engine, moe_engine, cherubim_engine 존재"

# 3) __init__.py 가 run_survey export
if [ -f "terraforming_engine/__init__.py" ]; then
  if ! grep -q "run_survey" terraforming_engine/__init__.py; then
    echo "FAIL: terraforming_engine/__init__.py 에 run_survey export가 없습니다 (Terraforming Engine 전용이 아님)"
    FAIL=1
  else
    echo "OK: __init__.py 에 run_survey 있음"
  fi
else
  echo "FAIL: terraforming_engine/__init__.py 없음"
  FAIL=1
fi

# 4) __main__.py 가 Terraforming CLI (run_survey 사용)
if [ -f "terraforming_engine/__main__.py" ]; then
  if ! grep -q "run_survey" terraforming_engine/__main__.py; then
    echo "FAIL: terraforming_engine/__main__.py 가 run_survey를 사용하지 않음 (Terraforming CLI가 아님)"
    FAIL=1
  else
    echo "OK: __main__.py Terraforming CLI용"
  fi
else
  echo "FAIL: terraforming_engine/__main__.py 없음"
  FAIL=1
fi

# 5) pyproject.toml 이 Terraforming Engine 용
if [ -f "pyproject.toml" ]; then
  if ! grep -q 'name = "terraforming-engine"' pyproject.toml && ! grep -q 'name="terraforming-engine"' pyproject.toml; then
    echo "FAIL: pyproject.toml 이 Terraforming Engine 프로젝트가 아님 (name = terraforming-engine 이어야 함)"
    FAIL=1
  else
    echo "OK: pyproject.toml Terraforming Engine 용"
  fi
else
  echo "FAIL: pyproject.toml 없음"
  FAIL=1
fi

echo "==="
if [ $FAIL -eq 0 ]; then
  echo "배포 구조 OK. from terraforming_engine import run_survey / python -m terraforming_engine 가 동작해야 합니다."
  exit 0
else
  echo "배포 구조 불일치. README §6(잘못된 배포 vs 올바른 배포)를 확인하고 이 리포를 통째로 배포하세요."
  exit 1
fi

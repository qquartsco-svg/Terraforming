"""
Terraforming Engine CLI.
실행: python -m terraforming_engine   또는  python -m terraforming_engine /path/to/snapshot.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# 패키지 루트 = standalone_build/Terraforming_Engine
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from terraforming_engine import __version__, run_survey

DEMO_SNAPSHOT = {
    "sigma_plate": 0.1,
    "P_w": 0.5,
    "S_rot": 0.2,
    "W_surface": 1e9,
    "W_total": 1.4e9,
    "dW_surface_dt_norm": 0.0,
    "greenhouse_proxy": 0.6,
    "hydrology_stability_proxy": 0.3,
    "strip_risk_proxy": 0.2,
    "biosphere_window_score": 0.8,
}


def main() -> None:
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if path.exists():
            snap = json.loads(path.read_text())
        else:
            snap = DEMO_SNAPSHOT
    else:
        snap = DEMO_SNAPSHOT

    print("Terraforming Engine (JOE → MOE → Cherubim)", __version__)
    report = run_survey(snap)
    print()
    print("[JOE]", report.joe.summary)
    print("[MOE]", report.moe.summary)
    print("[Cherubim]", report.cherubim.summary)
    print("[Plan]", report.plan.summary)
    print()
    print("Summary:", report.summary)


if __name__ == "__main__":
    main()

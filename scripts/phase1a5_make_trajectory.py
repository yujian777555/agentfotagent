"""Phase-1A-5: generate frozen L-SHADE trajectory summary for Agent prompts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.lshade_reimpl import run_lshade
from experiments.metabox.adapter import load_function

FUNCS = [1, 10, 20]
SEEDS = [11, 22, 33]
MAX_FES = 5000


def main():
    lines = []
    for fid in FUNCS:
        for seed in SEEDS:
            p = load_function(fid)
            r = run_lshade(p._problem, max_fes=MAX_FES, seed=seed, n_init=100)
            n = r.n_history
            lines.append(
                f"L-SHADE F{fid} seed={seed}: best_raw={r.best_raw:.6g} regret={r.best_regret:.6g} "
                f"fes={r.fes} N: {n[0]}->{n[len(n)//2]}->{n[-1]}"
            )
            # sample cost curve
            cc = r.cost_curve
            k = max(1, len(cc)//8)
            lines.append("  cost samples: " + ", ".join(f"{cc[i]:.4g}" for i in range(0, len(cc), k)))
            lines.append(f"  final_pop_size={n[-1]} gens={len(n)}")
    text = "\n".join(lines)
    out = ROOT / "results" / "phase1a5"
    out.mkdir(parents=True, exist_ok=True)
    (out / "lshade_trajectory_summary.txt").write_text(text, encoding="utf-8")
    print(text)
    print("WROTE results/phase1a5/lshade_trajectory_summary.txt")


if __name__ == "__main__":
    main()

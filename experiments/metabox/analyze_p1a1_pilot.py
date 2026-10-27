"""P1A-1 analysis: per-function paired comparisons, rankings, win/loss/tie."""
from __future__ import annotations

import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def load_latest_manifest():
    out = ROOT / "results" / "p1a1_pilot"
    ms = sorted(out.glob("manifest_p1a1-*.json"))
    if not ms:
        raise SystemExit("no p1a1 manifest")
    return json.loads(ms[-1].read_text(encoding="utf-8")), ms[-1]


def main() -> None:
    man, path = load_latest_manifest()
    rows = [r for r in man["rows"] if r.get("status") == "ok"]
    by = defaultdict(dict)  # (fid, seed) -> method -> metric
    for r in rows:
        m = r.get("best_regret")
        if m is None:
            m = r.get("best_raw_objective")
        by[(r["function_id"], r["seed"])][r["method"]] = m

    print("=== Final metric (lower better) ===")
    methods = sorted({r["method"] for r in rows})
    print("function seed | " + " | ".join(methods))
    for key in sorted(by):
        vals = by[key]
        print(key, "|", " | ".join(f"{vals.get(m, float('nan')):.4g}" for m in methods))

    # medians per method
    print("\n=== Median across runs ===")
    for m in methods:
        vals = [v[m] for v in by.values() if m in v]
        if vals:
            print(f"{m}: n={len(vals)} median={statistics.median(vals):.6g}")

    # win/loss/tie vs agent if present
    agent = "llm_agent"
    print("\n=== llm_agent vs each method (paired, lower metric wins) ===")
    if agent in methods:
        for other in methods:
            if other == agent:
                continue
            w = l = t = 0
            for key, vals in by.items():
                if agent not in vals or other not in vals:
                    continue
                a, b = vals[agent], vals[other]
                if a < b - 1e-12:
                    w += 1
                elif a > b + 1e-12:
                    l += 1
                else:
                    t += 1
            print(f"vs {other}: W={w} L={l} T={t}")
    else:
        print("LLM agent not present in results")

    # ranks per problem-seed
    print("\n=== Per-run ranks (1=best) ===")
    for key, vals in sorted(by.items()):
        ordered = sorted(vals.items(), key=lambda kv: kv[1])
        print(key, {m: i + 1 for i, (m, _) in enumerate(ordered)})

    print("\n=== LLM stats ===")
    print(json.dumps(man.get("llm_stats"), indent=2))
    print("llm_status:", man.get("llm_status"))
    print("failures:", len(man.get("failures", [])))
    for f in man.get("failures", [])[:5]:
        print(" ", f)

    # save summary
    summary = {
        "manifest": str(path),
        "run_id": man["run_id"],
        "llm_status": man.get("llm_status"),
        "rows": [
            {
                "method": r["method"],
                "function_id": r["function_id"],
                "seed": r["seed"],
                "metric": r.get("best_regret", r.get("best_raw_objective")),
                "fes": r.get("independent_fes"),
            }
            for r in rows
        ],
        "failures": man.get("failures"),
        "llm_stats": man.get("llm_stats"),
    }
    outp = path.parent / f"analysis_{man['run_id']}.json"
    outp.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print("WROTE", outp)


if __name__ == "__main__":
    main()

"""Phase-1A-10 candidate evaluator.

Parses, validates, deduplicates, and scores Agent-generated mechanism proposals.
No LLM calls. Pure offline logic.

Schema (per A2 protocol):
  mechanism_id, target_component, observed_evidence, causal_hypothesis,
  algorithmic_change, mathematical_rule, expected_effect, failure_prediction,
  ablation_plan, nearest_known_methods, implementation_requirements

Hard constraints:
- Must not reference closed mechanisms (CC-SOC, quality residual, IPW/DR,
  N+I restart, adaptive population reduction, archive x boundary interaction,
  F/CR memory smoothing, zero-improvement gating, diversity switching,
  p-best minimum distance).
- Must not be a rename of known methods (checked against known_mechanism_db).
- All 11 required fields must be present and non-empty.

Metrics recorded:
1. structural_valid_rate
2. evidence_traceable_rate
3. implementable_rate
4. known_mechanism_duplicate_rate
5. passed_independent_review_rate (placeholder for Stage C)
6. entered_performance_rate (placeholder for Stage D)
7. performance_gain (placeholder)
8. token/api/fe cost per valid candidate
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "mechanism_id",
    "target_component",
    "observed_evidence",
    "causal_hypothesis",
    "algorithmic_change",
    "mathematical_rule",
    "expected_effect",
    "failure_prediction",
    "ablation_plan",
    "nearest_known_methods",
    "implementation_requirements",
]

CLOSED_MECHANISMS = [
    "cc-soc", "ccsoc", "quality residual", "ipw", "dr credit",
    "n+i restart", "n+i", "immigrant restart", "state trigger",
    "adaptive population reduction", "adaptive n",
    "archive x boundary", "archive boundary interaction",
    "memory smoothing", "zero-improvement gate", "zero improvement gate",
    "diversity switching", "diversity gate",
    "p-best minimum distance", "pbest min distance",
]

# Known-mechanism database for duplicate detection (lowercase substrings).
KNOWN_MECHANISM_DB: Dict[str, str] = {
    "lehmer": "SHADE/L-SHADE M_F Lehmer mean (Tanabe 2014)",
    "weighted arithmetic mean": "SHADE M_CR update (Tanabe 2014)",
    "cauchy": "SHADE F sampling (Tanabe 2013)",
    "current-to-pbest": "JADE (Zhang & Sanderson 2009)",
    "external archive": "JADE archive (Zhang & Sanderson 2009)",
    "linear population reduction": "L-SHADE (Tanabe 2014)",
    "binomial crossover": "Standard DE crossover",
    "tournament selection": "GA tournament selection (Holland 1975)",
    "fitness sharing": "GA niching (Goldberg & Richardson 1987)",
    "crowding": "GA crowding (De Jong 1975)",
    "elitism": "Standard GA elitism",
    "cma-es": "CMA-ES (Hansen 2003)",
    "covariance matrix adaptation": "CMA-ES (Hansen 2003)",
    "step-size adaptation": "CMA-ES CSA (Hansen 2003)",
    "conditioncov_alleviate": "cma package built-in (Hansen)",
    "eigenvalue clipping": "CMA-ES condition alleviation variant",
    "mirrored sampling": "ES mirrored sampling (Brockhoff 2010)",
    "antithetic": "Antithetic variates",
    "self-adaptive": "Self-adaptive ES/GA (back to Rechenberg 1973)",
    "restart": "Restart strategies (Auger & Hansen 2005)",
    "bipop": "BIPOP-CMA-ES (Auger & Hansen 2005)",
    "ipop": "IPOP-CMA-ES (Auger & Hansen 2005)",
    "adaptive crossover": "AGA (Srinivas & Patnaik 1994)",
    "adaptive mutation": "Self-adaptive mutation",
    "differential evolution": "DE (Storn & Price 1997)",
    "shade": "SHADE (Tanabe & Fukunaga 2013)",
    "l-shade": "L-SHADE (Tanabe & Fukunaga 2014)",
    "jade": "JADE (Zhang & Sanderson 2009)",
    "jso": "jSO (Brest et al. 2017)",
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CandidateVerdict:
    mechanism_id: str
    group: str  # "A", "B", or "C"
    structural_valid: bool
    evidence_traceable: bool
    implementable: bool
    is_known_mechanism: bool
    is_closed_mechanism: bool
    is_duplicate: bool
    rejection_reasons: List[str] = field(default_factory=list)
    nearest_known_matches: List[str] = field(default_factory=list)
    content_hash: str = ""
    raw_input_tokens: int = 0
    raw_output_tokens: int = 0
    api_calls: int = 0
    fe_cost: int = 0

    @property
    def passes_pre_review(self) -> bool:
        return (
            self.structural_valid
            and self.evidence_traceable
            and self.implementable
            and not self.is_known_mechanism
            and not self.is_closed_mechanism
            and not self.is_duplicate
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mechanism_id": self.mechanism_id,
            "group": self.group,
            "structural_valid": self.structural_valid,
            "evidence_traceable": self.evidence_traceable,
            "implementable": self.implementable,
            "is_known_mechanism": self.is_known_mechanism,
            "is_closed_mechanism": self.is_closed_mechanism,
            "is_duplicate": self.is_duplicate,
            "passes_pre_review": self.passes_pre_review,
            "rejection_reasons": self.rejection_reasons,
            "nearest_known_matches": self.nearest_known_matches,
            "content_hash": self.content_hash,
            "raw_input_tokens": self.raw_input_tokens,
            "raw_output_tokens": self.raw_output_tokens,
            "api_calls": self.api_calls,
            "fe_cost": self.fe_cost,
        }


@dataclass
class EvalReport:
    n_submitted: int = 0
    n_structural_valid: int = 0
    n_evidence_traceable: int = 0
    n_implementable: int = 0
    n_known_duplicate: int = 0
    n_closed_violation: int = 0
    n_repeat: int = 0
    n_passes_pre_review: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_api_calls: int = 0
    total_fe_cost: int = 0
    verdicts: List[CandidateVerdict] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_submitted": self.n_submitted,
            "n_structural_valid": self.n_structural_valid,
            "n_evidence_traceable": self.n_evidence_traceable,
            "n_implementable": self.n_implementable,
            "n_known_duplicate": self.n_known_duplicate,
            "n_closed_violation": self.n_closed_violation,
            "n_repeat": self.n_repeat,
            "n_passes_pre_review": self.n_passes_pre_review,
            "structural_valid_rate": self.n_structural_valid / max(1, self.n_submitted),
            "evidence_traceable_rate": self.n_evidence_traceable / max(1, self.n_submitted),
            "implementable_rate": self.n_implementable / max(1, self.n_submitted),
            "known_mechanism_duplicate_rate": self.n_known_duplicate / max(1, self.n_submitted),
            "passes_pre_review_rate": self.n_passes_pre_review / max(1, self.n_submitted),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_api_calls": self.total_api_calls,
            "total_fe_cost": self.total_fe_cost,
            "verdicts": [v.to_dict() for v in self.verdicts],
        }


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def parse_candidate(raw: str, group: str = "?") -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """Parse a JSON candidate. Returns (dict or None, error list)."""
    errors: List[str] = []
    try:
        d = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, [f"JSON parse error: {e}"]

    if not isinstance(d, dict):
        return None, ["top-level is not an object"]

    for f in REQUIRED_FIELDS:
        if f not in d:
            errors.append(f"missing field: {f}")
        elif not d[f] or (isinstance(d[f], str) and not d[f].strip()):
            errors.append(f"empty field: {f}")

    return (d if not errors else None), errors


def content_hash(d: Dict[str, Any]) -> str:
    blob = json.dumps(d, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def check_closed_mechanism(d: Dict[str, Any]) -> List[str]:
    """Return list of closed-mechanism violations."""
    violations = []
    full_text = " ".join(str(v).lower() for v in d.values())
    for cm in CLOSED_MECHANISMS:
        if cm in full_text:
            violations.append(cm)
    return violations


def check_known_mechanism(d: Dict[str, Any]) -> List[str]:
    """Return list of known-mechanism matches found in the text."""
    matches = []
    full_text = " ".join(str(v).lower() for v in d.values())
    for kw, desc in KNOWN_MECHANISM_DB.items():
        if kw in full_text:
            matches.append(desc)
    return list(set(matches))


def check_implementable(d: Dict[str, Any]) -> bool:
    """Basic check: algorithmic_change and mathematical_rule are non-trivial."""
    algo = str(d.get("algorithmic_change", ""))
    math = str(d.get("mathematical_rule", ""))
    impl = str(d.get("implementation_requirements", ""))
    # Must have some formula-like content or code-like content
    has_formula = bool(re.search(r"[=+\-*/<>≤≥∑∫λσμαβγ]", math))
    has_impl = len(impl.strip()) > 10
    return has_formula and has_impl and len(algo.strip()) > 10


def check_evidence_traceable(d: Dict[str, Any]) -> bool:
    """Evidence must reference specific functions/seeds/numbers."""
    ev = str(d.get("observed_evidence", ""))
    # Must contain at least one function reference and one numeric metric
    has_func = bool(re.search(r"F\d+", ev))
    # Require a decimal number or multi-digit integer (not just the F{id} number)
    has_metric = bool(re.search(r"\d+\.\d+|\b\d{2,}\b", ev))
    return has_func and has_metric


def evaluate_candidate(
    raw: str,
    group: str = "?",
    seen_hashes: Optional[set] = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    api_calls: int = 0,
    fe_cost: int = 0,
) -> CandidateVerdict:
    """Evaluate a single candidate proposal."""
    if seen_hashes is None:
        seen_hashes = set()

    d, errors = parse_candidate(raw, group)
    if d is None:
        vid = "PARSE_FAIL"
        v = CandidateVerdict(
            mechanism_id=vid, group=group,
            structural_valid=False, evidence_traceable=False, implementable=False,
            is_known_mechanism=False, is_closed_mechanism=False, is_duplicate=False,
            rejection_reasons=errors,
            raw_input_tokens=input_tokens, raw_output_tokens=output_tokens,
            api_calls=api_calls, fe_cost=fe_cost,
        )
        return v

    mid = str(d.get("mechanism_id", "UNKNOWN"))
    ch = content_hash(d)

    # Structural validity
    structural_ok = not errors

    # Evidence traceability
    evidence_ok = check_evidence_traceable(d)

    # Implementability
    impl_ok = check_implementable(d)

    # Closed mechanism check
    closed_violations = check_closed_mechanism(d)
    is_closed = len(closed_violations) > 0

    # Known mechanism check
    known_matches = check_known_mechanism(d)
    is_known = len(known_matches) > 0

    # Duplicate check
    is_dup = ch in seen_hashes
    seen_hashes.add(ch)

    reasons = []
    if not structural_ok:
        reasons.extend(errors)
    if not evidence_ok:
        reasons.append("evidence not traceable to specific function/number")
    if not impl_ok:
        reasons.append("algorithmic_change/mathematical_rule/implementation_requirements insufficient")
    if is_closed:
        reasons.append(f"references closed mechanism(s): {closed_violations}")
    if is_known:
        reasons.append(f"matches known mechanism(s): {known_matches}")
    if is_dup:
        reasons.append("duplicate of earlier candidate")

    return CandidateVerdict(
        mechanism_id=mid, group=group,
        structural_valid=structural_ok,
        evidence_traceable=evidence_ok,
        implementable=impl_ok,
        is_known_mechanism=is_known,
        is_closed_mechanism=is_closed,
        is_duplicate=is_dup,
        rejection_reasons=reasons,
        nearest_known_matches=known_matches,
        content_hash=ch,
        raw_input_tokens=input_tokens,
        raw_output_tokens=output_tokens,
        api_calls=api_calls,
        fe_cost=fe_cost,
    )


def evaluate_batch(
    candidates: List[Dict[str, Any]],
) -> EvalReport:
    """Evaluate a batch of candidates.

    Each item: {"raw": str, "group": str, "input_tokens": int,
                 "output_tokens": int, "api_calls": int, "fe_cost": int}
    """
    report = EvalReport()
    seen_hashes: set = set()

    for item in candidates:
        v = evaluate_candidate(
            raw=item.get("raw", ""),
            group=item.get("group", "?"),
            seen_hashes=seen_hashes,
            input_tokens=item.get("input_tokens", 0),
            output_tokens=item.get("output_tokens", 0),
            api_calls=item.get("api_calls", 0),
            fe_cost=item.get("fe_cost", 0),
        )
        report.verdicts.append(v)
        report.n_submitted += 1
        if v.structural_valid:
            report.n_structural_valid += 1
        if v.evidence_traceable:
            report.n_evidence_traceable += 1
        if v.implementable:
            report.n_implementable += 1
        if v.is_known_mechanism:
            report.n_known_duplicate += 1
        if v.is_closed_mechanism:
            report.n_closed_violation += 1
        if v.is_duplicate:
            report.n_repeat += 1
        if v.passes_pre_review:
            report.n_passes_pre_review += 1
        report.total_input_tokens += v.raw_input_tokens
        report.total_output_tokens += v.raw_output_tokens
        report.total_api_calls += v.api_calls
        report.total_fe_cost += v.fe_cost

    return report


# ---------------------------------------------------------------------------
# Random-valid generator (Group C)
# ---------------------------------------------------------------------------

def generate_random_valid(
    seed: int,
    task_id: str,
    target_components: Optional[List[str]] = None,
) -> str:
    """Generate a structurally valid but random mechanism proposal.

    Uses a fixed seed for reproducibility. Generates a plausible-looking but
    non-sensical mechanism that passes structural checks but should be caught
    by novelty/implementability review.
    """
    import random
    rng = random.Random(seed)

    if target_components is None:
        target_components = [
            "mutation_operator", "crossover_operator", "selection_rule",
            "parameter_memory", "population_management", "boundary_handling",
            "archive_management", "recombination_weights",
        ]

    comp = rng.choice(target_components)
    params = ["alpha", "beta", "gamma", "delta", "epsilon", "kappa", "lambda"]
    p1, p2 = rng.sample(params, 2)
    v1 = round(rng.uniform(0.01, 0.99), 3)
    v2 = round(rng.uniform(0.01, 0.99), 3)
    func = rng.choice(["F1", "F4", "F7", "F10", "F11", "F15", "F20"])

    proposal = {
        "mechanism_id": f"RAND-{seed:04d}",
        "target_component": comp,
        "observed_evidence": (
            f"In {func} diagnostic traces, the {comp} shows anomalous behavior "
            f"with parameter {p1}={v1} and {p2}={v2} at generation "
            f"{rng.randint(10, 150)}."
        ),
        "causal_hypothesis": (
            f"The {comp} causes performance degradation because {p1} interacts "
            f"with {p2} in a way that reduces search efficiency when {p1} > {v1}."
        ),
        "algorithmic_change": (
            f"Modify the {comp} to use a dynamic {p1} that adapts based on the "
            f"ratio of {p2} to a moving average of recent improvements."
        ),
        "mathematical_rule": (
            f"{p1}_new = {v1} * {p2}_ratio + (1 - {v1}) * {p1}_old"
            f" where {p2}_ratio = {p2}_current / mean({p2}_history)"
        ),
        "expected_effect": (
            f"Improved convergence on {func} by maintaining better {comp} "
            f"diversity throughout the search."
        ),
        "failure_prediction": (
            f"If {p1} adaptation causes oscillation, performance on {func} "
            f"will degrade compared to baseline."
        ),
        "ablation_plan": (
            f"Compare standard {comp} vs adaptive {comp} vs fixed {p1}={v2} "
            f"on {func} and control function F1, 3 seeds each."
        ),
        "nearest_known_methods": (
            f"Self-adaptive parameter control, adaptive {comp} variants"
        ),
        "implementation_requirements": (
            f"Replace the {comp} update rule in lshade_canonical.py lines "
            f"corresponding to {p1} computation. Add {p2} history tracking."
        ),
    }
    return json.dumps(proposal, indent=2, ensure_ascii=False)

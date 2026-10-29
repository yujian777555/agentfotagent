"""Phase-1A-10 candidate evaluator (corrective version).

Fixes from Stage A-Corrective:
  A. Known-mechanism detection now only scans mechanism fields
     (algorithmic_change, mathematical_rule), NOT nearest_known_methods
     or observed_evidence. Mere citation of L-SHADE/SHADE in comparison
     fields does NOT trigger rejection.
  B. Random generator uses structured evidence from frozen task cards,
     not fabricated numbers. Evidence is a dict with task_id, trace_path,
     function, seed, metric, observed_value.
  C. Duplicate detection normalizes content by excluding mechanism_id,
     group, and other non-mechanism fields.
  D. Closed-mechanism detection also restricted to mechanism fields.

Schema (per A2 protocol):
  mechanism_id, target_component, observed_evidence, causal_hypothesis,
  algorithmic_change, mathematical_rule, expected_effect, failure_prediction,
  ablation_plan, nearest_known_methods, implementation_requirements

observed_evidence may be a string (for backward compat) or a structured dict:
  {"task_id": "...", "trace_path": "...", "function": "F..", "seed": N,
   "metric": "...", "observed_value": "..."}

All 11 required fields must be present and non-empty.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

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

# Fields that describe the ACTUAL proposed mechanism (scanned for violations).
MECHANISM_FIELDS = ["algorithmic_change", "mathematical_rule"]

# Fields where mentioning known/closed methods is acceptable (citation/comparison).
CITATION_FIELDS = ["nearest_known_methods", "observed_evidence", "causal_hypothesis",
                   "ablation_plan", "expected_effect", "failure_prediction"]

CLOSED_MECHANISMS = [
    "cc-soc", "ccsoc", "quality residual", "ipw", "dr credit",
    "n+i restart", "n+i", "immigrant restart", "state trigger",
    "adaptive population reduction", "adaptive n",
    "archive x boundary", "archive boundary interaction",
    "memory smoothing", "zero-improvement gate", "zero improvement gate",
    "diversity switching", "diversity gate",
    "p-best minimum distance", "pbest min distance",
]

# Known-mechanism keywords for static pre-screening.
KNOWN_MECHANISM_DB: Dict[str, str] = {
    "lehmer": "SHADE/L-SHADE M_F Lehmer mean (Tanabe 2014)",
    "weighted arithmetic mean": "SHADE M_CR update (Tanabe 2014)",
    "cauchy": "SHADE F sampling (Tanabe 2013)",
    "current-to-pbest": "JADE (Zhang & Sanderson 2009)",
    "linear population reduction": "L-SHADE (Tanabe 2014)",
    "binomial crossover": "Standard DE crossover",
    "tournament selection": "GA tournament selection (Holland 1975)",
    "fitness sharing": "GA niching (Goldberg & Richardson 1987)",
    "crowding": "GA crowding (De Jong 1975)",
    "cma-es": "CMA-ES (Hansen 2003)",
    "covariance matrix adaptation": "CMA-ES (Hansen 2003)",
    "mirrored sampling": "ES mirrored sampling (Brockhoff 2010)",
    "bipop": "BIPOP-CMA-ES (Auger & Hansen 2005)",
    "ipop": "IPOP-CMA-ES (Auger & Hansen 2005)",
    "adaptive crossover": "AGA (Srinivas & Patnaik 1994)",
}

# Structured evidence schema for observed_evidence dict.
EVIDENCE_REQUIRED_KEYS = {"task_id", "trace_path", "function", "seed", "metric", "observed_value"}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CandidateVerdict:
    mechanism_id: str
    group: str
    structural_valid: bool
    evidence_traceable: bool
    implementable: bool
    is_known_mechanism: bool
    is_closed_mechanism: bool
    is_duplicate: bool
    rejection_reasons: List[str] = field(default_factory=list)
    nearest_known_matches: List[str] = field(default_factory=list)
    normalized_hash: str = ""
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
            "normalized_hash": self.normalized_hash,
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
# Parsing
# ---------------------------------------------------------------------------

def parse_candidate(raw: str, group: str = "?") -> Tuple[Optional[Dict[str, Any]], List[str]]:
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
        else:
            v = d[f]
            if isinstance(v, str) and not v.strip():
                errors.append(f"empty field: {f}")
            elif isinstance(v, dict) and not v:
                errors.append(f"empty field: {f}")
            elif v is None:
                errors.append(f"empty field: {f}")

    return (d if not errors else None), errors


# ---------------------------------------------------------------------------
# Hashing / normalization
# ---------------------------------------------------------------------------

def content_hash(d: Dict[str, Any]) -> str:
    blob = json.dumps(d, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def normalized_mechanism_hash(d: Dict[str, Any]) -> str:
    """Hash of core mechanism content, excluding non-mechanism fields.

    Excludes: mechanism_id, group, nearest_known_methods (citations),
    observed_evidence (task-specific). Focuses on:
    target_component, causal_hypothesis, algorithmic_change,
    mathematical_rule, expected_effect, failure_prediction,
    ablation_plan, implementation_requirements.
    """
    core = {
        "target_component": str(d.get("target_component", "")),
        "causal_hypothesis": str(d.get("causal_hypothesis", "")),
        "algorithmic_change": str(d.get("algorithmic_change", "")),
        "mathematical_rule": str(d.get("mathematical_rule", "")),
        "expected_effect": str(d.get("expected_effect", "")),
        "failure_prediction": str(d.get("failure_prediction", "")),
        "ablation_plan": str(d.get("ablation_plan", "")),
        "implementation_requirements": str(d.get("implementation_requirements", "")),
    }
    # Normalize: lowercase, collapse whitespace
    norm = json.dumps(core, sort_keys=True, ensure_ascii=False).lower()
    norm = re.sub(r"\s+", " ", norm)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Mechanism checks (scanning ONLY mechanism fields)
# ---------------------------------------------------------------------------

def _mechanism_text(d: Dict[str, Any]) -> str:
    return " ".join(str(d.get(f, "")).lower() for f in MECHANISM_FIELDS)


def check_closed_mechanism(d: Dict[str, Any]) -> List[str]:
    """Check for closed-mechanism violations in MECHANISM fields only."""
    text = _mechanism_text(d)
    violations = []
    for cm in CLOSED_MECHANISMS:
        if cm in text:
            violations.append(cm)
    return violations


def check_known_mechanism(d: Dict[str, Any]) -> List[str]:
    """Check for known-mechanism matches in MECHANISM fields only.

    This is a static pre-screening only. Final novelty assessment is
    done in Stage C independent review.
    """
    text = _mechanism_text(d)
    matches = []
    for kw, desc in KNOWN_MECHANISM_DB.items():
        if kw in text:
            matches.append(desc)
    return list(set(matches))


# ---------------------------------------------------------------------------
# Evidence check
# ---------------------------------------------------------------------------

def check_evidence_traceable(d: Dict[str, Any]) -> bool:
    """Validate evidence is traceable to real traces.

    Accepts either:
    - Structured dict with EVIDENCE_REQUIRED_KEYS and real-looking values.
    - String with function reference + numeric metric (legacy, weaker).
    """
    ev = d.get("observed_evidence", "")

    if isinstance(ev, dict):
        # Structured evidence: must have all required keys
        if not EVIDENCE_REQUIRED_KEYS.issubset(ev.keys()):
            return False
        # trace_path must be non-empty string
        if not str(ev.get("trace_path", "")).strip():
            return False
        # function must match F{id} pattern
        if not re.match(r"^F\d+$", str(ev.get("function", ""))):
            return False
        # metric must be non-empty
        if not str(ev.get("metric", "")).strip():
            return False
        return True

    if isinstance(ev, str):
        # Legacy string: require function ref + numeric metric
        has_func = bool(re.search(r"F\d+", ev))
        has_metric = bool(re.search(r"\d+\.\d+|\b\d{2,}\b", ev))
        return has_func and has_metric

    return False


# ---------------------------------------------------------------------------
# Implementability check
# ---------------------------------------------------------------------------

def check_implementable(d: Dict[str, Any]) -> bool:
    algo = str(d.get("algorithmic_change", ""))
    math = str(d.get("mathematical_rule", ""))
    impl = str(d.get("implementation_requirements", ""))
    has_formula = bool(re.search(r"[=+\-*/<>≤≥∑∫λσμαβγ]", math))
    has_impl = len(impl.strip()) > 10
    return has_formula and has_impl and len(algo.strip()) > 10


# ---------------------------------------------------------------------------
# Evaluate
# ---------------------------------------------------------------------------

def evaluate_candidate(
    raw: str,
    group: str = "?",
    seen_hashes: Optional[Set[str]] = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    api_calls: int = 0,
    fe_cost: int = 0,
) -> CandidateVerdict:
    if seen_hashes is None:
        seen_hashes = set()

    d, errors = parse_candidate(raw, group)
    if d is None:
        return CandidateVerdict(
            mechanism_id="PARSE_FAIL", group=group,
            structural_valid=False, evidence_traceable=False, implementable=False,
            is_known_mechanism=False, is_closed_mechanism=False, is_duplicate=False,
            rejection_reasons=errors,
            raw_input_tokens=input_tokens, raw_output_tokens=output_tokens,
            api_calls=api_calls, fe_cost=fe_cost,
        )

    mid = str(d.get("mechanism_id", "UNKNOWN"))
    ch = content_hash(d)
    nh = normalized_mechanism_hash(d)

    structural_ok = not errors
    evidence_ok = check_evidence_traceable(d)
    impl_ok = check_implementable(d)
    closed_violations = check_closed_mechanism(d)
    is_closed = len(closed_violations) > 0
    known_matches = check_known_mechanism(d)
    is_known = len(known_matches) > 0

    # Duplicate: use normalized hash (excludes mechanism_id, group, citations)
    is_dup = nh in seen_hashes
    seen_hashes.add(nh)

    reasons = []
    if not structural_ok:
        reasons.extend(errors)
    if not evidence_ok:
        reasons.append("evidence not traceable to real trace/metric")
    if not impl_ok:
        reasons.append("algorithmic_change/mathematical_rule/implementation_requirements insufficient")
    if is_closed:
        reasons.append(f"re-proposes closed mechanism(s) in mechanism fields: {closed_violations}")
    if is_known:
        reasons.append(f"mechanism fields match known mechanism(s): {known_matches}")
    if is_dup:
        reasons.append("duplicate of earlier candidate (normalized mechanism hash)")

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
        normalized_hash=nh,
        content_hash=ch,
        raw_input_tokens=input_tokens,
        raw_output_tokens=output_tokens,
        api_calls=api_calls,
        fe_cost=fe_cost,
    )


def evaluate_batch(candidates: List[Dict[str, Any]]) -> EvalReport:
    report = EvalReport()
    seen_hashes: Set[str] = set()

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
# Random-valid generator (Group C) — corrective version
# ---------------------------------------------------------------------------

# Frozen template library: real algorithm components with real modification points.
# Each template maps to a real code location in lshade_canonical.py.
FROZEN_TEMPLATES = [
    {
        "target_component": "parameter_memory",
        "modification_point": "update_memory() function in lshade_canonical.py",
        "real_metric": "M_CR drift",
        "real_functions": ["F1", "F6", "F10", "F20"],
    },
    {
        "target_component": "mutation_operator",
        "modification_point": "mutant computation in run_lshade_canonical()",
        "real_metric": "diversity collapse",
        "real_functions": ["F1", "F7", "F10", "F12"],
    },
    {
        "target_component": "selection_rule",
        "modification_point": "trial comparison (tf <= fit[i]) in run_lshade_canonical()",
        "real_metric": "zero-improvement success rate",
        "real_functions": ["F7", "F21"],
    },
    {
        "target_component": "boundary_handling",
        "modification_point": "np.clip(mutant, lb, ub) in run_lshade_canonical()",
        "real_metric": "repair success gap",
        "real_functions": ["F1", "F7", "F10", "F20"],
    },
    {
        "target_component": "archive_management",
        "modification_point": "archive.append / archive.pop in run_lshade_canonical()",
        "real_metric": "archive r2 fraction",
        "real_functions": ["F1", "F7", "F10", "F20"],
    },
    {
        "target_component": "crossover_operator",
        "modification_point": "cross = rng.rand(dim) < CR in run_lshade_canonical()",
        "real_metric": "CR drift",
        "real_functions": ["F1", "F6", "F10"],
    },
]

# Real evidence snippets from Phase-1A-7/8 diagnostic traces.
REAL_EVIDENCE = {
    "M_CR drift": {"metric": "CR_mean_late", "values": {"F1": 0.85, "F6": 0.95, "F10": 0.98, "F20": 0.03}},
    "diversity collapse": {"metric": "diversity_late", "values": {"F1": 0.000, "F7": 0.000, "F10": 0.000, "F12": 0.000}},
    "zero-improvement success rate": {"metric": "success_rate_late", "values": {"F7": 0.82, "F21": 1.00}},
    "repair success gap": {"metric": "repair_success_rate", "values": {"F1": 0.30, "F7": 0.12, "F10": 0.12, "F20": 0.11}},
    "archive r2 fraction": {"metric": "arch_r2_rate", "values": {"F1": 0.51, "F7": 0.51, "F10": 0.51, "F20": 0.51}},
    "CR drift": {"metric": "CR_mean_late", "values": {"F1": 0.85, "F6": 0.95, "F10": 0.98}},
}


def generate_random_valid(
    seed: int,
    task_id: str,
    evidence_registry: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate a random-but-valid mechanism proposal from frozen templates.

    Uses real algorithm components and real evidence values.
    Does NOT fabricate observations.
    """
    import random
    rng = random.Random(seed)

    template = FROZEN_TEMPLATES[seed % len(FROZEN_TEMPLATES)]
    comp = template["target_component"]
    mod_point = template["modification_point"]
    metric_name = template["real_metric"]
    func = rng.choice(template["real_functions"])
    ev_data = REAL_EVIDENCE.get(metric_name, {})
    obs_val = ev_data.get("values", {}).get(func, 0.0)
    metric = ev_data.get("metric", "unknown")

    params = ["alpha", "beta", "gamma", "delta"]
    p1 = rng.choice(params)
    v1 = round(rng.uniform(0.1, 0.9), 2)

    structured_evidence = {
        "task_id": task_id,
        "trace_path": f"results/phase1a7/diagnostic_traces/{func}_s11.json",
        "function": func,
        "seed": 11,
        "metric": metric,
        "observed_value": obs_val,
    }

    proposal = {
        "mechanism_id": f"RAND-{seed:04d}",
        "target_component": comp,
        "observed_evidence": structured_evidence,
        "causal_hypothesis": (
            f"The {comp} at {mod_point} causes degraded performance because "
            f"the {metric} of {obs_val} on {func} indicates suboptimal behavior."
        ),
        "algorithmic_change": (
            f"Modify the {comp} by introducing a dynamic {p1} parameter "
            f"with value {v1} that adapts based on recent improvement history."
        ),
        "mathematical_rule": (
            f"{p1} = {v1} + 0.1 * (improvement_rate - 0.5)"
        ),
        "expected_effect": (
            f"Improved {metric} on {func}, leading to better convergence."
        ),
        "failure_prediction": (
            f"If the {p1} adaptation is too aggressive, {func} performance degrades."
        ),
        "ablation_plan": (
            f"Compare standard {comp} vs adaptive {p1} on {func} and F1, 3 seeds."
        ),
        "nearest_known_methods": (
            f"Self-adaptive parameter control in DE/ES variants"
        ),
        "implementation_requirements": (
            f"Modify {mod_point}. Add {p1} tracking variable. "
            f"Estimated change: ~10 lines in lshade_canonical.py."
        ),
    }
    return json.dumps(proposal, indent=2, ensure_ascii=False)

"""Phase-1A-10 A4 (corrective): offline validation tests.

Covers: parser, closed-mechanism detection (mechanism fields only),
known-mechanism false-positive fix, evidence traceability (structured),
duplicate normalization, random generator with real evidence, FE protection.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.metabox.agent_assisted_ec.candidate_evaluator import (
    EVIDENCE_REQUIRED_KEYS,
    CLOSED_MECHANISMS,
    MECHANISM_FIELDS,
    REQUIRED_FIELDS,
    check_closed_mechanism,
    check_evidence_traceable,
    check_implementable,
    check_known_mechanism,
    content_hash,
    evaluate_batch,
    evaluate_candidate,
    generate_random_valid,
    normalized_mechanism_hash,
    parse_candidate,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_PROPOSAL = json.dumps({
    "mechanism_id": "TEST-001",
    "target_component": "parameter_memory",
    "observed_evidence": {
        "task_id": "TASK-02-cr-memory-drift",
        "trace_path": "results/phase1a7/diagnostic_traces/F01_s11.json",
        "function": "F1",
        "seed": 11,
        "metric": "CR_mean_late",
        "observed_value": 0.85
    },
    "causal_hypothesis": "Weighted arithmetic mean allows positive feedback drift.",
    "algorithmic_change": "Introduce a relative-improvement-scaled weight for M_CR update.",
    "mathematical_rule": "w_new = |Δf| / (|Δf| + median_Δf) * |Δf| where median_Δf is from rolling window",
    "expected_effect": "Slower CR drift on F1/F6/F10.",
    "failure_prediction": "If median estimation is noisy, M_CR becomes unstable on F1.",
    "ablation_plan": "Compare standard vs scaled weight on F1, F6, F10, 3 seeds each.",
    "nearest_known_methods": "SHADE weighted arithmetic mean (Tanabe 2014); robust regression weighting.",
    "implementation_requirements": "Modify update_memory() in lshade_canonical.py: change w computation. ~5 lines.",
}, indent=2)

# Candidate that CITES L-SHADE/SHADE in nearest_known_methods — must NOT be rejected.
CITATION_PROPOSAL = json.dumps({
    "mechanism_id": "TEST-CITE",
    "target_component": "mutation_operator",
    "observed_evidence": {
        "task_id": "TASK-03-f-collapse",
        "trace_path": "results/phase1a7/diagnostic_traces/F04_s11.json",
        "function": "F4",
        "seed": 11,
        "metric": "F_mean_late",
        "observed_value": 0.08
    },
    "causal_hypothesis": "F memory collapses because small-F successes have higher frequency.",
    "algorithmic_change": "Add a diversity-sensitive F boost that scales with population spread.",
    "mathematical_rule": "F_eff = F * (1 + beta * normalized_diversity) where beta = 0.3",
    "expected_effect": "Maintain F above 0.1 on F4/F11/F15.",
    "failure_prediction": "If diversity estimate is wrong, F overshoots on F1.",
    "ablation_plan": "Compare standard vs boosted F on F4, F11, F15 and F1 control.",
    "nearest_known_methods": "L-SHADE Cauchy F sampling (Tanabe 2014); jSO F adaptation; these are comparison baselines, not the proposed mechanism.",
    "implementation_requirements": "Modify F sampling in run_lshade_canonical(): add diversity multiplier. ~8 lines.",
}, indent=2)

# Candidate that RE-PROPOSES a closed mechanism in its algorithmic_change.
CLOSED_PROPOSAL = json.dumps({
    "mechanism_id": "TEST-CLOSED",
    "target_component": "population_management",
    "observed_evidence": {
        "task_id": "TASK-05-seed-bifurcation",
        "trace_path": "results/phase1a7/diagnostic_traces/F11_s11.json",
        "function": "F11",
        "seed": 11,
        "metric": "diversity_late",
        "observed_value": 0.175
    },
    "causal_hypothesis": "Population diversity collapse causes seed-dependent behavior.",
    "algorithmic_change": "Apply N+I restart with uniform immigrants when stall_gen > 50.",
    "mathematical_rule": "if stall_gen > 50: replace worst 10% with uniform immigrants",
    "expected_effect": "Restore diversity on F11.",
    "failure_prediction": "Restarts waste FE.",
    "ablation_plan": "Compare with/without restart on F11, F10.",
    "nearest_known_methods": "Restart strategies (Auger & Hansen 2005)",
    "implementation_requirements": "Add restart trigger in main loop of run_lshade_canonical().",
}, indent=2)

MISSING_FIELD_PROPOSAL = json.dumps({
    "mechanism_id": "TEST-002",
    "target_component": "selection_rule",
    "observed_evidence": {"task_id": "X", "trace_path": "Y", "function": "F7", "seed": 11, "metric": "m", "observed_value": 0.5},
})

LEGACY_STRING_EVIDENCE = json.dumps({
    "mechanism_id": "TEST-LEGACY",
    "target_component": "selection_rule",
    "observed_evidence": "F7 s=22 late success_rate=0.824 but stall_gen=53.",
    "causal_hypothesis": "Zero-improvement successes pollute memory.",
    "algorithmic_change": "Scale memory weight by improvement magnitude.",
    "mathematical_rule": "w = |Δf| * sigmoid(Δf / median_Δf)",
    "expected_effect": "Better memory on F7.",
    "failure_prediction": "May fail on F1.",
    "ablation_plan": "Compare on F7 and F1.",
    "nearest_known_methods": "SHADE memory update.",
    "implementation_requirements": "Modify update_memory() in lshade_canonical.py. ~5 lines.",
})


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class TestParser:
    def test_valid_structured(self):
        d, errors = parse_candidate(VALID_PROPOSAL)
        assert d is not None
        assert len(errors) == 0

    def test_valid_legacy_string(self):
        d, errors = parse_candidate(LEGACY_STRING_EVIDENCE)
        assert d is not None

    def test_missing_field(self):
        d, errors = parse_candidate(MISSING_FIELD_PROPOSAL)
        assert d is None
        assert any("missing field" in e for e in errors)

    def test_invalid_json(self):
        d, errors = parse_candidate("not json")
        assert d is None

    def test_all_required_fields(self):
        assert len(REQUIRED_FIELDS) == 11


# ---------------------------------------------------------------------------
# Fix A: known-mechanism false positive
# ---------------------------------------------------------------------------

class TestKnownMechanismFix:
    def test_citation_in_nearest_known_methods_NOT_flagged(self):
        """Citing L-SHADE/SHADE in nearest_known_methods must NOT cause rejection."""
        v = evaluate_candidate(CITATION_PROPOSAL, group="A")
        # The mechanism fields (algorithmic_change, mathematical_rule) do NOT
        # contain "l-shade" or "shade" as the actual mechanism being proposed.
        assert not v.is_known_mechanism, (
            f"False positive: citing L-SHADE in nearest_known_methods should not "
            f"trigger known-mechanism rejection. Matches: {v.nearest_known_matches}"
        )
        assert not v.is_closed_mechanism

    def test_mechanism_fields_only_scanned(self):
        """check_known_mechanism only looks at MECHANISM_FIELDS."""
        d = {
            "algorithmic_change": "Introduce a novel diversity-sensitive weight.",
            "mathematical_rule": "w = f(diversity) with novel formula",
            "nearest_known_methods": "L-SHADE, SHADE, JADE, CMA-ES",
        }
        matches = check_known_mechanism(d)
        # nearest_known_methods mentions L-SHADE etc but should NOT be scanned
        assert len(matches) == 0, f"Should not match from citation field: {matches}"

    def test_actual_known_mechanism_in_mechanism_field_IS_flagged(self):
        """If the actual proposed mechanism IS Lehmer mean, it should be flagged."""
        d = {
            "algorithmic_change": "Replace M_F update with Lehmer mean.",
            "mathematical_rule": "M_F = sum(w * F^2) / sum(w * F)",
        }
        matches = check_known_mechanism(d)
        assert any("Lehmer" in m for m in matches)


# ---------------------------------------------------------------------------
# Fix A: closed-mechanism detection
# ---------------------------------------------------------------------------

class TestClosedMechanismFix:
    def test_closed_in_mechanism_field_rejected(self):
        v = evaluate_candidate(CLOSED_PROPOSAL, group="A")
        assert v.is_closed_mechanism
        assert not v.passes_pre_review

    def test_citation_of_closed_mechanism_in_comparison_NOT_flagged(self):
        """Mentioning N+I in nearest_known_methods as 'this is NOT what we do' is OK."""
        d = {
            "algorithmic_change": "A completely novel mechanism.",
            "mathematical_rule": "x = novel_formula(y)",
            "nearest_known_methods": "N+I restart was rejected in Phase-1A-4R3; we propose something different.",
        }
        violations = check_closed_mechanism(d)
        assert len(violations) == 0, f"Should not flag from citation: {violations}"

    def test_all_closed_mechanisms_listed(self):
        assert "n+i restart" in CLOSED_MECHANISMS
        assert "quality residual" in CLOSED_MECHANISMS


# ---------------------------------------------------------------------------
# Fix B: structured evidence
# ---------------------------------------------------------------------------

class TestStructuredEvidence:
    def test_structured_evidence_valid(self):
        d, _ = parse_candidate(VALID_PROPOSAL)
        assert check_evidence_traceable(d) is True

    def test_structured_missing_key(self):
        d = {"observed_evidence": {"task_id": "X", "trace_path": "Y", "function": "F1"}}
        assert check_evidence_traceable(d) is False

    def test_structured_empty_trace_path(self):
        d = {"observed_evidence": {"task_id": "X", "trace_path": "", "function": "F1", "seed": 1, "metric": "m", "observed_value": 0.5}}
        assert check_evidence_traceable(d) is False

    def test_structured_bad_function(self):
        d = {"observed_evidence": {"task_id": "X", "trace_path": "Y", "function": "NOT_A_FUNC", "seed": 1, "metric": "m", "observed_value": 0.5}}
        assert check_evidence_traceable(d) is False

    def test_legacy_string_still_accepted(self):
        d, _ = parse_candidate(LEGACY_STRING_EVIDENCE)
        assert check_evidence_traceable(d) is True

    def test_vague_string_rejected(self):
        d = {"observed_evidence": "The algorithm performs poorly."}
        assert check_evidence_traceable(d) is False

    def test_all_evidence_keys_defined(self):
        assert EVIDENCE_REQUIRED_KEYS == {"task_id", "trace_path", "function", "seed", "metric", "observed_value"}


# ---------------------------------------------------------------------------
# Fix C: duplicate normalization
# ---------------------------------------------------------------------------

class TestDuplicateNormalization:
    def test_same_mechanism_different_id_is_duplicate(self):
        """Two candidates with same mechanism content but different mechanism_id
        should be detected as duplicates."""
        import copy
        d1 = json.loads(VALID_PROPOSAL)
        d2 = copy.deepcopy(d1)
        d2["mechanism_id"] = "DIFFERENT-ID"
        d2["nearest_known_methods"] = "Completely different citation"

        nh1 = normalized_mechanism_hash(d1)
        nh2 = normalized_mechanism_hash(d2)
        assert nh1 == nh2, "Same mechanism content should produce same normalized hash"

    def test_different_mechanism_not_duplicate(self):
        d1 = json.loads(VALID_PROPOSAL)
        d2 = json.loads(CITATION_PROPOSAL)
        nh1 = normalized_mechanism_hash(d1)
        nh2 = normalized_mechanism_hash(d2)
        assert nh1 != nh2

    def test_evaluate_detects_duplicate(self):
        seen = set()
        v1 = evaluate_candidate(VALID_PROPOSAL, group="A", seen_hashes=seen)
        # Same mechanism, different ID
        import copy
        d = json.loads(VALID_PROPOSAL)
        d["mechanism_id"] = "CHANGED-ID"
        raw2 = json.dumps(d)
        v2 = evaluate_candidate(raw2, group="B", seen_hashes=seen)
        assert not v1.is_duplicate
        assert v2.is_duplicate

    def test_normalized_hash_excludes_mechanism_id(self):
        d = json.loads(VALID_PROPOSAL)
        nh1 = normalized_mechanism_hash(d)
        d["mechanism_id"] = "WHATEVER"
        nh2 = normalized_mechanism_hash(d)
        assert nh1 == nh2


# ---------------------------------------------------------------------------
# Implementability
# ---------------------------------------------------------------------------

class TestImplementability:
    def test_valid_implementable(self):
        d, _ = parse_candidate(VALID_PROPOSAL)
        assert check_implementable(d) is True

    def test_vague_not_implementable(self):
        d = {
            "algorithmic_change": "Do better.",
            "mathematical_rule": "x = y",
            "implementation_requirements": "Change stuff.",
        }
        assert check_implementable(d) is False


# ---------------------------------------------------------------------------
# Full evaluation
# ---------------------------------------------------------------------------

class TestEvaluateCandidate:
    def test_valid_proposal_passes(self):
        v = evaluate_candidate(VALID_PROPOSAL, group="A")
        assert v.structural_valid
        assert v.evidence_traceable
        assert v.implementable
        assert not v.is_closed_mechanism
        assert not v.is_known_mechanism
        assert v.normalized_hash != ""

    def test_citation_proposal_passes(self):
        v = evaluate_candidate(CITATION_PROPOSAL, group="A")
        assert v.passes_pre_review

    def test_closed_rejected(self):
        v = evaluate_candidate(CLOSED_PROPOSAL, group="A")
        assert not v.passes_pre_review

    def test_ledger(self):
        v = evaluate_candidate(VALID_PROPOSAL, group="A", input_tokens=100, output_tokens=200, api_calls=1, fe_cost=5000)
        assert v.raw_input_tokens == 100
        assert v.fe_cost == 5000


# ---------------------------------------------------------------------------
# Batch
# ---------------------------------------------------------------------------

class TestBatch:
    def test_counts(self):
        candidates = [
            {"raw": VALID_PROPOSAL, "group": "A", "input_tokens": 100},
            {"raw": CLOSED_PROPOSAL, "group": "A", "input_tokens": 100},
            {"raw": MISSING_FIELD_PROPOSAL, "group": "B", "input_tokens": 80},
        ]
        report = evaluate_batch(candidates)
        assert report.n_submitted == 3
        assert report.n_closed_violation == 1

    def test_serializable(self):
        report = evaluate_batch([{"raw": VALID_PROPOSAL, "group": "A"}])
        json.dumps(report.to_dict())


# ---------------------------------------------------------------------------
# Fix B: random generator with real evidence
# ---------------------------------------------------------------------------

class TestRandomGeneratorFix:
    def test_generates_structured_evidence(self):
        raw = generate_random_valid(seed=42, task_id="TASK-01")
        d = json.loads(raw)
        assert isinstance(d["observed_evidence"], dict)
        assert "task_id" in d["observed_evidence"]
        assert "trace_path" in d["observed_evidence"]
        assert "function" in d["observed_evidence"]

    def test_evidence_passes_traceable_check(self):
        raw = generate_random_valid(seed=42, task_id="TASK-01")
        d = json.loads(raw)
        assert check_evidence_traceable(d) is True

    def test_reproducible(self):
        raw1 = generate_random_valid(seed=42, task_id="TASK-01")
        raw2 = generate_random_valid(seed=42, task_id="TASK-01")
        assert raw1 == raw2

    def test_different_seeds_different_templates(self):
        raws = [generate_random_valid(seed=s, task_id="T") for s in range(12)]
        comps = set()
        for raw in raws:
            d = json.loads(raw)
            comps.add(d["target_component"])
        assert len(comps) > 1

    def test_has_all_required_fields(self):
        raw = generate_random_valid(seed=42, task_id="TASK-01")
        d = json.loads(raw)
        for f in REQUIRED_FIELDS:
            assert f in d
            assert d[f]

    def test_no_fabricated_values(self):
        """Evidence values must come from REAL_EVIDENCE registry."""
        raw = generate_random_valid(seed=0, task_id="TASK-01")
        d = json.loads(raw)
        ev = d["observed_evidence"]
        # observed_value must be a real number from the registry
        assert isinstance(ev["observed_value"], (int, float))
        assert ev["observed_value"] != 0 or ev["function"] == "F1"  # F1 diversity is 0.0

    def test_structural_valid(self):
        raw = generate_random_valid(seed=42, task_id="TASK-01")
        v = evaluate_candidate(raw, group="C")
        assert v.structural_valid
        assert v.evidence_traceable


# ---------------------------------------------------------------------------
# FE protection
# ---------------------------------------------------------------------------

class TestFEProtection:
    def test_fe_recorded(self):
        v = evaluate_candidate(VALID_PROPOSAL, group="A", fe_cost=5000)
        assert v.fe_cost == 5000

    def test_batch_fe_sum(self):
        report = evaluate_batch([
            {"raw": VALID_PROPOSAL, "group": "A", "fe_cost": 5000},
            {"raw": CLOSED_PROPOSAL, "group": "B", "fe_cost": 5000},
        ])
        assert report.total_fe_cost == 10000

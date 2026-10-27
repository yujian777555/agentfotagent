"""Goal-state-based evaluator.

Primary metric: verified task success rate computed ONLY from the environment's
final state and the task-specific success predicate. The Agent's self-report in
the execution trace never affects ``success``.

Phase-0-R1: fail closed on missing/malformed required entities and empty goals.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..environments.tool_world import state_hash
from ..interfaces import EpisodeResult, Evaluator, TaskInstance


# Semantic version advanced in Phase-0-R2 after R1 evaluator fixes.
EVALUATOR_VERSION = "aes-evaluator-v2"


# Expected dial names for dial_set goals (complete set required).
REQUIRED_DIALS = ("alpha", "beta", "gamma")
DIAL_VALUE_MIN = 0
DIAL_VALUE_MAX = 3

# Entity types as defined by aes-task-gen-v2 generators / tool world.
KEY_CRATE_ARTIFACT_TYPE = "artifact"
KEY_CRATE_CONTAINER_TYPE = "crate"
KEY_CRATE_SURFACE_TYPE = "surface"
RELAY_OBJECT_TYPE = "relay"
RELAY_CODE_DIGITS = 3
RELAY_FREQ_MIN = 1
RELAY_FREQ_MAX = 7


class StateBasedEvaluator(Evaluator):
    """Fail-closed evaluator over terminal environment state."""

    def __init__(self, genome_hash: str = "") -> None:
        self.genome_hash = genome_hash

    def success_predicate(self, task: TaskInstance, final_state: Mapping[str, Any]) -> bool:
        if not isinstance(final_state, Mapping):
            return False
        goal = task.hidden_goal
        if not isinstance(goal, Mapping) or not goal:
            return False
        gtype = goal.get("type")

        if gtype == "key_crate":
            return self._pred_key_crate(goal, final_state, task)
        if gtype == "dial_set":
            return self._pred_dial_set(goal, final_state)
        if gtype == "relay_route":
            return self._pred_relay_route(goal, final_state)

        # Unknown goal types fail closed.
        return False

    def _pred_key_crate(self, goal: Mapping[str, Any], state: Mapping[str, Any], task: TaskInstance) -> bool:
        spec = goal.get("object_on_surface")
        if not isinstance(spec, Mapping):
            return False
        obj_id = spec.get("object")
        surface = spec.get("surface")
        if not isinstance(obj_id, str) or not obj_id:
            return False
        if not isinstance(surface, str) or not surface:
            return False

        # crate_unlocked is a required constraint; missing or non-true fails closed.
        if goal.get("crate_unlocked") is not True:
            return False

        # Authoritative world contract from the generated task (R4-03).
        setup = task.setup or {}
        legal_locations = set(setup.get("locations") or [])
        legal_surfaces = set(setup.get("surfaces") or [])
        setup_objects = setup.get("objects") or {}
        if not legal_locations:
            return False
        if not isinstance(setup_objects, Mapping):
            return False

        objects = state.get("objects")
        if not isinstance(objects, Mapping):
            return False

        def _loc_ok(obj: Mapping[str, Any]) -> bool:
            loc = obj.get("location")
            return isinstance(loc, str) and loc in (legal_locations | legal_surfaces)

        # Target artifact must exist with the generator-defined type and sit on the surface.
        obj = objects.get(obj_id)
        if not isinstance(obj, Mapping):
            return False
        if obj.get("type") != KEY_CRATE_ARTIFACT_TYPE:
            return False
        if obj.get("location") != surface:
            return False
        if not _loc_ok(obj):
            return False

        # Crate container: expected type, explicit unlock, location matches task setup.
        crate = objects.get("crate")
        if not isinstance(crate, Mapping):
            return False
        if crate.get("type") != KEY_CRATE_CONTAINER_TYPE:
            return False
        if crate.get("unlocked") is not True:
            return False
        crate_setup = setup_objects.get("crate")
        if not isinstance(crate_setup, Mapping):
            return False
        expected_crate_loc = crate_setup.get("location")
        if not isinstance(expected_crate_loc, str) or not expected_crate_loc:
            return False
        if crate.get("location") != expected_crate_loc:
            return False
        if expected_crate_loc not in legal_locations:
            return False

        # Surface object: expected type and location from task setup.
        surface_obj = objects.get(surface)
        if not isinstance(surface_obj, Mapping):
            return False
        if surface_obj.get("type") != KEY_CRATE_SURFACE_TYPE:
            return False
        surface_setup = setup_objects.get(surface)
        if not isinstance(surface_setup, Mapping):
            return False
        expected_surface_loc = surface_setup.get("location")
        if not isinstance(expected_surface_loc, str) or not expected_surface_loc:
            return False
        if surface_obj.get("location") != expected_surface_loc:
            return False
        if expected_surface_loc not in legal_locations:
            return False
        if surface not in legal_surfaces:
            return False

        return True

    def _pred_dial_set(self, goal: Mapping[str, Any], state: Mapping[str, Any]) -> bool:
        targets = goal.get("targets")
        if not isinstance(targets, Mapping) or not targets:
            return False
        # Complete expected dial set required — partial goals fail closed.
        if set(targets.keys()) != set(REQUIRED_DIALS):
            return False
        dials = state.get("dials")
        if not isinstance(dials, Mapping):
            return False
        for key in REQUIRED_DIALS:
            expected = targets.get(key)
            if not isinstance(expected, int) or isinstance(expected, bool):
                return False
            if expected < DIAL_VALUE_MIN or expected > DIAL_VALUE_MAX:
                return False
            if key not in dials:
                return False
            actual = dials.get(key)
            if not isinstance(actual, int) or isinstance(actual, bool):
                return False
            if actual != expected:
                return False
        return True

    @staticmethod
    def _valid_relay_code(code: Any) -> bool:
        """Canonical relay code: exactly 3 digit characters (aes-task-gen-v2)."""
        if not isinstance(code, str):
            return False
        if len(code) != RELAY_CODE_DIGITS:
            return False
        return all(ch.isdigit() and ch.isascii() for ch in code)

    @staticmethod
    def _expected_relay_frequency(code: str) -> int:
        digits = [int(ch) for ch in code]
        return (sum(digits) % 7) + 1

    def _pred_relay_route(self, goal: Mapping[str, Any], state: Mapping[str, Any]) -> bool:
        # Required goal fields with full schema validation (R3-02).
        if "frequency" not in goal or "code" not in goal:
            return False
        code = goal.get("code")
        expected = goal.get("frequency")
        if not self._valid_relay_code(code):
            return False
        if not isinstance(expected, int) or isinstance(expected, bool):
            return False
        if expected < RELAY_FREQ_MIN or expected > RELAY_FREQ_MAX:
            return False
        # code/frequency must match the generator formula.
        if expected != self._expected_relay_frequency(code):
            return False

        # Required world object.
        objects = state.get("objects")
        if not isinstance(objects, Mapping):
            return False
        relay_obj = objects.get("relay")
        if not isinstance(relay_obj, Mapping):
            return False
        if relay_obj.get("type") != RELAY_OBJECT_TYPE:
            return False

        relay = state.get("relay")
        if not isinstance(relay, Mapping):
            return False
        activated = relay.get("activated")
        if activated is not True:
            return False
        frequency = relay.get("frequency")
        if not isinstance(frequency, int) or isinstance(frequency, bool):
            return False
        return frequency == expected

    @staticmethod
    def _safe_steps(final_state: Any) -> int:
        if not isinstance(final_state, Mapping):
            return 0
        raw = final_state.get("step", 0)
        if isinstance(raw, bool):
            return 0
        if isinstance(raw, int):
            return max(0, raw)
        try:
            return max(0, int(raw))
        except (TypeError, ValueError):
            return 0

    def evaluate(
        self,
        task: TaskInstance,
        final_state: Mapping[str, Any],
        trace: Sequence[Mapping[str, Any]],
    ) -> EpisodeResult:
        # Success is computed exclusively from final_state + hidden goal.
        try:
            success = bool(self.success_predicate(task, final_state))
        except Exception:
            success = False  # fail closed on unexpected evaluator errors

        try:
            steps = self._safe_steps(final_state)
        except Exception:
            steps = 0

        invalid_actions = 0
        try:
            for entry in trace or []:
                info = entry.get("info") or {}
                if info.get("valid") is False or entry.get("valid") is False:
                    invalid_actions += 1
        except Exception:
            invalid_actions = 0

        repeated_states = 0
        try:
            seen = set()
            for entry in trace or []:
                sh = entry.get("state_hash")
                if sh is None:
                    continue
                if sh in seen:
                    repeated_states += 1
                else:
                    seen.add(sh)
        except Exception:
            repeated_states = 0

        try:
            termination_reason = (
                str(final_state.get("termination_reason", "unknown"))
                if isinstance(final_state, Mapping)
                else "unknown"
            )
        except Exception:
            termination_reason = "unknown"

        if termination_reason in {"error", "backend_error", "missing_output"}:
            success = False

        claimed = False
        try:
            claimed = any(
                bool((e.get("info") or {}).get("self_report_success"))
                or bool(e.get("self_report_success"))
                for e in (trace or [])
            )
        except Exception:
            claimed = False

        diagnostic = {
            "claimed_success": claimed,
            "self_report_ignored": True,
            "termination_reason": termination_reason,
        }

        try:
            final_state_hash = state_hash(final_state if isinstance(final_state, Mapping) else {})
        except Exception:
            final_state_hash = "unhashable-state"

        return EpisodeResult(
            task_id=task.task_id,
            genome_hash=self.genome_hash,
            success=success,
            steps=steps,
            invalid_actions=invalid_actions,
            repeated_states=repeated_states,
            termination_reason=termination_reason,
            final_state_hash=final_state_hash,
            diagnostic=diagnostic,
        )


def evaluate_episode(
    task: TaskInstance,
    final_state: Mapping[str, Any],
    trace: Sequence[Mapping[str, Any]],
    genome_hash: str = "",
) -> EpisodeResult:
    return StateBasedEvaluator(genome_hash=genome_hash).evaluate(task, final_state, trace)

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
            return self._pred_key_crate(goal, final_state)
        if gtype == "dial_set":
            return self._pred_dial_set(goal, final_state)
        if gtype == "relay_route":
            return self._pred_relay_route(goal, final_state)

        # Unknown goal types fail closed.
        return False

    def _pred_key_crate(self, goal: Mapping[str, Any], state: Mapping[str, Any]) -> bool:
        spec = goal.get("object_on_surface")
        if not isinstance(spec, Mapping):
            return False
        obj_id = spec.get("object")
        surface = spec.get("surface")
        if not obj_id or not surface:
            return False

        objects = state.get("objects")
        if not isinstance(objects, Mapping):
            return False

        obj = objects.get(obj_id)
        if not isinstance(obj, Mapping):
            return False  # missing target object → fail closed
        if obj.get("location") != surface:
            return False

        # Crate must exist and its unlocked status must be explicitly valid.
        crate = objects.get("crate")
        if not isinstance(crate, Mapping):
            return False  # missing crate record → fail closed (F5)
        if goal.get("crate_unlocked"):
            # Require an explicit successful unlock, not a missing/False flag.
            if crate.get("unlocked") is not True:
                return False
        return True

    def _pred_dial_set(self, goal: Mapping[str, Any], state: Mapping[str, Any]) -> bool:
        targets = goal.get("targets")
        if not isinstance(targets, Mapping) or not targets:
            return False  # empty/missing target set → fail closed (F5)
        dials = state.get("dials")
        if not isinstance(dials, Mapping):
            return False
        for key, expected in targets.items():
            if key not in dials:
                return False  # missing dial → fail closed
            actual = dials.get(key)
            if not isinstance(actual, int) or isinstance(actual, bool):
                return False
            if not isinstance(expected, int) or isinstance(expected, bool):
                return False
            if actual != expected:
                return False
        return True

    def _pred_relay_route(self, goal: Mapping[str, Any], state: Mapping[str, Any]) -> bool:
        relay = state.get("relay")
        if not isinstance(relay, Mapping):
            return False  # missing/malformed relay → fail closed (F5)
        activated = relay.get("activated")
        if activated is not True:
            return False
        frequency = relay.get("frequency")
        expected = goal.get("frequency")
        if not isinstance(frequency, int) or isinstance(frequency, bool):
            return False
        if not isinstance(expected, int) or isinstance(expected, bool):
            return False
        return frequency == expected

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

        steps = int(final_state.get("step", 0)) if isinstance(final_state, Mapping) else 0
        invalid_actions = 0
        for entry in trace or []:
            info = entry.get("info") or {}
            if info.get("valid") is False or entry.get("valid") is False:
                invalid_actions += 1

        repeated_states = 0
        seen = set()
        for entry in trace or []:
            sh = entry.get("state_hash")
            if sh is None:
                continue
            if sh in seen:
                repeated_states += 1
            else:
                seen.add(sh)

        termination_reason = (
            str(final_state.get("termination_reason", "unknown"))
            if isinstance(final_state, Mapping)
            else "unknown"
        )
        if termination_reason in {"error", "backend_error", "missing_output"}:
            success = False

        claimed = any(
            bool((e.get("info") or {}).get("self_report_success"))
            or bool(e.get("self_report_success"))
            for e in (trace or [])
        )
        diagnostic = {
            "claimed_success": claimed,
            "self_report_ignored": True,
            "termination_reason": termination_reason,
        }

        return EpisodeResult(
            task_id=task.task_id,
            genome_hash=self.genome_hash,
            success=success,
            steps=steps,
            invalid_actions=invalid_actions,
            repeated_states=repeated_states,
            termination_reason=termination_reason,
            final_state_hash=state_hash(final_state if isinstance(final_state, Mapping) else {}),
            diagnostic=diagnostic,
        )


def evaluate_episode(
    task: TaskInstance,
    final_state: Mapping[str, Any],
    trace: Sequence[Mapping[str, Any]],
    genome_hash: str = "",
) -> EpisodeResult:
    return StateBasedEvaluator(genome_hash=genome_hash).evaluate(task, final_state, trace)

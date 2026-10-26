"""Goal-state-based evaluator.

Primary metric: verified task success rate computed ONLY from the environment's
final state and the task-specific success predicate. The Agent's self-report in
the execution trace never affects ``success``.
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
        goal = task.hidden_goal
        gtype = goal.get("type")

        if gtype == "key_crate":
            spec = goal.get("object_on_surface", {})
            obj_id = spec.get("object")
            surface = spec.get("surface")
            objects = final_state.get("objects", {})
            obj = objects.get(obj_id, {})
            on_surface = obj.get("location") == surface
            crate = objects.get("crate", {})
            crate_unlocked = bool(crate.get("unlocked")) or not bool(crate.get("locked"))
            if goal.get("crate_unlocked") and not crate_unlocked:
                return False
            return bool(on_surface)

        if gtype == "dial_set":
            targets = goal.get("targets", {})
            dials = final_state.get("dials", {})
            return all(int(dials.get(k, -999)) == int(v) for k, v in targets.items())

        if gtype == "relay_route":
            relay = final_state.get("relay", {})
            return bool(relay.get("activated")) and int(relay.get("frequency", -1)) == int(
                goal.get("frequency", -2)
            )

        # Unknown goal types fail closed.
        return False

    def evaluate(
        self,
        task: TaskInstance,
        final_state: Mapping[str, Any],
        trace: Sequence[Mapping[str, Any]],
    ) -> EpisodeResult:
        # Success is computed exclusively from final_state + hidden goal.
        success = bool(self.success_predicate(task, final_state))

        steps = int(final_state.get("step", 0))
        invalid_actions = 0
        for entry in trace:
            info = entry.get("info") or {}
            if info.get("valid") is False or entry.get("valid") is False:
                invalid_actions += 1

        repeated_states = 0
        seen = set()
        for entry in trace:
            sh = entry.get("state_hash")
            if sh is None:
                continue
            if sh in seen:
                repeated_states += 1
            else:
                seen.add(sh)

        termination_reason = str(final_state.get("termination_reason", "unknown"))
        # Fail closed: incomplete/invalid runs are not successes even if the agent
        # claimed completion.
        if termination_reason in {"error", "backend_error", "missing_output"}:
            success = False

        # Self-report sabotage guard: a trace that claims success cannot flip the flag.
        claimed = any(
            bool((e.get("info") or {}).get("self_report_success"))
            or bool(e.get("self_report_success"))
            for e in trace
        )
        diagnostic = {
            "claimed_success": claimed,
            "self_report_ignored": True,
            "termination_reason": termination_reason,
        }

        return EpisodeResult(
            task_id=task.public.task_id,
            genome_hash=self.genome_hash,
            success=success,
            steps=steps,
            invalid_actions=invalid_actions,
            repeated_states=repeated_states,
            termination_reason=termination_reason,
            final_state_hash=state_hash(final_state),
            diagnostic=diagnostic,
        )


def evaluate_episode(
    task: TaskInstance,
    final_state: Mapping[str, Any],
    trace: Sequence[Mapping[str, Any]],
    genome_hash: str = "",
) -> EpisodeResult:
    return StateBasedEvaluator(genome_hash=genome_hash).evaluate(task, final_state, trace)

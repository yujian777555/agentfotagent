"""Deterministic mock backend for engineering tests ONLY.

This module is never Agent-capability evidence. It is a scripted policy whose
behavior is shaped by the compiled phenotype so that gene intervention tests can
observe real execution differences.

Declared gene semantics wired into decisions (Phase-0-R1):
- planning_mode=plan_first            → a stored plan is consumed to pick phases/actions;
                                        changing the plan changes the next action.
- memory_policy=bounded_episodic      → room/object search uses phenotype.recall().
- verification_policy=check_before_finalize → verify_state output is read; submit is
                                        blocked until public goal checks pass.
- tool_selection_policy=state_conditioned → ranking depends on live situation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from ..environments.tool_world import ToolWorld, state_hash
from ..evaluation.evaluator import StateBasedEvaluator
from ..evaluation.provenance import EpisodeTrace
from ..genome.schema import genome_hash
from ..interfaces import (
    Action,
    AgentBackend,
    Observation,
    RuntimeTask,
    StepResult,
    TaskInstance,
)
from .phenotype import FIXED_TOOL_RANK, Phenotype, compile_phenotype


ENGINEERING_ONLY = True
MOCK_BACKEND_ID = "mock-engineering-v1"

KEY_CRATE_ROOMS = ("hall", "storage", "corridor", "vault")
RELAY_ROOMS = ("hub", "north", "south", "east")

# Plan step vocabulary consumed by the policy when planning_mode=plan_first.
DEFAULT_PLANS = {
    "key_crate": ["find_key", "unlock_crate", "transport_statue", "finalize"],
    "dial_set": ["gather_info", "set_dials", "finalize"],
    "relay_route": ["gather_notes", "activate", "set_frequency", "finalize"],
}


class MockBackend(AgentBackend):
    """AgentBackend wrapper around MockPolicy. Engineering tests only."""

    backend_id = MOCK_BACKEND_ID

    def __init__(self, policy: "MockPolicy") -> None:
        self.policy = policy
        self.last_payload: Optional[Dict[str, Any]] = None

    def propose(self, observation: Observation, context: Mapping[str, Any]) -> Action:
        # Exact model-facing payload: observation + runtime context only.
        self.last_payload = {
            "observation": dict(observation.content),
            "context": dict(context),
        }
        return self.policy.next_action(observation.content)


@dataclass
class MockPolicy:
    phenotype: Phenotype
    runtime_task: RuntimeTask
    family: str  # engineering label; NOT part of the model-facing payload
    known_offsets: Dict[str, int] = field(default_factory=dict)
    known_gauges: Dict[str, int] = field(default_factory=dict)
    known_frags: Dict[str, str] = field(default_factory=dict)
    failed_keys: List[str] = field(default_factory=list)
    inspected_objects: List[str] = field(default_factory=list)
    room_cursor: int = 0
    last_action: Optional[Action] = None
    placed_statue: bool = False
    last_verify_summary: Optional[Dict[str, Any]] = None

    def next_action(self, observation: Mapping[str, Any]) -> Action:
        self.phenotype.remember(observation)

        if self.phenotype.should_plan_first():
            plan = DEFAULT_PLANS.get(self.family, ["solve", "finalize"])
            self.phenotype.set_plan(plan)
            self.last_action = Action(tool="make_plan", args={"steps": list(plan)})
            return self.last_action

        candidates = self._solver_candidates(observation)
        action = self._select(candidates)

        # verification_policy: read verify output before finalizing.
        if action.tool == "submit" and self.phenotype.should_verify_before_finalize():
            self.phenotype.reset_verification()
            action = Action(tool="verify_state", args={})

        self.last_action = action
        return action

    # -- selection by tool_selection_policy -------------------------------

    def _select(self, candidates: Sequence[Action]) -> Action:
        if len(candidates) == 1:
            return candidates[0]
        policy = self.phenotype.genome.tool_selection_policy
        if policy == "fixed_ranking":
            rank = list(FIXED_TOOL_RANK)
        else:
            rank = list(self.phenotype.rank_tools({}, situation=self._situation()))

        def key(a: Action) -> Tuple[int, str]:
            try:
                r = rank.index(a.tool)
            except ValueError:
                r = len(rank) + 1
            return (r, a.tool)

        return sorted(candidates, key=key)[0]

    def _situation(self) -> str:
        if self.family == "dial_set":
            return "dials_unsolved"
        if self.family == "relay_route":
            return "in_room_with_notes"
        return "default"

    # -- plan consumption --------------------------------------------------

    def _plan_phase(self) -> Optional[str]:
        return self.phenotype.current_plan_step()

    def _finish_phase_if(self, condition: bool) -> None:
        if condition and self.phenotype.plan:
            self.phenotype.advance_plan()

    # -- family solvers ---------------------------------------------------

    def _solver_candidates(self, obs: Mapping[str, Any]) -> List[Action]:
        if self.family == "key_crate":
            return self._key_crate_candidates(obs)
        if self.family == "dial_set":
            return self._dial_set_candidates(obs)
        return self._relay_candidates(obs)

    # key_crate ------------------------------------------------------------

    def _key_crate_candidates(self, obs: Mapping[str, Any]) -> List[Action]:
        loc = obs.get("location")
        inv = list(obs.get("inventory", []))
        visible = list(obs.get("visible_objects", []))
        phase = self._plan_phase()

        # Completion signals advance the plan based on observed world state.
        if self.placed_statue:
            if self.phenotype.plan:
                self.phenotype.set_plan_index(len(self.phenotype.plan) - 1)
            return [Action(tool="submit", args={})]
        if "statue" in visible and phase in {None, "find_key", "unlock_crate"}:
            self._finish_phase_if(phase == "find_key")
            self._finish_phase_if(phase == "unlock_crate")
        if "statue" in inv and phase in {None, "find_key", "unlock_crate", "transport_statue"}:
            # Holding the statue: transport phase.
            if phase == "find_key":
                self.phenotype.set_plan_index(2)  # transport_statue
            elif phase == "unlock_crate":
                self.phenotype.advance_plan()

        phase = self._plan_phase()

        if phase == "finalize":
            if "statue" in inv:
                if loc != "hall":
                    return [Action(tool="move", args={"location": "hall"})]
                return [Action(tool="place", args={"object_id": "statue", "location": "pedestal"})]
            return [Action(tool="submit", args={})]

        if phase == "transport_statue":
            if "statue" in inv:
                if loc != "hall":
                    return [Action(tool="move", args={"location": "hall"})]
                return [Action(tool="place", args={"object_id": "statue", "location": "pedestal"})]
            if "statue" in visible:
                return [Action(tool="take", args={"object_id": "statue"})]
            if loc != "vault":
                return [Action(tool="move", args={"location": "vault"})]
            return [Action(tool="take", args={"object_id": "statue"})]

        if phase == "unlock_crate":
            # Already open / statue available → advance.
            if "statue" in visible or "statue" in inv:
                self.phenotype.advance_plan()
                return self._key_crate_candidates(obs)
            held = [c for c in inv if c.startswith("coin")]
            usable = [c for c in held if c not in self.failed_keys]
            if usable:
                if loc != "vault":
                    return [Action(tool="move", args={"location": "vault"})]
                return [Action(tool="unlock", args={"object_id": "crate", "key_id": usable[0]})]
            self.phenotype.set_plan_index(0)  # back to find_key

        # find_key / reactive: gather coins and try them.
        if "statue" in inv:
            if loc != "hall":
                return [Action(tool="move", args={"location": "hall"})]
            return [Action(tool="place", args={"object_id": "statue", "location": "pedestal"})]
        if "statue" in visible:
            return [Action(tool="take", args={"object_id": "statue"})]

        held_coins = [c for c in inv if c.startswith("coin")]
        usable = [c for c in held_coins if c not in self.failed_keys]

        if usable and loc == "vault":
            return [Action(tool="unlock", args={"object_id": "crate", "key_id": usable[0]})]
        if usable and loc != "vault":
            return [Action(tool="move", args={"location": "vault"})]
        if held_coins and not usable:
            return [Action(tool="place", args={"object_id": held_coins[0], "location": loc})]

        coins_here = [
            o for o in visible if str(o).startswith("coin") and str(o) not in self.failed_keys
        ]
        if coins_here:
            coin = coins_here[0]
            actions = [Action(tool="take", args={"object_id": coin})]
            if coin not in self.inspected_objects:
                actions.append(Action(tool="inspect", args={"object_id": coin}))
            return actions

        return self._explore_rooms(loc, KEY_CRATE_ROOMS)

    # dial_set -------------------------------------------------------------

    def _dial_set_candidates(self, obs: Mapping[str, Any]) -> List[Action]:
        dials = obs.get("dials", {})

        need_offsets = not self.known_offsets
        need_gauges = [d for d in ("alpha", "beta", "gamma") if d not in self.known_gauges]

        if need_offsets or need_gauges:
            candidates: List[Action] = []
            if need_offsets:
                candidates.append(Action(tool="read_offset_card", args={}))
            for d in need_gauges:
                candidates.append(Action(tool="read_gauge", args={"dial": d}))
            return candidates

        # Info complete: plan moves to set_dials if it is still on gather_info.
        phase = self._plan_phase()
        if phase == "gather_info":
            self.phenotype.advance_plan()
            phase = self._plan_phase()

        pending = False
        for dial in ("alpha", "beta", "gamma"):
            target = (self.known_gauges[dial] - self.known_offsets[dial]) % 4
            if dials.get(dial) != target:
                pending = True
                return [Action(tool="set_dial", args={"dial": dial, "value": target})]

        if not pending:
            self._finish_phase_if(phase in {"gather_info", "set_dials"})
        return [Action(tool="submit", args={})]

    # relay_route ----------------------------------------------------------

    def _relay_candidates(self, obs: Mapping[str, Any]) -> List[Action]:
        loc = obs.get("location")
        visible = list(obs.get("visible_objects", []))
        relay = obs.get("relay", {}) or {}
        notes_read = obs.get("notes_read", {}) or {}
        phase = self._plan_phase()

        for nid, text in notes_read.items():
            self.known_frags[nid] = text

        missing = [f"note_{i}" for i in range(3) if f"note_{i}" not in self.known_frags]
        if missing:
            note = missing[0]
            if note in visible:
                return [Action(tool="read_note", args={"note_id": note})]
            return self._explore_rooms(loc, RELAY_ROOMS)

        frags = self.known_frags
        digit_strs = [_digit(frags[f"note_{i}"]) for i in range(3)]
        code = "".join(digit_strs)
        digits = [int(d) for d in digit_strs]
        frequency = (sum(digits) % 7) + 1

        if not relay.get("activated"):
            if loc != "hub":
                return [Action(tool="move", args={"location": "hub"})]
            self._finish_phase_if(phase in {"gather_notes", "activate"})
            return [Action(tool="activate_relay", args={"code": code})]

        if relay.get("frequency") != frequency:
            self._finish_phase_if(phase == "activate")
            return [Action(tool="set_frequency", args={"frequency": frequency})]

        self._finish_phase_if(phase in {"set_frequency", "activate", "gather_notes"})
        return [Action(tool="submit", args={})]

    def _explore_rooms(self, loc, rooms: Sequence[str]) -> List[Action]:
        """Explore rooms.

        memory_policy=bounded_episodic skips rooms already seen in phenotype.recall().
        memory_policy=none advances a cursor and may revisit (recall() is empty).
        """
        loc_s = str(loc)
        visited = set(self.phenotype.recalled_locations())

        if self.phenotype.genome.memory_policy == "bounded_episodic":
            order = [r for r in rooms if r not in visited]
            if not order:
                return [Action(tool="list_objects", args={})]
            return [Action(tool="move", args={"location": order[0]})]

        room = rooms[self.room_cursor % len(rooms)]
        self.room_cursor += 1
        if room != loc_s:
            return [Action(tool="move", args={"location": room})]
        return [Action(tool="list_objects", args={})]


def _digit(fragment_or_digit: Optional[str]) -> str:
    if fragment_or_digit is None:
        return "0"
    text = str(fragment_or_digit)
    if "digit" in text:
        return text.rsplit("digit", 1)[-1].strip()
    return text.strip()


def _goal_checks_passed(family: str, summary: Mapping[str, Any], policy: "MockPolicy") -> bool:
    """Public goal checks derived from verify_state output (no hidden goal)."""
    if family == "key_crate":
        surfaces = summary.get("surface_contents") or {}
        on_pedestal = "statue" in (surfaces.get("pedestal") or [])
        unlocked = (summary.get("unlocked") or {}).get("crate")
        return bool(on_pedestal and unlocked)
    if family == "dial_set":
        if not policy.known_offsets:
            return False
        dials = summary.get("dials") or {}
        for dial in ("alpha", "beta", "gamma"):
            if dial not in policy.known_gauges:
                return False
            target = (policy.known_gauges[dial] - policy.known_offsets[dial]) % 4
            if dials.get(dial) != target:
                return False
        return True
    if family == "relay_route":
        return bool(summary.get("relay_activated")) and summary.get("relay_frequency") is not None
    return False


def _ingest_mock_results(
    policy: MockPolicy,
    info: Mapping[str, Any],
    observation: Mapping[str, Any],
    action: Mapping[str, Any],
) -> None:
    result = info.get("result") or {}
    family = policy.family

    if action.get("tool") == "unlock" and info.get("valid") is False:
        key_id = (action.get("args") or {}).get("key_id")
        if key_id and key_id not in policy.failed_keys:
            policy.failed_keys.append(str(key_id))

    if action.get("tool") == "verify_state" and info.get("valid") is True:
        summary = dict(result)
        passed = _goal_checks_passed(family, summary, policy)
        summary["goal_checks_passed"] = passed
        policy.last_verify_summary = summary
        if passed:
            policy.phenotype.record_verification(summary)
            policy.phenotype.mark_verified()
        else:
            policy.phenotype.record_verification(summary)
            policy.phenotype.reset_verification()

    if family == "dial_set":
        if "offsets" in result:
            policy.known_offsets = dict(result["offsets"])
        if "dial" in result and "gauge" in result:
            policy.known_gauges[str(result["dial"])] = int(result["gauge"])
    elif family == "relay_route":
        if "note_id" in result and "text" in result:
            policy.known_frags[str(result["note_id"])] = str(result["text"])
        for nid, text in (observation.get("notes_read") or {}).items():
            policy.known_frags[str(nid)] = str(text)
    elif family == "key_crate":
        if action.get("tool") == "inspect":
            oid = (action.get("args") or {}).get("object_id")
            if oid and oid not in policy.inspected_objects:
                policy.inspected_objects.append(str(oid))
        if action.get("tool") == "place" and (action.get("args") or {}).get("object_id") == "statue":
            policy.placed_statue = True


def run_episode(
    task: TaskInstance,
    genome,
    *,
    seed: int = 0,
    backend_id: str = MOCK_BACKEND_ID,
    environment=None,
    evaluator=None,
    store_trace: bool = True,
) -> Tuple[bool, EpisodeTrace, Dict[str, Any]]:
    """Execute one deterministic mock episode. Engineering-only."""
    ph = compile_phenotype(genome)
    gh = genome_hash(ph.genome)
    policy = MockPolicy(
        phenotype=ph,
        runtime_task=task.runtime,
        family=task.family,
    )
    backend = MockBackend(policy)

    env = environment if environment is not None else ToolWorld()
    ev = evaluator if evaluator is not None else StateBasedEvaluator(genome_hash=gh)

    observation = env.reset(task)
    trace = EpisodeTrace(
        task_id=task.runtime.task_id,
        split=task.split,
        genome_hash=gh,
        backend_id=backend_id,
        seed=seed,
    )

    max_steps = task.runtime.max_steps
    terminated = False
    termination_reason = ""
    for i in range(max_steps):
        # Model-facing context: runtime task fields only (no seed/hash/hidden goal).
        runtime_context = {
            "task_id": task.runtime.task_id,
            "description": task.runtime.description,
            "max_steps": task.runtime.max_steps,
        }
        try:
            action = backend.propose(
                Observation(content=observation.content), runtime_context
            )
        except Exception as exc:  # fail closed on backend errors
            termination_reason = "backend_error"
            trace.final_state = dict(env.final_state())
            trace.termination_reason = termination_reason
            result = ev.evaluate(task, env.final_state(), trace.steps)
            return False, trace, {
                "error": str(exc),
                "episode_result": result,
                "engineering_only": True,
                "backend_payload": backend.last_payload,
            }

        try:
            step_result: StepResult = env.step(action)
        except Exception as exc:
            termination_reason = "error"
            trace.final_state = dict(env.final_state())
            trace.termination_reason = termination_reason
            result = ev.evaluate(task, env.final_state(), trace.steps)
            return False, trace, {
                "error": str(exc),
                "episode_result": result,
                "engineering_only": True,
                "backend_payload": backend.last_payload,
            }

        info = dict(step_result.info)
        valid = bool(info.get("valid", True))
        if action.tool == "submit":
            info["self_report_success"] = True

        if store_trace:
            trace.append_step(
                step_index=i,
                observation=observation.content,
                action=action.to_dict(),
                info=info,
                state_hash=state_hash(env.final_state()),
                valid=valid,
            )

        _ingest_mock_results(policy, info, observation.content, action.to_dict())
        observation = step_result.observation
        terminated = step_result.terminated
        termination_reason = step_result.termination_reason
        if terminated:
            break

    if not terminated:
        termination_reason = termination_reason or "max_steps"

    final_state = dict(env.final_state())
    trace.final_state = final_state
    trace.termination_reason = str(final_state.get("termination_reason", termination_reason))
    result = ev.evaluate(task, final_state, trace.steps)
    return bool(result.success), trace, {
        "episode_result": result,
        "final_state": final_state,
        "engineering_only": True,
        "backend_payload": backend.last_payload,
    }

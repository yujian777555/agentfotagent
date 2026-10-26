"""Deterministic controlled multi-step tool-use world (AES target environment).

Design constraints (docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md §5):
- hidden goal + explicit success predicate, evaluated from final world state only;
- typed tool API: read-only info tools and state-changing tools;
- multi-step tasks requiring information gathering, planning, action selection;
- invalid-action handling, explicit terminal states, reproducible reset/step;
- hidden goal is sealed inside the environment/evaluator and never observed by the Agent.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

from ..interfaces import Action, Observation, StepResult, TaskInstance


TOOL_WORLD_VERSION = "aes-tool-world-v1"

# Public tools visible to the Agent runtime.
READ_ONLY_TOOLS = (
    "list_objects",
    "inspect",
    "read_note",
    "read_gauge",
    "read_offset_card",
    "verify_state",
    "make_plan",
)
STATE_CHANGING_TOOLS = (
    "move",
    "take",
    "place",
    "unlock",
    "set_dial",
    "activate_relay",
    "set_frequency",
    "submit",
)
ALL_TOOLS = READ_ONLY_TOOLS + STATE_CHANGING_TOOLS


class HiddenGoalAccessError(RuntimeError):
    """Raised when code outside the evaluator/environment tries to read hidden goals."""


def _stable_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass
class _SealedGoal:
    """Opaque container. Attribute access is allowed only from evaluator/env paths."""

    goal: Mapping[str, Any]
    _unlocked: bool = False

    def unlock(self) -> Mapping[str, Any]:
        """Only environment termination scoring and the evaluator may call this."""
        if not self._unlocked:
            # Deliberately require an explicit unlock so accidental iteration/serialization
            # of the environment cannot dump the goal into traces.
            raise HiddenGoalAccessError(
                "hidden goal is sealed; only evaluator scoring unlocks it"
            )
        return self.goal

    def force_unlock(self) -> Mapping[str, Any]:
        """Environment-internal scoring path."""
        self._unlocked = True
        return self.goal


@dataclass
class WorldState:
    """Mutable world state. ``public_view()`` is the only Agent-visible projection."""

    location: str
    inventory: List[str]
    objects: Dict[str, Dict[str, Any]]
    dials: Dict[str, int]
    notes: Dict[str, str]
    relay: Dict[str, Any]
    plan: Optional[List[str]]
    step: int
    terminated: bool
    termination_reason: str
    flags: Set[str] = field(default_factory=set)
    read_notes: Set[str] = field(default_factory=set)

    def public_view(self) -> Dict[str, Any]:
        """Agent-visible projection: local only. No global object map, no hidden goals."""
        visible_here = sorted(
            oid
            for oid, obj in self.objects.items()
            if obj.get("location") == self.location and not obj.get("concealed")
        )
        # Notes become visible in observations only after read_note().
        read_notes = {
            nid: self.notes[nid] for nid in sorted(self.read_notes) if nid in self.notes
        }
        return {
            "location": self.location,
            "inventory": sorted(self.inventory),
            "visible_objects": visible_here,
            "dials": dict(self.dials),
            "relay": {
                "activated": bool(self.relay.get("activated", False)),
                "frequency": self.relay.get("frequency"),
            },
            "notes_read": read_notes,
            "plan": list(self.plan) if self.plan else None,
            "step": self.step,
            "terminated": self.terminated,
        }

    def snapshot(self) -> Dict[str, Any]:
        """Full state snapshot for evaluator + provenance (still without hidden goal)."""
        return {
            "location": self.location,
            "inventory": list(self.inventory),
            "objects": json.loads(json.dumps(self.objects, sort_keys=True)),
            "dials": dict(self.dials),
            "notes": dict(self.notes),
            "read_notes": sorted(self.read_notes),
            "relay": dict(self.relay),
            "plan": list(self.plan) if self.plan else None,
            "step": self.step,
            "terminated": self.terminated,
            "termination_reason": self.termination_reason,
            "flags": sorted(self.flags),
        }


class ToolWorld:
    """Deterministic sandboxed multi-step tool-use world."""

    version = TOOL_WORLD_VERSION

    def __init__(self, max_steps_default: int = 40) -> None:
        self.max_steps_default = max_steps_default
        self._task: Optional[TaskInstance] = None
        self._goal: Optional[_SealedGoal] = None
        self._state: Optional[WorldState] = None
        self._initial_state_hash: str = ""

    # -- lifecycle ---------------------------------------------------------

    def reset(self, task: TaskInstance) -> Observation:
        self._task = task
        self._goal = _SealedGoal(goal=dict(task.hidden_goal))
        self._state = self._build_state(task)
        self._initial_state_hash = _stable_hash(self._state.snapshot())
        return Observation(content=self._state.public_view())

    def _build_state(self, task: TaskInstance) -> WorldState:
        setup = task.setup
        return WorldState(
            location=str(setup.get("start_location", "hall")),
            inventory=[],
            objects=json.loads(json.dumps(setup.get("objects", {}), sort_keys=True)),
            dials=dict(setup.get("dials", {})),
            notes=dict(setup.get("notes", {})),
            relay=dict(setup.get("relay", {"activated": False, "frequency": None, "code": None})),
            plan=None,
            step=0,
            terminated=False,
            termination_reason="",
        )

    @property
    def current_public_view(self) -> Mapping[str, Any]:
        assert self._state is not None, "reset() must be called first"
        return self._state.public_view()

    def final_state(self) -> Mapping[str, Any]:
        assert self._state is not None, "reset() must be called first"
        return self._state.snapshot()

    # -- stepping ----------------------------------------------------------

    def step(self, action: Action) -> StepResult:
        assert self._state is not None and self._task is not None, "reset() must be called first"
        st = self._state
        if st.terminated:
            raise RuntimeError("episode already terminated")

        tool = action.tool
        if tool not in ALL_TOOLS:
            result = self._invalid(f"unknown tool: {tool}")
        else:
            handler = getattr(self, f"_tool_{tool}", None)
            if handler is None:
                result = self._invalid(f"tool not implemented: {tool}")
            else:
                result = handler(dict(action.args))

        # Invalid actions must not mutate world fields other than the step counter
        # (handled inside handlers only on success). We still count the step.
        if not result.info.get("valid", True):
            st.step += 1
            if st.step >= self._task.public.max_steps and not st.terminated:
                self._terminate("max_steps")
            return StepResult(
                observation=Observation(content=st.public_view()),
                terminated=st.terminated,
                termination_reason=st.termination_reason,
                info=dict(result.info),
            )

        st.step += 1
        if not st.terminated and st.step >= self._task.public.max_steps:
            self._terminate("max_steps")

        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=st.terminated,
            termination_reason=st.termination_reason,
            info=dict(result.info),
        )

    def _invalid(self, message: str) -> StepResult:
        return StepResult(
            observation=Observation(content=self._state.public_view()),  # type: ignore[union-attr]
            terminated=False,
            termination_reason="",
            info={"valid": False, "error": message},
        )

    def _terminate(self, reason: str) -> None:
        assert self._state is not None
        self._state.terminated = True
        self._state.termination_reason = reason

    # -- tools -------------------------------------------------------------

    def _tool_list_objects(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        here = sorted(
            oid
            for oid, obj in st.objects.items()
            if obj.get("location") == st.location and not obj.get("concealed")
        )
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"objects": here}},
        )

    def _tool_inspect(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        oid = args.get("object_id")
        if oid not in st.objects:
            return self._invalid(f"unknown object: {oid}")
        obj = st.objects[oid]
        if obj.get("concealed"):
            return self._invalid(f"unknown object: {oid}")
        # Inspection requires proximity: object is here or already held.
        if obj.get("location") != st.location and oid not in st.inventory:
            return self._invalid(f"object not here: {oid}")
        public_attrs = {
            "id": oid,
            "type": obj.get("type"),
            "location": obj.get("location"),
            "unlocked": obj.get("unlocked"),
            "description": obj.get("description"),
            "tags": list(obj.get("tags", [])),
        }
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": public_attrs},
        )

    def _tool_read_note(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        note_id = args.get("note_id")
        if note_id not in st.notes:
            return self._invalid(f"unknown note: {note_id}")
        # Require the note object to be local (visible at current location).
        note_obj = st.objects.get(str(note_id))
        if note_obj is None or note_obj.get("location") != st.location:
            return self._invalid(f"note not here: {note_id}")
        st.read_notes.add(str(note_id))
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"note_id": note_id, "text": st.notes[note_id]}},
        )

    def _tool_read_gauge(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        dial = args.get("dial")
        setup = self._task.setup if self._task else {}
        gauges = setup.get("gauges", {})
        if dial not in gauges:
            return self._invalid(f"unknown dial: {dial}")
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"dial": dial, "gauge": gauges[dial]}},
        )

    def _tool_read_offset_card(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        setup = self._task.setup if self._task else {}
        offsets = setup.get("offsets", {})
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"offsets": dict(offsets)}},
        )

    def _tool_verify_state(self, args: Mapping[str, Any]) -> StepResult:
        """Public consistency summary used by verification_policy. No hidden goal."""
        st = self._state
        assert st is not None
        unlocked = {oid: bool(o.get("unlocked", True)) for oid, o in st.objects.items() if o.get("type") in {"crate", "relay"}}
        summary = {
            "unlocked": unlocked,
            "dials": dict(st.dials),
            "inventory": sorted(st.inventory),
            "relay_activated": bool(st.relay.get("activated", False)),
            "relay_frequency": st.relay.get("frequency"),
        }
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": summary},
        )

    def _tool_make_plan(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        steps = args.get("steps") or args.get("plan") or []
        if not isinstance(steps, (list, tuple)):
            return self._invalid("plan steps must be a list")
        st.plan = [str(s) for s in steps]
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"plan": st.plan}},
        )

    def _tool_move(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        loc = args.get("location")
        setup = self._task.setup if self._task else {}
        locations = setup.get("locations", [])
        if loc not in locations:
            return self._invalid(f"unknown location: {loc}")
        st.location = str(loc)
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"location": st.location}},
        )

    def _tool_take(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        oid = args.get("object_id")
        if oid not in st.objects or st.objects[oid].get("concealed"):
            return self._invalid(f"unknown object: {oid}")
        obj = st.objects[oid]
        if obj.get("type") not in {"portable", "artifact", "key"}:
            return self._invalid(f"object not portable: {oid}")
        if obj.get("location") != st.location:
            return self._invalid(f"object not here: {oid}")
        if obj.get("inside"):
            container = obj["inside"]
            cont = st.objects.get(container, {})
            if cont.get("locked") or cont.get("unlocked") is False:
                return self._invalid(f"object locked inside: {container}")
        if oid in st.inventory:
            return self._invalid(f"already held: {oid}")
        obj["location"] = "inventory"
        obj["inside"] = None
        st.inventory.append(oid)
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"inventory": sorted(st.inventory)}},
        )

    def _tool_place(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        oid = args.get("object_id")
        dest = args.get("location")
        if oid not in st.inventory:
            return self._invalid(f"not held: {oid}")
        setup = self._task.setup if self._task else {}
        valid_dest = set(setup.get("locations", [])) | set(setup.get("surfaces", []))
        if dest not in valid_dest:
            return self._invalid(f"unknown destination: {dest}")
        st.inventory.remove(oid)
        st.objects[oid]["location"] = dest
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"object_id": oid, "location": dest}},
        )

    def _tool_unlock(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        oid = args.get("object_id")
        key_id = args.get("key_id")
        if oid not in st.objects:
            return self._invalid(f"unknown object: {oid}")
        obj = st.objects[oid]
        if key_id not in st.inventory:
            return self._invalid(f"key not held: {key_id}")
        required = obj.get("lock_key")
        if not required:
            return self._invalid(f"object not locked: {oid}")
        if key_id != required:
            return self._invalid("wrong key")
        obj["unlocked"] = True
        obj["locked"] = False
        # Release contained objects to the unlocker's location and un-conceal them.
        for other_id, other in st.objects.items():
            if other.get("inside") == oid:
                other["location"] = st.location
                other["inside"] = None
                other["concealed"] = False
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"object_id": oid, "unlocked": True}},
        )

    def _tool_set_dial(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        dial = args.get("dial")
        value = args.get("value")
        if dial not in st.dials:
            return self._invalid(f"unknown dial: {dial}")
        if not isinstance(value, int) or isinstance(value, bool):
            return self._invalid("dial value must be an int")
        st.dials[str(dial)] = int(value)
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"dial": dial, "value": int(value)}},
        )

    def _tool_activate_relay(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        code = args.get("code")
        expected = st.relay.get("code")
        if expected is None:
            return self._invalid("relay not configured")
        if str(code) != str(expected):
            return self._invalid("wrong code")
        st.relay["activated"] = True
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"activated": True}},
        )

    def _tool_set_frequency(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        if not st.relay.get("activated"):
            return self._invalid("relay not activated")
        freq = args.get("frequency")
        if not isinstance(freq, int) or isinstance(freq, bool):
            return self._invalid("frequency must be an int")
        st.relay["frequency"] = int(freq)
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=False,
            termination_reason="",
            info={"valid": True, "result": {"frequency": int(freq)}},
        )

    def _tool_submit(self, args: Mapping[str, Any]) -> StepResult:
        st = self._state
        assert st is not None
        self._terminate("agent_submit")
        return StepResult(
            observation=Observation(content=st.public_view()),
            terminated=True,
            termination_reason="agent_submit",
            info={"valid": True, "result": {"submitted": True}},
        )

    # -- scoring support ---------------------------------------------------

    def unlock_goal_for_scoring(self) -> Mapping[str, Any]:
        """Explicit evaluator path. Runtime Agent code must never call this."""
        if self._goal is None:
            raise RuntimeError("no task loaded")
        return self._goal.force_unlock()


def load_task_from_dict(raw: Mapping[str, Any]) -> TaskInstance:
    """Reconstruct a TaskInstance from a serialized manifest entry."""
    from ..interfaces import PublicTask

    public = PublicTask(
        task_id=str(raw["public"]["task_id"]),
        family=str(raw["public"]["family"]),
        split=str(raw["public"]["split"]),
        description=str(raw["public"]["description"]),
        max_steps=int(raw["public"]["max_steps"]),
        seed=int(raw["public"]["seed"]),
        generator_version=str(raw["public"]["generator_version"]),
        content_hash=str(raw["public"]["content_hash"]),
    )
    return TaskInstance(
        public=public,
        hidden_goal=dict(raw["hidden_goal"]),
        setup=dict(raw["setup"]),
        seed=int(raw["seed"]),
        generator_version=str(raw["generator_version"]),
        content_hash=str(raw["content_hash"]),
    )


def task_content_hash(
    family: str,
    seed: int,
    generator_version: str,
    setup: Mapping[str, Any],
    hidden_goal: Mapping[str, Any],
    description: str,
    max_steps: int,
) -> str:
    payload = {
        "family": family,
        "seed": seed,
        "generator_version": generator_version,
        "setup": setup,
        "hidden_goal": hidden_goal,
        "description": description,
        "max_steps": max_steps,
    }
    return _stable_hash(payload)


def state_hash(state: Mapping[str, Any]) -> str:
    return _stable_hash(state)

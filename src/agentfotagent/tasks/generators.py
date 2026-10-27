"""Procedural task generators with task-family train/dev/held-out splits.

Families
--------
- ``key_crate``   (train + dev): find a key among decoys, unlock a crate, transfer artifact.
- ``dial_set``    (train + dev): gather gauge readings + offset card, set three dials.
- ``relay_route`` (held-out only): assemble a code from notes, activate relay, set frequency.

Held-out families are disjoint from train/dev families so holdout tests measure
family-level generalization, not merely new seeds of seen families.
"""
from __future__ import annotations

import random
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from ..environments.tool_world import task_content_hash
from ..interfaces import RuntimeTask, TaskInstance


GENERATOR_VERSION = "aes-task-gen-v1"

FAMILIES: Tuple[str, ...] = ("key_crate", "dial_set", "relay_route")

# Family → splits it participates in. Held-out family is never in train/dev.
FAMILY_SPLITS: Dict[str, Tuple[str, ...]] = {
    "key_crate": ("train", "dev"),
    "dial_set": ("train", "dev"),
    "relay_route": ("held_out",),
}

DEFAULT_MAX_STEPS = {
    "key_crate": 24,
    "dial_set": 16,
    "relay_route": 20,
}


def generate_task(family: str, seed: int, split: str, task_id: str | None = None) -> TaskInstance:
    if family not in FAMILIES:
        raise ValueError(f"unknown family: {family}")
    if split not in FAMILY_SPLITS[family]:
        raise ValueError(f"family {family} does not support split {split}")
    if task_id is None:
        task_id = f"{family}/{split}/seed{seed:06d}"
    if family == "key_crate":
        return _gen_key_crate(seed, split, task_id)
    if family == "dial_set":
        return _gen_dial_set(seed, split, task_id)
    return _gen_relay_route(seed, split, task_id)


def _make_task(
    family: str,
    split: str,
    task_id: str,
    seed: int,
    description: str,
    setup: Dict[str, Any],
    hidden_goal: Dict[str, Any],
) -> TaskInstance:
    max_steps = DEFAULT_MAX_STEPS[family]
    content_hash = task_content_hash(
        family=family,
        seed=seed,
        generator_version=GENERATOR_VERSION,
        setup=setup,
        hidden_goal=hidden_goal,
        description=description,
        max_steps=max_steps,
    )
    runtime = RuntimeTask(
        task_id=task_id,
        description=description,
        max_steps=max_steps,
    )
    return TaskInstance(
        runtime=runtime,
        family=family,
        split=split,
        hidden_goal=hidden_goal,
        setup=setup,
        seed=seed,
        generator_version=GENERATOR_VERSION,
        content_hash=content_hash,
    )


# ---------------------------------------------------------------------------
# Family: key_crate
# ---------------------------------------------------------------------------

def _gen_key_crate(seed: int, split: str, task_id: str) -> TaskInstance:
    rng = random.Random(seed * 7919 + 13)
    key_ids = ["coin_a", "coin_b", "coin_c"]
    rng.shuffle(key_ids)
    key_id = key_ids[0]
    decoys = key_ids[1:]

    key_room = rng.choice(["storage", "corridor", "vault"])
    decoy_rooms = [r for r in ["storage", "corridor", "vault"] if r != key_room]
    rng.shuffle(decoy_rooms)

    setup: Dict[str, Any] = {
        "start_location": "hall",
        "locations": ["hall", "storage", "corridor", "vault"],
        "surfaces": ["pedestal"],
        "dials": {},
        "notes": {},
        "relay": {"activated": False, "frequency": None, "code": None},
        "objects": {
            "crate": {
                "type": "crate",
                "location": "vault",
                "locked": True,
                "unlocked": False,
                "lock_key": key_id,
                "description": "a locked crate",
                "tags": ["container"],
            },
            "statue": {
                "type": "artifact",
                "location": "vault",
                "inside": "crate",
                "description": "a small statue",
                "tags": ["artifact"],
            },
            "pedestal": {
                "type": "surface",
                "location": "hall",
                "description": "display pedestal",
                "tags": ["surface"],
            },
            key_id: {
                "type": "key",
                "location": key_room,
                "description": "a metal coin that looks like a key",
                "tags": ["coin"],
            },
            decoys[0]: {
                "type": "key",
                "location": decoy_rooms[0],
                "description": "a metal coin that looks like a key",
                "tags": ["coin"],
            },
            decoys[1]: {
                "type": "key",
                "location": decoy_rooms[1],
                "description": "a metal coin that looks like a key",
                "tags": ["coin"],
            },
        },
    }

    # Statue is concealed until the crate is unlocked (public world never reveals goal).
    setup["objects"]["statue"]["concealed"] = True

    hidden_goal = {
        "type": "key_crate",
        "object_on_surface": {"object": "statue", "surface": "pedestal"},
        "crate_unlocked": True,
        "required_unlock_key": key_id,
    }
    description = (
        "Move the statue onto the pedestal in the hall. "
        "The statue is inside a locked crate in the vault. "
        "Exactly one of the coin-like keys unlocks the crate; the others are decoys. "
        "Call submit when done."
    )
    return _make_task("key_crate", split, task_id, seed, description, setup, hidden_goal)


# ---------------------------------------------------------------------------
# Family: dial_set
# ---------------------------------------------------------------------------

def _gen_dial_set(seed: int, split: str, task_id: str) -> TaskInstance:
    rng = random.Random(seed * 104729 + 7)
    names = ["alpha", "beta", "gamma"]
    targets = {n: rng.randrange(4) for n in names}
    offsets = {n: rng.randrange(4) for n in names}
    gauges = {n: (targets[n] + offsets[n]) % 4 for n in names}

    setup: Dict[str, Any] = {
        "start_location": "console",
        "locations": ["console"],
        "surfaces": [],
        "dial_location": "console",
        "dials": {n: 0 for n in names},
        "gauges": gauges,
        "offsets": offsets,
        "notes": {},
        "relay": {"activated": False, "frequency": None, "code": None},
        "objects": {
            "console": {
                "type": "surface",
                "location": "console",
                "description": "calibration console",
                "tags": ["console"],
            }
        },
    }
    hidden_goal = {
        "type": "dial_set",
        "targets": targets,
        "formula": "target = (gauge - offset) % 4",
    }
    description = (
        "Set dials alpha, beta, gamma to their hidden calibration targets. "
        "Each dial has a gauge reading equal to (target + offset) % 4. "
        "The offset card lists the offsets. "
        "Compute target = (gauge - offset) % 4 for each dial, set them, then submit."
    )
    return _make_task("dial_set", split, task_id, seed, description, setup, hidden_goal)


# ---------------------------------------------------------------------------
# Family: relay_route (held-out only)
# ---------------------------------------------------------------------------

def _gen_relay_route(seed: int, split: str, task_id: str) -> TaskInstance:
    rng = random.Random(seed * 15485863 + 3)
    digits = [rng.randrange(10) for _ in range(3)]
    code = "".join(str(d) for d in digits)
    frequency = (sum(digits) % 7) + 1  # public formula in the task description

    rooms = ["north", "south", "east"]
    note_ids = [f"note_{i}" for i in range(3)]
    placements = list(zip(note_ids, rooms))
    rng.shuffle(placements)
    notes = {}
    note_room = {}
    for note_id, room in placements:
        note_room[note_id] = room
    for i, note_id in enumerate(note_ids):
        notes[note_id] = f"fragment {i}: digit {digits[i]}"

    setup: Dict[str, Any] = {
        "start_location": "hub",
        "locations": ["hub"] + rooms,
        "surfaces": [],
        "dials": {},
        "notes": notes,
        "note_room": note_room,
        "relay": {"activated": False, "frequency": None, "code": code},
        "objects": {
            "relay": {
                "type": "relay",
                "location": "hub",
                "locked": True,
                "unlocked": False,
                "description": "route relay terminal",
                "tags": ["relay"],
            }
        },
    }
    # Attach each note as an inspectable object in its room.
    for note_id, room in placements:
        setup["objects"][note_id] = {
            "type": "note",
            "location": room,
            "description": "a paper note",
            "tags": ["note"],
        }

    hidden_goal = {
        "type": "relay_route",
        "code": code,
        "frequency": frequency,
        "formula": "frequency = (digit_sum % 7) + 1",
        "note_digits": {note_id: digits[i] for i, note_id in enumerate(note_ids)},
    }
    description = (
        "Activate the relay at the hub and set its frequency. "
        "Three notes in the north, south and east rooms each contain one code fragment "
        "in the form 'fragment i: digit d'. The three-digit code is fragment digits in order 0,1,2. "
        "Activate the relay with that code, then set frequency to (digit_sum % 7) + 1, then submit."
    )
    return _make_task("relay_route", split, task_id, seed, description, setup, hidden_goal)


# ---------------------------------------------------------------------------
# Split manifests
# ---------------------------------------------------------------------------

def generate_split_manifests(
    train_seeds: Sequence[int],
    dev_seeds: Sequence[int],
    held_out_seeds: Sequence[int],
) -> Dict[str, List[TaskInstance]]:
    """Build train/dev/held-out instance lists.

    - train: families with FAMILY_SPLITS including 'train'
    - dev:   families with FAMILY_SPLITS including 'dev'
    - held_out: families with FAMILY_SPLITS including 'held_out' (family-disjoint)
    """
    train: List[TaskInstance] = []
    dev: List[TaskInstance] = []
    held_out: List[TaskInstance] = []

    for family, splits in FAMILY_SPLITS.items():
        if "train" in splits:
            for seed in train_seeds:
                train.append(generate_task(family, seed, "train"))
        if "dev" in splits:
            for seed in dev_seeds:
                dev.append(generate_task(family, seed, "dev"))
        if "held_out" in splits:
            for seed in held_out_seeds:
                held_out.append(generate_task(family, seed, "held_out"))

    return {"train": train, "dev": dev, "held_out": held_out}

"""MetaBox-v2 source-domain adapter (reserved).

Phase-0 does not integrate MetaBox. This package exists so the layout matches
docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md §3. No MetaBox meta-training is
authorized until a separately reviewed experiment plan is approved.
"""

ADAPTER_STATUS = "RESERVED_NOT_IMPLEMENTED"


def not_authorized() -> None:
    raise RuntimeError(
        "MetaBox integration is not authorized in Phase-0. "
        "See docs/OWN_EXPERIMENTAL_ENVIRONMENT_SPEC.md §8 and planner/latest_plan.md Task 4."
    )

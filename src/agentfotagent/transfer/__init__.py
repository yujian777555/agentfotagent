"""Transfer object package (reserved).

The transfer object between source-domain optimization and target-domain Agent
genotypes must be specified and approved before implementation. Phase-0 only
reserves the boundary.
"""

TRANSFER_STATUS = "RESERVED_SEMANTICS_NOT_APPROVED"


def not_authorized() -> None:
    raise RuntimeError(
        "Transfer object semantics are not approved yet. "
        "See planner/latest_plan.md Task 3."
    )

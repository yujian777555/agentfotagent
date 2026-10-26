# results/

Append-only run manifests, raw trajectories, checksums and analysis outputs.

- `manifests/` — frozen task-split manifests (public index + evaluation-side full splits).
- `runs/` — future experiment run records. Phase-0 writes only engineering artifacts.

Never store secrets. Mock-backend outputs are engineering-only and must never be
reported as Agent capability evidence.

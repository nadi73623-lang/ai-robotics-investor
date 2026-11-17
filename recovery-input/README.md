# Archive upload required

Place exactly one file in this directory:

`AI_Robotics_Investor_Balanced_1.3.4_Corrected_2026-11-17_v2.zip`

Expected SHA-256:

`a128ecc73cc7ff62b96104c1ecb41d19f9c060601b59dea001c8be288fdd8f5f`

After the ZIP is committed to this branch, GitHub Actions workflow
`.github/workflows/recover-balanced-archive.yml` should run automatically.
It verifies the archive, extracts the project under `recovered/AI_Robotics_Investor/`,
runs Python bytecode compilation, and commits the recovered source snapshot to
this repair branch.

Do not upload secrets, API keys, or production credentials here.

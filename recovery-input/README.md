# Archive upload required

Place exactly one file in this directory:

`AI_Robotics_Investor_Balanced_1.3.4_Corrected_2026-11-17.zip`

Expected SHA-256:

`d55e0aac82a10f9e1567395d70cf2d4a354ee3100301c02d01096c5db5781401`

After the ZIP is committed to this branch, GitHub Actions workflow
`.github/workflows/recover-balanced-archive.yml` should run automatically.
It verifies the archive, extracts the project under `recovered/AI_Robotics_Investor/`,
runs Python bytecode compilation, and commits the recovered source snapshot to
this repair branch.

Do not upload secrets, API keys, or production credentials here.

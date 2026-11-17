# Archive upload required

Place exactly one file in this directory:

`AI_Robotics_Investor_Balanced_1.3.4_Corrected_2026-11-17_v3.zip`

Expected SHA-256:

`25b70bf831667bbb90e8cb6562d96f080dc27fdeca563b707ee1e30a76f56610`

After the ZIP is committed to this branch, GitHub Actions workflow
`.github/workflows/recover-balanced-archive.yml` should run automatically.
It verifies the archive, extracts the project under `recovered/AI_Robotics_Investor/`,
runs Python bytecode compilation, and commits the recovered source snapshot to
this repair branch.

Do not upload secrets, API keys, or production credentials here.

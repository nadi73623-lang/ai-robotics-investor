# Archive upload required

Place exactly one file in this directory:

`AI_Robotics_Investor_Balanced_1.3.4_Corrected_2026-11-17_v4.zip`

Expected SHA-256:

`783e2029896a381e82ccf814c1fc8b4793e2c5f3588612a96ed84eeb4051eeca`

After the ZIP is committed to this branch, GitHub Actions workflow
`.github/workflows/recover-balanced-archive.yml` should run automatically.
It verifies the archive, extracts the project under `recovered/AI_Robotics_Investor/`,
runs Python bytecode compilation, and commits the recovered source snapshot to
this repair branch.

Do not upload secrets, API keys, or production credentials here.

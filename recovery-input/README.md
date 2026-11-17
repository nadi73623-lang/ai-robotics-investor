# Archive upload required

Place exactly one file in this directory:

`AI_Robotics_Investor_Balanced_1.3.4_Global_Equity_Master_2026-11-08_2.zip`

Expected SHA-256:

`49d694dc8a3b3e3402654e2ed0c205b589fdaed0383baf0a8c5155ba3a9c8a81`

After the ZIP is committed to this branch, GitHub Actions workflow
`.github/workflows/recover-balanced-archive.yml` should run automatically.
It verifies the archive, extracts the project under `recovered/AI_Robotics_Investor/`,
runs Python bytecode compilation, and commits the recovered source snapshot to
this repair branch.

Do not upload secrets, API keys, or production credentials here.

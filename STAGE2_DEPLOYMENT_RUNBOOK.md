# Stage2 deployment runbook — AI Robotics read-only endpoint

## Scope and safety
Separate read-only Worker. It does not replace the existing report publisher and must not be merged into the scanner publishing path. It has no KV write operation and exposes only GET, HEAD and OPTIONS.

## Existing KV binding
The verified existing namespace `AI_ROBOTICS_REPORT` is configured in `private_sync_worker/wrangler.robotics-report.toml`.
Namespace ID: `35a4ec24211540fa9a098923773d667f`.
The Worker reads only `latest_scan`. Do not create another namespace and do not change the publisher.

## Required GitHub environment secrets
In repository Settings → Environments → `robotics-worker-production`, configure:
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN` (only the permissions required to deploy this Worker and set its secret)
- `ROBOTICS_READ_TOKEN` (long, unique read-only endpoint token)

Never put secret values in Git or chat. The KV namespace ID is not a secret and is already configured in the Wrangler TOML.

## Deployment
After the three secrets are configured, open Actions → Deploy read-only Robotics Worker → Run workflow, selecting `stage2-balanced-1.3.4`.
The workflow runs Worker tests before deploying. Deployment has not yet been run or verified.

## Report acceptance gate
Current KV value was inspected by the owner and reported as:
- `release_ready=false`
- strategy field missing
- `generated_at=2026-10-16T08:29:04.568185+00:00`

This report is not publishable through the read-only endpoint. The Worker intentionally rejects it with HTTP 503. Do not edit these fields manually or weaken validation. First run the real scanner/publisher successfully and verify a fresh report with `release_ready=true`, strategy `balanced-1.3-audit`, and timestamp no older than 36 hours.

## Smoke checks after deployment and report refresh
- Authenticated GET `/api/robotics/report`: expected HTTP 200 with the actual current approved report.
- Unauthenticated GET: HTTP 401.
- PUT: HTTP 405.
- Stale/non-release-ready report: HTTP 503.

## Android acceptance
Install verified debug APK `AI-Robotics-Investor-0.1.231-debug.apk` on Motorola Edge 30 Fusion. Configure deployed HTTPS Worker URL and `ROBOTICS_READ_TOKEN`. Confirm current report loads and invalid token is rejected. APK is debug-signed, not a production release.

## Current state (2026-11-11)
- Branch: `stage2-balanced-1.3.4`; `main` remains unchanged.
- Android 0.1.231 debug APK built and verified in GitHub Actions, including AES-GCM token encryption using Android Keystore.
- Existing KV namespace ID is now configured in the isolated Worker.
- Worker deployment and live endpoint smoke tests remain pending.
- Current KV report fails the release gate; scanner/publisher refresh is required before Android live-report acceptance.
- No paid service is required by this code. Do not enable paid features without owner approval.


## Root-cause audit of stale KV (2026-11-11)
- The current `.github/workflows/scan.yml` on `main` runs `python scanner.py` and commits only `data/scan.json`. It contains no Cloudflare credentials, KV binding, or KV publication step.
- The Stage2 branch has the same scan workflow behavior. The separate read-only Worker only calls KV `get("latest_scan")`; it cannot refresh or publish the key.
- Therefore a new market scan in GitHub does not automatically update the existing Cloudflare KV namespace. The owner-reported 2026-10-16 value can remain stale until the separate, currently unidentified publisher is located or an approved publisher integration is designed.
- Current scanner output is a public-news/SEC/price attention report. It does not contain the required Balanced 1.3 release gate fields (`release_ready=true`, `strategy_version=balanced-1.3-audit`) and must not be relabeled as an approved Balanced report.
- Do not connect `data/scan.json` directly to the production KV key or loosen the Worker validation. That would bypass investment-data and release-quality gates.
- Next safe prerequisite: identify the existing publisher (likely outside this repository or in a separate Cloudflare Worker) and audit its source and deployment history. Then implement an explicit validated publication path only after Balanced 1.3 is genuinely integrated and its data acceptance tests pass.

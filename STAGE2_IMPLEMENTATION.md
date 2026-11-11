# Stage2 — AI Robotics read-only Android integration

This is a reconstruction from the preserved repository baseline and the Stage2 interface specification. It is not the recovered original ZIP.

## Android
- App version: 0.1.231 (versionCode 231), Java 17, compile/target SDK 35, AGP 8.7.3, Gradle 8.9.
- Separate AI Robotics screen with HTTPS backend URL and locally stored READ_TOKEN.
- GET /api/robotics/report only. Client rejects reports unless release_ready=true, strategy balanced-1.3-audit, and timestamp is not future or older than 36 hours.
- No trading execution, write endpoint, or real-money order path is included.

## Read-only Worker
- Deploy separately using private_sync_worker/wrangler.robotics-report.toml.
- Bind existing KV namespace to ROBOTICS_REPORT_KV and set secret READ_TOKEN.
- Reads only latest_scan. Supports GET, HEAD, OPTIONS; all other methods return 405.
- Requires READ_TOKEN and repeats release_ready, strategy, timestamp and size checks.
- Does not publish, mutate KV, or bypass the existing report publisher's release gates.

## Build
GitHub Actions builds a debug APK on pushes to this branch and on manual dispatch. Artifact name: AI-Robotics-Investor-0.1.231-debug.
The APK is not a production-signed release. No APK is claimed until a successful workflow artifact is available.

## Deployment prerequisites
- Existing Cloudflare KV namespace ID and Worker route/domain.
- Set READ_TOKEN as a Worker secret. Do not commit it.
- No paid service is required by this code. No Worker deployment is performed automatically.

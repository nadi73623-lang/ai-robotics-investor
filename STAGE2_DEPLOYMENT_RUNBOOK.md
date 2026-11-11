# Stage2 deployment runbook — AI Robotics read-only endpoint

## Scope and safety
This is a separate read-only Worker. It does not replace the existing report publisher and must not be merged into the scanner's publishing path. It has no KV write operation and exposes only GET, HEAD and OPTIONS. Do not put Cloudflare credentials, KV IDs or READ_TOKEN in Git.

## Required values (owner-provided)
- Existing Cloudflare KV namespace ID containing the published `latest_scan` report.
- A Worker hostname/route under a domain controlled by the owner.
- A long, unique `READ_TOKEN` (keep it private).
- Cloudflare account access for the deployment operator.

No value above is guessed or embedded in this repository. No paid plan or service is required by this code itself; check current account limits/pricing before enabling optional paid features.

## Deploy from the repository root
1. In Cloudflare, identify the existing KV namespace that already receives the approved `latest_scan` report. Do not create a second namespace unless the publishing pipeline is deliberately configured to write to it.
2. Replace `REPLACE_WITH_EXISTING_KV_NAMESPACE_ID` in `private_sync_worker/wrangler.robotics-report.toml` with that exact namespace ID.
3. From `private_sync_worker/`, authenticate Wrangler with the intended Cloudflare account and deploy:
   ```sh
   npx wrangler login
   npx wrangler secret put READ_TOKEN --config wrangler.robotics-report.toml
   npx wrangler deploy --config wrangler.robotics-report.toml
   ```
   Prefer an already-installed Wrangler. Do not install or subscribe to a paid service without approval.
4. Record the deployed HTTPS Worker URL privately. Do not commit the token or secret config.
5. Confirm the KV namespace contains a current, approved `latest_scan` report with `release_ready=true`, strategy `balanced-1.3-audit`, and a timestamp no older than 36 hours.

## Smoke checks
Set the URL and token locally; do not paste the token into chat or commit it.
```sh
curl -i -H "Authorization: Bearer $READ_TOKEN" "$WORKER_URL/api/robotics/report"
curl -i -X PUT -H "Authorization: Bearer $READ_TOKEN" "$WORKER_URL/api/robotics/report"
```
Expected: authenticated GET returns HTTP 200 with the approved report; PUT returns HTTP 405. Unauthenticated GET must return HTTP 401; stale or non-release-ready reports must be rejected with HTTP 503. Never use a fabricated report as evidence of live readiness.

## Android installation and acceptance
- Install the newly built, verified debug APK `AI-Robotics-Investor-0.1.231-debug.apk` on Motorola Edge 30 Fusion.
- In **Konfiguracja**, enter the deployed HTTPS Worker base URL and dedicated read-only `READ_TOKEN`.
- Tap **Pobierz raport**. Acceptance requires the real current report to display and pass release/strategy/timestamp checks.
- Confirm an invalid token is rejected and no write/trading capability is present.

## Android token protection
The current source stores the token ciphertext in app-private SharedPreferences, encrypted with AES-GCM. The AES key is generated and retained by Android Keystore and is not stored in the preferences file. A one-time migration encrypts the legacy plaintext preference and removes that old key after successful encryption. If decryption/migration fails, the app treats the token as unavailable. Device lock and app sandbox protections still matter; rotate the read token if the device is lost. This is not a substitute for physical-device acceptance.

## Current verified state (2026-11-11)
- Branch: `stage2-balanced-1.3.4`
- Security source commit: `76c22a16fa5531ac86f08a6539f16d8b8dfa3117`.
- Android source uses AES-GCM with Android Keystore. A fresh CI build for this commit must be confirmed before treating its APK as verified.
- Earlier build commit `1ef3f9c94042360307c33db99a959523f623c52c`, run `43017737668`: success; Worker tests, metadata validation, debug build and APK checksum passed for that earlier source revision only.
- Earlier APK SHA-256: `07a77910dccf244ef0f6de65e236b91b6ac3cf2eeb9c54d562f76c9a18f26900`. This checksum does not identify a build containing the later Keystore change.
- Cloudflare deployment, live current-report verification and physical-device acceptance are not performed.
- APK is debug-signed, not a production release.
- `main` and the existing scanner are not changed by this Stage2 branch.

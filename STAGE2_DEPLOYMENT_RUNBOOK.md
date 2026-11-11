# Stage2 deployment runbook — AI Robotics read-only endpoint

## Scope and safety
This is a separate read-only Worker. It does not replace the existing report publisher and must not be merged into the scanner's publishing path. It has no KV write operation and exposes only GET, HEAD and OPTIONS. Do not put Cloudflare credentials, KV IDs or READ_TOKEN in Git.

## Required values (owner-provided)
- Existing Cloudflare KV namespace ID containing the published `latest_scan` report.
- A Worker hostname/route under a domain controlled by the owner.
- A long, unique `READ_TOKEN` (keep it private).
- Cloudflare account access for the deployment operator.

No value above is guessed or embedded in this repository. No paid plan or service is required by this code itself; check the current Cloudflare account limits/pricing before enabling any optional paid feature.

## Deploy from the repository root
1. Open the Cloudflare dashboard and identify the existing KV namespace that already receives the approved `latest_scan` report. Do not create a second namespace unless the publishing pipeline is deliberately configured to write to it.
2. Replace `REPLACE_WITH_EXISTING_KV_NAMESPACE_ID` in `private_sync_worker/wrangler.robotics-report.toml` with that exact namespace ID. Keep the binding name `ROBOTICS_REPORT_KV`.
3. From `private_sync_worker/`, authenticate Wrangler with the intended Cloudflare account and deploy using the config:
   ```sh
   npx wrangler login
   npx wrangler secret put READ_TOKEN --config wrangler.robotics-report.toml
   npx wrangler deploy --config wrangler.robotics-report.toml
   ```
   Use an already-installed Wrangler where possible; do not install or subscribe to a paid service without approval.
4. Record the deployed HTTPS Worker URL privately. Do not commit the token or any secret config.
5. Confirm the KV namespace contains a current, approved `latest_scan` report with `release_ready=true`, strategy `balanced-1.3-audit`, and a timestamp no older than 36 hours.

## Smoke checks
Replace the URL and token locally; do not paste the token into chat or commit it.
```sh
curl -i -H "Authorization: Bearer $READ_TOKEN" "$WORKER_URL/api/robotics/report"
curl -i -X PUT -H "Authorization: Bearer $READ_TOKEN" "$WORKER_URL/api/robotics/report"
```
Expected: first request returns HTTP 200 with the approved report; second returns HTTP 405. Also verify unauthenticated GET returns HTTP 401 and stale/non-release-ready reports are rejected with HTTP 503. Never use a fabricated report as evidence of live readiness.

## Android installation and acceptance
- Install the verified debug APK `AI-Robotics-Investor-0.1.231-debug.apk` on Motorola Edge 30 Fusion.
- In **Konfiguracja**, enter the deployed HTTPS Worker base URL and the dedicated read-only `READ_TOKEN`.
- Tap **Pobierz raport**. Acceptance requires the real current report to display and pass the app's release/strategy/timestamp checks.
- Confirm an invalid token is rejected and no write/trading capability is present.

## Security note
The current Android implementation stores the token in app-private SharedPreferences. Android app sandboxing applies, but this implementation does not encrypt the token with Android Keystore. Use a unique, least-privilege read token, protect the device, and rotate the token if the device is lost. Keystore-backed token storage should be completed before distributing the APK beyond the owner's test device.

## Current verified state (2026-11-11)
- Branch: `stage2-balanced-1.3.4`
- Build commit: `1ef3f9c94042360307c33db99a959523f623c52c`
- GitHub Actions run: `43017737668` — success; Worker tests, metadata check, debug build and APK checksum steps all succeeded.
- Artifact: `AI-Robotics-Investor-0.1.231-debug` (artifact ID `13853826259`).
- APK SHA-256: `07a77910dccf244ef0f6de65e236b91b6ac3cf2eeb9c54d562f76c9a18f26900`.
- Cloudflare deployment and physical-device acceptance: not performed; required owner credentials/configuration and device test are outstanding.
- `main` and the existing scanner are not changed by this Stage2 branch.

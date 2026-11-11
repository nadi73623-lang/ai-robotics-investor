import test from "node:test";
import assert from "node:assert/strict";
import worker, { validate } from "../private_sync_worker/robotics_report_worker.mjs";

const fresh = () => ({ release_ready: true, strategy_version: "balanced-1.3-audit", generated_at: new Date().toISOString(), companies: [] });
const env = (report = fresh()) => ({ READ_TOKEN: "test-read-token", ROBOTICS_REPORT_KV: { get: async key => { assert.equal(key, "latest_scan"); return JSON.stringify(report); } } });
const req = (method = "GET", token = "test-read-token") => new Request("https://worker.example/api/robotics/report", { method, headers: token ? { Authorization: "Bearer " + token } : {} });

test("serves fresh release-ready report to read token", async () => {
  const r = await worker.fetch(req(), env());
  assert.equal(r.status, 200);
  assert.equal((await r.json()).release_ready, true);
});
test("rejects missing or incorrect token", async () => {
  assert.equal((await worker.fetch(req("GET", ""), env())).status, 401);
  assert.equal((await worker.fetch(req("GET", "wrong"), env())).status, 401);
});
test("rejects write methods without touching KV", async () => {
  let reads = 0; const e = env(); e.ROBOTICS_REPORT_KV.get = async () => { reads++; return "{}"; };
  assert.equal((await worker.fetch(req("PUT"), e)).status, 405);
  assert.equal(reads, 0);
});
test("supports CORS preflight", async () => {
  const r = await worker.fetch(req("OPTIONS", ""));
  assert.equal(r.status, 204);
  assert.match(r.headers.get("access-control-allow-methods"), /GET/);
  assert.doesNotMatch(r.headers.get("access-control-allow-methods"), /PUT/);
});
test("blocks non-ready, wrong strategy, stale and future reports", () => {
  assert.equal(validate({ ...fresh(), release_ready: false }), "report_not_release_ready");
  assert.equal(validate({ ...fresh(), strategy_version: "other" }), "unsupported_strategy");
  assert.equal(validate({ ...fresh(), generated_at: new Date(Date.now() - 37*3600e3).toISOString() }), "report_stale_or_future");
  assert.equal(validate({ ...fresh(), generated_at: new Date(Date.now() + 60000).toISOString() }), "report_stale_or_future");
  assert.equal(validate({ ...fresh(), generated_at: "bad-date" }), "invalid_report_timestamp");
});
test("returns 503 when report missing", async () => {
  const e = { READ_TOKEN: "test-read-token", ROBOTICS_REPORT_KV: { get: async () => null } };
  assert.equal((await worker.fetch(req(), e)).status, 404);
});

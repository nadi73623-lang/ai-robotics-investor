const REPORT_KEY = "latest_scan";
const STRATEGY = "balanced-1.3-audit";
const MAX_AGE_MS = 36 * 60 * 60 * 1000;

function response(body, status, origin = "*", extra = {}) {
  return new Response(body, { status, headers: {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store, max-age=0",
    "access-control-allow-origin": origin,
    "access-control-allow-methods": "GET, HEAD, OPTIONS",
    "access-control-allow-headers": "Authorization, Content-Type",
    "vary": "Origin",
    "x-content-type-options": "nosniff",
    ...extra
  }});
}
function validate(report, now = Date.now()) {
  if (!report || typeof report !== "object" || Array.isArray(report)) return "invalid_report_shape";
  if (report.release_ready !== true) return "report_not_release_ready";
  const strategy = report.strategy_version || report.strategy;
  if (strategy !== STRATEGY) return "unsupported_strategy";
  const stamp = report.generated_at || report.generated_at_utc || report.created_at || report.as_of;
  if (typeof stamp !== "string" || !stamp) return "missing_report_timestamp";
  const time = Date.parse(stamp);
  if (!Number.isFinite(time)) return "invalid_report_timestamp";
  const age = now - time;
  if (age < 0 || age > MAX_AGE_MS) return "report_stale_or_future";
  return null;
}
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== "/api/robotics/report") return response(JSON.stringify({ error: "not_found" }), 404);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: {
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "GET, HEAD, OPTIONS",
      "access-control-allow-headers": "Authorization, Content-Type",
      "access-control-max-age": "600",
      "vary": "Origin"
    }});
    if (!["GET", "HEAD"].includes(request.method)) return response(JSON.stringify({ error: "method_not_allowed" }), 405, "*", { allow: "GET, HEAD, OPTIONS" });
    if (!env.READ_TOKEN || !env.ROBOTICS_REPORT_KV) return response(JSON.stringify({ error: "service_not_configured" }), 503);
    const supplied = request.headers.get("authorization") || "";
    if (supplied !== "Bearer " + env.READ_TOKEN) return response(JSON.stringify({ error: "unauthorized" }), 401, "*", { "www-authenticate": "Bearer" });
    try {
      const raw = await env.ROBOTICS_REPORT_KV.get(REPORT_KEY);
      if (!raw) return response(JSON.stringify({ error: "report_not_found" }), 404);
      if (raw.length > 1_500_000) return response(JSON.stringify({ error: "report_too_large" }), 413);
      let report;
      try { report = JSON.parse(raw); } catch { return response(JSON.stringify({ error: "invalid_report_json" }), 503); }
      const invalid = validate(report);
      if (invalid) return response(JSON.stringify({ error: invalid }), 503);
      const body = JSON.stringify(report);
      return new Response(request.method === "HEAD" ? null : body, { status: 200, headers: {
        "content-type": "application/json; charset=utf-8",
        "cache-control": "no-store, max-age=0",
        "access-control-allow-origin": "*",
        "vary": "Origin",
        "x-content-type-options": "nosniff",
        "content-length": String(new TextEncoder().encode(body).length)
      }});
    } catch {
      return response(JSON.stringify({ error: "report_read_failed" }), 503);
    }
  }
};
export { validate };

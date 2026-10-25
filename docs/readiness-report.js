(function (global) {
  "use strict";
  const DATA_SCHEMA = "client-readiness.v2";
  const REPORT_SCHEMA = "client-readiness-report.v1";
  const operators = new Set(["contains", "equals", "min_version", "cert_name_exists", "cert_expiry_days"]);
  function validateData(data) {
    if (!data || data.schema_version !== DATA_SCHEMA) throw new Error("Unsupported data schema; use the v2 helper or import a v2 report.");
    if (!data.meta || !Array.isArray(data.meta.capabilities) || !data.meta.capabilities.every(v => typeof v === "string")) throw new Error("Missing or invalid helper capabilities.");
    if (data.meta.collected_at != null && !Number.isFinite(Date.parse(data.meta.collected_at))) throw new Error("Invalid collection timestamp.");
    for (const item of Object.values(data.meta.collection_status || {})) {
      if (!item || !["OK", "ERROR", "UNSUPPORTED", "NOT_CHECKED"].includes(item.status)) throw new Error("Invalid collection status.");
    }
    return data;
  }
  function validateProfile(profile) {
    if (!profile || typeof profile.profile !== "string" || !Array.isArray(profile.checks) || !profile.checks.length) throw new Error("Invalid profile.");
    const ids = new Set();
    for (const r of profile.checks) {
      if (!r.id || ids.has(r.id) || !operators.has(r.operator) || typeof (r.evidence_field || r.source) !== "string") throw new Error("Invalid or duplicate profile rule.");
      ids.add(r.id);
      if (["contains", "equals", "min_version", "cert_name_exists"].includes(r.operator) && !Object.hasOwn(r, "expected")) throw new Error("Missing expected value in profile.");
      if (r.operator === "cert_expiry_days" && (typeof r.match !== "string" || !r.match)) throw new Error("Missing certificate match in profile.");
      if (r.operator === "min_version" && !/^\d+(\.\d+)*$/.test(String(r.expected))) throw new Error("Invalid minimum version in profile.");
    }
    return profile;
  }
  function freshness(data, now = new Date().toISOString()) {
    const stamp = data.meta?.collected_at;
    if (!stamp) return {unknown: true, stale: true, text: "Collection time unknown — freshness unverified"};
    const minutes = Math.floor((Date.parse(now) - Date.parse(stamp)) / 60000);
    return {unknown: false, stale: minutes > 15 || minutes < -1, text: minutes < -1 ? "Collection time is in the future" : `Collected ${Math.max(0, minutes)} min ago`};
  }
  function create(profile, data, source, evaluatedAt = new Date().toISOString()) {
    validateProfile(profile); validateData(data);
    if (typeof source !== "string" || !source) throw new Error("Missing report source.");
    if (!Number.isFinite(Date.parse(evaluatedAt))) throw new Error("Invalid evaluation timestamp.");
    const record = JSON.parse(JSON.stringify({schema_version: REPORT_SCHEMA, profile, data, source, evaluated_at: evaluatedAt}));
    Object.assign(record, global.ClientReadinessEvaluator.evaluateProfile(record.profile, record.data, {now: evaluatedAt}));
    // Keep the full profile snapshot, not only the evaluator's profile ID.
    record.profile = JSON.parse(JSON.stringify(profile));
    return record;
  }
  function parse(text) {
    const record = JSON.parse(text);
    if (record?.schema_version !== REPORT_SCHEMA) throw new Error("Unsupported report schema.");
    const result = create(record.profile, record.data, record.source, record.evaluated_at);
    result.redacted = record.redacted === true;
    return result;
  }
  function redact(report) {
    const clone = JSON.parse(JSON.stringify(report));
    const sensitiveKeys = new Set(["hostname", "local_ips", "path", "subject", "issuer", "thumbprint", "system_profiler", "sc_auth_list"]);
    function clean(value) {
      if (Array.isArray(value)) return value.map(clean);
      if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, sensitiveKeys.has(key) ? (Array.isArray(item) ? [] : "[redacted]") : clean(item)]));
      return value;
    }
    const safe = create(clone.profile, clean(clone.data), clone.source, clone.evaluated_at);
    safe.redacted = true;
    return safe;
  }
  function summary(report) {
    const s = report.summary;
    return [`Client readiness: ${report.profile.profile}`, `Source: ${report.source}; evaluated: ${report.evaluated_at}`, `PASS ${s.passed} | FAIL ${s.failed} | WARN ${s.warnings} | UNSUPPORTED ${s.unsupported} | NOT_CHECKED ${s.not_checked} | ERROR ${s.errors}`, ...report.results.filter(r => r.status !== "PASS").map(r => `${r.id}: ${r.status} — ${r.evidence}. ${r.remediation}`)].join("\n");
  }
  function html(report) {
    const escape = v => String(v ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
    const rows = report.results.map(r => `<tr>${[r.id, r.title, r.status, r.evidence, r.remediation].map(v => `<td>${escape(v)}</td>`).join("")}</tr>`).join("");
    return `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Client readiness report</title><style>body{font:16px system-ui;margin:2rem}table{border-collapse:collapse}td,th{border:1px solid #aaa;padding:.6rem;text-align:left}pre{white-space:pre-wrap}</style><h1>Client readiness report</h1><pre>${escape(summary(report))}</pre><p>${escape(freshness(report.data).text)}. Masked: ${report.redacted === true}</p><table><thead><tr><th>ID</th><th>Check</th><th>Status</th><th>Evidence</th><th>Remediation</th></tr></thead><tbody>${rows}</tbody></table></html>`;
  }
  global.ClientReadinessReport = {validateData, validateProfile, freshness, create, parse, redact, summary, html};
})(window);

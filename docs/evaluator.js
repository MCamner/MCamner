(function (global) {
  "use strict";

  function normalizeArray(value) {
    if (Array.isArray(value)) return value;
    if (value === undefined || value === null) return [];
    return [value];
  }

  function getByPath(obj, path) {
    if (!obj || !path) return undefined;
    return path.split(".").reduce((acc, key) => {
      if (acc && Object.prototype.hasOwnProperty.call(acc, key)) {
        return acc[key];
      }
      return undefined;
    }, obj);
  }

  function compareContains(actual, expected) {
    const actualArr = normalizeArray(actual).map(String);
    const expectedArr = normalizeArray(expected).map(String);

    const missing = expectedArr.filter((item) => !actualArr.includes(item));

    return {
      ok: missing.length === 0,
      actual: actualArr,
      expected: expectedArr,
      detail: missing.length === 0
        ? "All expected values found"
        : "Missing: " + missing.join(", ")
    };
  }

  function compareEquals(actual, expected) {
    const ok = String(actual) === String(expected);
    return {
      ok,
      actual,
      expected,
      detail: ok
        ? "Actual value matches expected"
        : `Expected "${expected}" but got "${actual}"`
    };
  }

  function compareMinVersion(actual, expected) {
    const a = String(actual || "").split(".").map(Number);
    const e = String(expected || "").split(".").map(Number);
    const len = Math.max(a.length, e.length);

    for (let i = 0; i < len; i++) {
      const av = a[i] || 0;
      const ev = e[i] || 0;
      if (av > ev) return { ok: true, actual, expected, detail: "Version OK" };
      if (av < ev) return { ok: false, actual, expected, detail: "Version too low" };
    }

    return { ok: true, actual, expected, detail: "Version OK" };
  }

  function compareCertNameExists(actual, expected) {
    const certs = Array.isArray(actual) ? actual : [];
    const wanted = String(expected || "").toLowerCase();

    const match = certs.find((c) =>
      String(c.name || "").toLowerCase().includes(wanted)
    );

    return {
      ok: Boolean(match),
      actual: match || null,
      expected,
      detail: match
        ? `Found certificate: ${match.name}`
        : `Certificate not found: ${expected}`
    };
  }

  function parseDate(str) {
    if (!str) return null;
    const d = new Date(str);
    return isNaN(d.getTime()) ? null : d;
  }

  function compareCertExpiry(actual, rule) {
    const certs = Array.isArray(actual) ? actual : [];
    const name = String(rule.match || "").toLowerCase();
    const warnDays = rule.warn_days || 30;
    const failDays = rule.fail_days || 0;

    const cert = certs.find((c) =>
      String(c.name || "").toLowerCase().includes(name)
    );

    if (!cert) {
      return {
        ok: false,
        status: "FAIL",
        detail: `Certificate not found: ${rule.match}`
      };
    }

    const expiry = parseDate(cert.not_after);

    if (!expiry) {
      return {
        ok: false,
        status: "FAIL",
        detail: "Invalid or missing expiry date"
      };
    }

    const now = new Date();
    const diffDays = Math.floor((expiry - now) / (1000 * 60 * 60 * 24));

    if (diffDays < failDays) {
      return {
        ok: false,
        status: "FAIL",
        detail: `Expired ${Math.abs(diffDays)} days ago`
      };
    }

    if (diffDays <= warnDays) {
      return {
        ok: true,
        status: "WARN",
        detail: `Expires in ${diffDays} days`
      };
    }

    return {
      ok: true,
      status: "PASS",
      detail: `Valid (${diffDays} days remaining)`
    };
  }

  function evaluateRule(rule, data) {
    const sourceValue = getByPath(data, rule.source);
    let result;

    switch (rule.operator) {
      case "contains":
        result = compareContains(sourceValue, rule.expected);
        break;
      case "equals":
        result = compareEquals(sourceValue, rule.expected);
        break;
      case "min_version":
        result = compareMinVersion(sourceValue, rule.expected);
        break;
      case "cert_name_exists":
        result = compareCertNameExists(sourceValue, rule.expected);
        break;
      case "cert_expiry_days":
        result = compareCertExpiry(sourceValue, rule);
        break;
      default:
        result = {
          ok: false,
          detail: "Unsupported operator"
        };
    }

    const status = result.status || (result.ok ? "PASS" : "FAIL");

    return {
      id: rule.id,
      title: rule.title,
      severity: rule.severity || "medium",
      status,
      expected: rule.expected || rule.match,
      actual: result.actual || null,
      evidence: result.detail,
      remediation: rule.remediation || "",
      timestamp: new Date().toISOString()
    };
  }

  function evaluateProfile(profile, data) {
    const results = profile.checks.map((rule) =>
      evaluateRule(rule, data)
    );

    const summary = {
      total: results.length,
      passed: results.filter(r => r.status === "PASS").length,
      failed: results.filter(r => r.status === "FAIL").length,
      warnings: results.filter(r => r.status === "WARN").length
    };

    return {
      summary,
      results
    };
  }

  global.ClientReadinessEvaluator = {
    evaluateProfile
  };
})(window);

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

    for (let i = 0; i < len; i += 1) {
      const av = a[i] || 0;
      const ev = e[i] || 0;
      if (av > ev) {
        return {
          ok: true,
          actual,
          expected,
          detail: `Version ${actual} satisfies minimum ${expected}`
        };
      }
      if (av < ev) {
        return {
          ok: false,
          actual,
          expected,
          detail: `Version ${actual} is below minimum ${expected}`
        };
      }
    }

    return {
      ok: true,
      actual,
      expected,
      detail: `Version ${actual} satisfies minimum ${expected}`
    };
  }

  function compareCertNameExists(actual, expected) {
    const certs = Array.isArray(actual) ? actual : [];
    const wanted = String(expected || "").toLowerCase();

    const match = certs.find((cert) => {
      const name = String((cert && cert.name) || "").toLowerCase();
      return name === wanted || name.includes(wanted);
    });

    return {
      ok: Boolean(match),
      actual: match || null,
      expected,
      detail: match
        ? `Found certificate: ${match.name || expected}`
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

  function hasCapability(data, requiredCapability) {
    if (!requiredCapability) return true;
    const capabilities = getByPath(data, "meta.capabilities");
    return Array.isArray(capabilities) && capabilities.includes(requiredCapability);
  }

  function evaluateRule(rule, data) {
    if (!hasCapability(data, rule.required_capability)) {
      return {
        id: rule.id,
        title: rule.title,
        category: rule.category || "general",
        severity: rule.severity || "medium",
        status: "UNSUPPORTED",
        expected: rule.expected || rule.match || null,
        actual: null,
        evidence: `Missing helper capability: ${rule.required_capability}`,
        remediation: rule.remediation || "",
        source: rule.source || "",
        timestamp: new Date().toISOString()
      };
    }

    const sourceValue = getByPath(data, rule.evidence_field || rule.source);
    let comparison;

    switch (rule.operator) {
      case "contains":
        comparison = compareContains(sourceValue, rule.expected);
        break;
      case "equals":
        comparison = compareEquals(sourceValue, rule.expected);
        break;
      case "min_version":
        comparison = compareMinVersion(sourceValue, rule.expected);
        break;
      case "cert_name_exists":
        comparison = compareCertNameExists(sourceValue, rule.expected);
        break;
      case "cert_expiry_days":
        comparison = compareCertExpiry(sourceValue, rule);
        break;
      default:
        comparison = {
          ok: false,
          actual: sourceValue,
          expected: rule.expected,
          detail: `Unsupported operator: ${rule.operator}`
        };
    }

    const status = comparison.status || (comparison.ok ? "PASS" : "FAIL");

    return {
      id: rule.id,
      title: rule.title,
      category: rule.category || "general",
      severity: rule.severity || "medium",
      status,
      expected: comparison.expected,
      actual: comparison.actual,
      evidence: comparison.detail,
      remediation: rule.remediation || "",
      source: rule.source || rule.evidence_field || "",
      timestamp: new Date().toISOString()
    };
  }

  function evaluateProfile(profile, data) {
    const checks = Array.isArray(profile.checks) ? profile.checks : [];
    const results = checks.map((rule) => evaluateRule(rule, data));

    const summary = {
      total: results.length,
      passed: results.filter((r) => r.status === "PASS").length,
      failed: results.filter((r) => r.status === "FAIL").length,
      warnings: results.filter((r) => r.status === "WARN").length,
      unsupported: results.filter((r) => r.status === "UNSUPPORTED").length,
      critical_failed: results.filter(
        (r) => r.status === "FAIL" && r.severity === "critical"
      ).length
    };

    return {
      profile: profile.profile || "unknown",
      summary,
      results
    };
  }

  global.ClientReadinessEvaluator = {
    evaluateRule,
    evaluateProfile
  };
})(window);

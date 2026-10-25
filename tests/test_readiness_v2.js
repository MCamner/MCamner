const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ctx = {window: {}};
vm.runInNewContext(fs.readFileSync('docs/evaluator.js', 'utf8'), ctx);
const e = ctx.window.ClientReadinessEvaluator;
const rule = {id: 'version', source: 'citrix.version', operator: 'min_version', expected: '23.11.0'};
test('missing and malformed observations are not client failures or passes', () => {
  assert.equal(e.evaluateRule(rule, {}).status, 'NOT_CHECKED');
  assert.equal(e.evaluateRule(rule, {citrix: {version: '23.11.invalid'}}).status, 'NOT_CHECKED');
  assert.equal(e.evaluateRule(rule, {citrix: {version: '23.11.1'}}).status, 'PASS');
});
test('collection failure stays ERROR', () => {
  assert.equal(e.evaluateRule(rule, {meta: {collection_status: {citrix: {status: 'ERROR', detail: 'timeout'}}}}).status, 'ERROR');
});
test('unsupported capability remains distinct', () => {
  assert.equal(e.evaluateRule({...rule, required_capability: 'citrix.version'}, {meta: {capabilities: []}}).status, 'UNSUPPORTED');
});
test('certificate validity requires actual expiry evidence and a controlled clock', () => {
  const r = {id: 'cert', source: 'certificates.details', operator: 'cert_expiry_days', match: 'Demo CA', warn_days: 30};
  assert.equal(e.evaluateRule(r, {certificates: {details: [{name: 'Demo CA'}]}}).status, 'NOT_CHECKED');
  assert.equal(e.evaluateRule(r, {certificates: {details: [{name: 'Demo CA', not_after: '2026-01-02T00:00:00Z'}]}}, {now: '2026-01-02T00:00:00Z'}).status, 'FAIL');
});
vm.runInNewContext(fs.readFileSync('docs/readiness-report.js', 'utf8'), ctx);
const reports = ctx.window.ClientReadinessReport;
const data = {schema_version: 'client-readiness.v2', meta: {collected_at: '2026-01-01T00:00:00Z', capabilities: ['citrix.version'], hostname: 'private-host'}, citrix: {version: '23.11.1'}, network: {local_ips: ['10.0.0.2']}};
const profile = {profile: 'test', checks: [rule]};
test('reject legacy and malformed inputs, but accept supported measurement', () => {
  assert.throws(() => reports.validateData({agent: {version: '0.4'}}), /schema/);
  assert.throws(() => reports.validateData({...data, meta: {}}), /capabilities/);
  assert.throws(() => reports.validateData({...data, meta: {...data.meta, collected_at: 'bad'}}), /timestamp/);
  assert.equal(reports.validateData(data), data);
});
test('report round trip preserves evaluation and does not mutate original', () => {
  const report = reports.create(profile, data, 'live-helper', '2026-01-01T12:00:00Z');
  const loaded = reports.parse(JSON.stringify(report));
  assert.equal(JSON.stringify(loaded.results), JSON.stringify(report.results));
  assert.equal(loaded.profile.profile, 'test');
  assert.equal(data.meta.hostname, 'private-host');
  const safe = reports.redact(report);
  assert.ok(!JSON.stringify(safe).includes('private-host'));
  assert.ok(!JSON.stringify(safe).includes('10.0.0.2'));
  assert.equal(safe.redacted, true);
  assert.equal(reports.parse(JSON.stringify(safe)).results[0].status, 'PASS');
});
test('import recalculates results rather than trusting report claims', () => {
  const report = reports.create(profile, data, 'sample-data', '2026-01-01T12:00:00Z');
  report.results[0].status = 'FAIL';
  assert.equal(reports.parse(JSON.stringify(report)).results[0].status, 'PASS');
  assert.equal(reports.freshness(data, '2026-01-02T00:00:00Z').stale, true);
  assert.equal(reports.freshness({...data, meta: {...data.meta, collected_at: null}}).unknown, true);
});
test('profiles and shipped measurements satisfy the contract', () => {
  const index = JSON.parse(fs.readFileSync('docs/profiles/index.json'));
  for (const p of index.profiles) reports.validateProfile(JSON.parse(fs.readFileSync('docs/' + p.path)));
  for (const name of ['sample-client-data.json', 'live-client-data.json']) reports.validateData(JSON.parse(fs.readFileSync('docs/' + name)));
});
test('standalone HTML escapes untrusted report content', () => {
  const report = reports.create({...profile, checks:[{...rule, title:'<script>alert(1)</script>'}]}, data, 'imported');
  const html = reports.html(report);
  assert.ok(!html.includes('<script>'));
  assert.ok(html.includes('&lt;script&gt;'));
});

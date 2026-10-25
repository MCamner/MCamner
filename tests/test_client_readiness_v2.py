import subprocess

from helper import client_readiness_agent_v2 as agent


def test_capabilities_do_not_claim_macos_collectors_on_linux(monkeypatch):
    monkeypatch.setattr(agent.platform, 'system', lambda: 'Linux')
    monkeypatch.setattr(agent, 'command_exists', lambda name: False)
    capabilities = agent.collect_capabilities()
    assert 'certificates.details' not in capabilities
    assert 'citrix.version' not in capabilities
    assert 'smartcard.readers' not in capabilities


def test_command_failures_remain_visible(monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired('example', 1)
    monkeypatch.setattr(agent.subprocess, 'run', timeout)
    try:
        agent.run_command(['example'])
    except agent.CollectionError:
        pass
    else:
        raise AssertionError('command failure was hidden')


def test_payload_contains_schema_time_and_collection_errors(monkeypatch):
    monkeypatch.setattr(agent, 'collect_capabilities', lambda: ['network.online'])
    for name in ('network', 'certificates', 'citrix', 'smartcard', 'processes'):
        monkeypatch.setattr(agent, 'collect_' + name, lambda: {})
    def fail():
        raise agent.CollectionError('command timed out')
    monkeypatch.setattr(agent, 'collect_network', fail)
    payload = agent.build_payload('kiosk')
    assert payload['schema_version'] == 'client-readiness.v2'
    assert payload['meta']['collected_at'].endswith('+00:00')
    assert payload['meta']['collection_status']['network']['status'] == 'ERROR'
    assert payload['network'] == {}


def test_keychain_metadata_is_not_certificate_validity():
    text = 'SHA-1 hash: ' + 'a' * 40 + '\n    "labl"<blob>="Demo CA"\n    "mdat"<timedate>="20250101000000Z"'
    cert = agent._parse_security_certificate_text(text, 'test')[0]
    assert cert['name'] == 'Demo CA'
    assert 'not_after' not in cert


def test_v2_status_endpoint_and_origin_policy(monkeypatch):
    import json
    import threading
    import urllib.error
    import urllib.request
    from http.server import ThreadingHTTPServer

    payload = {'schema_version': 'client-readiness.v2', 'meta': {'capabilities': []}}
    monkeypatch.setattr(agent, 'build_payload', lambda profile: {**payload, 'profile': profile})
    server = ThreadingHTTPServer(('127.0.0.1', 0), agent.make_handler('kiosk', ['http://localhost:8000']))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = 'http://127.0.0.1:%s' % server.server_port
    try:
        req = urllib.request.Request(base + '/status', headers={'Origin': 'http://localhost:8000'})
        with urllib.request.urlopen(req, timeout=3) as response:
            assert response.headers['Access-Control-Allow-Origin'] == 'http://localhost:8000'
            body = json.load(response)
            assert body['schema_version'] == 'client-readiness.v2'
            assert body['profile'] == 'kiosk'
        req = urllib.request.Request(base + '/status', headers={'Origin': 'https://untrusted.example'})
        try:
            urllib.request.urlopen(req, timeout=3)
        except urllib.error.HTTPError as error:
            assert error.code == 403
        else:
            raise AssertionError('Unexpected origin accepted')
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_helper_payload_reaches_browser_evaluator(monkeypatch):
    import json
    from pathlib import Path

    monkeypatch.setattr(agent, 'collect_capabilities', lambda: ['citrix.installed', 'citrix.version'])
    monkeypatch.setattr(agent, 'collect_citrix', lambda: {'installed': True, 'version': '23.11.1'})
    payload = agent.build_payload('test')
    script = '''
const fs = require('fs'), vm = require('vm');
const ctx = {window: {}};
for (const name of ['evaluator.js', 'readiness-report.js']) vm.runInNewContext(fs.readFileSync('docs/' + name, 'utf8'), ctx);
const data = ctx.window.ClientReadinessReport.validateData(JSON.parse(fs.readFileSync(0, 'utf8')));
const output = ctx.window.ClientReadinessEvaluator.evaluateProfile({profile:'test', checks:[
  {id:'citrix', source:'citrix.version', required_capability:'citrix.version', operator:'min_version', expected:'23.11.0'}
]}, data);
if (output.summary.passed !== 1) throw new Error(JSON.stringify(output));
'''
    subprocess.run(['node', '-e', script], input=json.dumps(payload), text=True,
                   cwd=Path(__file__).resolve().parents[1], check=True, timeout=10)

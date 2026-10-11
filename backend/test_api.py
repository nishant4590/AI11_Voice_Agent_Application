from fastapi.testclient import TestClient
from backend.main import app


def test_tool_requires_backend_identity(monkeypatch):
    monkeypatch.setenv('DEMO_TOKEN', 'test-local-only-token')
    with TestClient(app) as client:
        assert client.post('/api/tool', json={'name':'get_order_status','order_id':'ORD-9182'}).status_code == 401
        headers={'Authorization':'Bearer test-local-only-token'}
        denied=client.post('/api/tool',headers=headers,json={'name':'request_cancellation','order_id':'ORD-7710'})
        assert 'error' in denied.json()['result']
        forged=client.post('/api/tool',headers=headers,json={'name':'get_order_status','order_id':'ORD-9182','user_id':'other-customer'})
        assert forged.status_code == 422
        malformed=client.post('/api/tool',headers=headers,json={'name':'get_order_status','order_id':'not-an-order'})
        assert malformed.status_code == 422


def test_live_voice_fails_clearly_without_key(monkeypatch):
    monkeypatch.setenv('DEMO_TOKEN', 'test-local-only-token')
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    with TestClient(app) as client:
        r=client.post('/api/session',headers={'Authorization':'Bearer test-local-only-token','Content-Type':'application/sdp'},content='v=0')
        assert r.status_code == 503


def test_provider_sdp_contract(monkeypatch):
    import json
    import httpx
    import backend.main as main
    monkeypatch.setenv("DEMO_TOKEN", "local-test-token")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-test-key")
    monkeypatch.setenv("REALTIME_MODEL", "gpt-realtime-2.1")
    requests = []
    async def handler(request):
        requests.append(request)
        return httpx.Response(201, text="v=0\r\nmock-answer")
    real_client = httpx.AsyncClient
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs:
                        real_client(transport=httpx.MockTransport(handler), **kwargs))
    with TestClient(app) as client:
        response = client.post("/api/session", content="v=0\r\nmock-offer",
                  headers={"Authorization": "Bearer local-test-token", "Content-Type": "application/sdp"})
    assert response.status_code == 200
    assert response.text == "v=0\r\nmock-answer"
    request = requests[0]
    assert str(request.url) == "https://api.openai.com/v1/realtime/calls"
    assert request.headers["authorization"] == "Bearer fake-test-key"
    body = request.content.decode()
    assert 'name="sdp"' in body and 'name="session"' in body
    assert "gpt-realtime-2.1" in body and "get_order_status" in body


def test_provider_errors_and_invalid_input(monkeypatch, caplog):
    import httpx
    import backend.main as main
    monkeypatch.setenv("DEMO_TOKEN", "local-test-token")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-test-key")
    real_client = httpx.AsyncClient
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs:
        real_client(transport=httpx.MockTransport(lambda request:
            httpx.Response(401, json={"error": {"message": "private-provider-message",
                                                  "type": "invalid_request_error",
                                                  "code": "invalid_model", "param": "model"}},
                           headers={"x-request-id": "req-test"})), **kwargs))
    headers = {"Authorization": "Bearer local-test-token"}
    with TestClient(app) as client:
        assert client.post("/api/session", headers=headers, content=b"\xff").status_code == 400
        assert client.post("/api/session", headers=headers, content="not sdp").status_code == 400
        assert client.post("/api/session", headers=headers, content="v=0" + "x"*100000).status_code == 413
        response = client.post("/api/session", headers=headers, content="v=0")
        assert response.status_code == 502
        assert "private-provider-message" not in response.text
    assert "status=401" in caplog.text
    assert "request_id=req-test" in caplog.text
    assert "error_code=invalid_model" in caplog.text
    assert "private-provider-message" in caplog.text


def test_provider_credit_exhaustion_returns_actionable_error(monkeypatch):
    import httpx
    import backend.main as main
    monkeypatch.setenv("DEMO_TOKEN", "local-test-token")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-test-key")
    real_client = httpx.AsyncClient
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs:
        real_client(transport=httpx.MockTransport(lambda request:
            httpx.Response(429, json={"error": {"message": "No credits remaining",
                                                  "code": "credit_balance_exhausted"}})), **kwargs))
    headers = {"Authorization": "Bearer local-test-token", "Content-Type": "application/sdp"}
    with TestClient(app) as client:
        response = client.post("/api/session", headers=headers, content="v=0")
    assert response.status_code == 429
    assert "credits are exhausted" in response.json()["detail"]

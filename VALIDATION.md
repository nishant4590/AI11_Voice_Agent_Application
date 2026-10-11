# Validation — 11 October 2026

- Python 3.12: `python -m pytest backend -q` → **8 passed**.
- Tests cover ownership denial, confirmation identity binding, expiry and single use, API authentication, argument validation, missing key, malformed/oversized SDP, multipart provider request and sanitized provider rejection.
- Provider contract tests use httpx.MockTransport: no real API calls, keys or charges.
- Node 22.9.0: `npm run build` → success with Vite 7.3.7; Vite warns this Node release is below its supported minimum of 22.12.0.
- Python source parses successfully.
- One test-environment deprecation warning: Starlette's httpx TestClient adapter. Tests passed; this does not affect the runtime WebRTC relay.
- Exact Python test environment in backend/requirements-tested.txt; React package-lock.json is included.

## Not verified here

Live OpenAI session creation, model access/billing, browser microphone/audio, interruption behavior, actual model tool selection and end-to-end latency require testing on your machine with your own API key. Backend tests and a production build do not establish those behaviors.

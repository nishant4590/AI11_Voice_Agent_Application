# AI11 — Voice Agent Challenge Lab

The **voice-agent application** for @AspyroNishant's architecture series: React microphone → OpenAI Realtime over WebRTC → tool request → Python authorization and fictional order data → spoken answer.

This repository contains application code only. No video rendering code, recordings or API keys are included.

## Requirements

- Python 3.11+.
- Node.js 20.19+ or 22.12+.
- Chrome or Edge recommended for the live demo; localhost microphone permission and headphones.
- For live voice: your OpenAI API key, API billing and access to the configured Realtime model. A ChatGPT subscription does not cover API calls.

## Start Python — terminal 1

Run from the extracted repository root:

```bash
python -m venv .venv
```

Activate on macOS/Linux:

```bash
source .venv/bin/activate
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Then:

```bash
python -m pip install -r backend/requirements.txt
```

Copy `.env.example` to `.env` (`cp .env.example .env` on macOS/Linux; `Copy-Item .env.example .env` in PowerShell). Set a long random `DEMO_TOKEN`. Generate one with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

For live voice, also set `OPENAI_API_KEY` in `.env`. Leave the key blank for the simulated tool-flow test. Keep `REALTIME_MODEL=gpt-realtime-2.1` or select a Realtime model available to your API project. Never place your OpenAI key in React or commit `.env`.

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

## Start React — terminal 2

```bash
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173 and enter your **DEMO_TOKEN**, not your OpenAI API key. Vite forwards `/api` to Python on port 8000.

## Test without an API key

Use the three buttons in **Test the Python tool flow**:

1. Lookup ORD-9182 → processing, delivery Monday.
2. Try another account → unavailable; ORD-7710 belongs to another demo customer.
3. Request cancellation → pending; the order remains processing until you click **Confirm cancellation**.
4. Enable **Add 4s tool delay** → observe the measured Python tool time.

This mode simulates tool requests and uses the real local Python service. It does not simulate a live AI conversation or generated voice.

## Test real voice with your key

Click **Start voice**, grant microphone permission and speak:

- “Where is my order? The ID is O R D, nine one eight two.”
- “Wait, tell me that more briefly.” — interrupt while the agent is speaking.
- “Cancel order O R D, seven seven one zero.” — expect account denial.
- “Cancel order O R D, nine one eight two.” — expect confirmation before a state change.

The event log displays tool arguments, returned data, tool duration and agent transcript. The reported milliseconds measure the Python tool call only; they are not full speech-to-speech latency. **Stop & release mic** closes the peer connection and releases microphone tracks. Restart Python to reset the fictional orders; use one worker for this in-memory demo.

## Architecture and files

| File | Responsibility |
|---|---|
| frontend/src/main.jsx | Microphone, WebRTC audio, event handling, tool forwarding and confirmation UI |
| frontend/vite.config.js | Local backend proxy |
| backend/main.py | Authentication, SDP relay, allowlisted tools, argument validation |
| backend/service.py | Fictional order ownership and single-use expiring confirmation |
| backend/test_*.py | Backend behavior and mocked provider contract tests |
| DEMO_GUIDE.md | Practical next-video demo sequence |

The server sends SDP plus session configuration to `/v1/realtime/calls`. The OpenAI API key stays on Python. Model function calls are forwarded from the browser to authenticated Python. Tool results return as `function_call_output`, followed by `response.create`.

## Tests

```bash
python -m pytest backend -q
cd frontend
npm run build
```

See VALIDATION.md for the actual checks completed. Live microphone/model testing requires your key and is separate from mocked API tests.

## Troubleshooting

- 401 from Python: enter the exact DEMO_TOKEN saved in `.env`, then restart Python after edits.
- 503: no OpenAI key is configured; simulated tool buttons still work.
- 429 with an exhausted-credit message: the API organization associated with `OPENAI_API_KEY` has no API credits. Add credits or enable billing for that organization; rotating `DEMO_TOKEN` does not affect API billing. A ChatGPT subscription is separate.
- 502: the Python server reached the voice provider, but it rejected the session. Check the Python terminal for the provider HTTP status, error code, message and request ID; then verify API billing, key permissions and access to the configured Realtime model. The detailed provider error is logged server-side only, not returned to the browser.
- No microphone: grant permission; use localhost or HTTPS and check your input device.
- No agent sound: click the audio controls; check speakers/headphones and system volume.
- Connection interrupted: Stop, then Start voice again.
- Cancellation already occurred: restart Python to reset state.

## Demo boundaries

Local demonstration only: fixed backend identity, shared local bearer token, in-memory fictional orders and browser tool orchestration. No real orders, phone calls, database, durable audit trail, rate limiting or deployment authentication. Do not expose this server publicly as-is. Production needs trusted server-side tool orchestration and confirmation-result reporting, per-user authentication, persistence, turn relevance and operation idempotency. Stopping speech does not roll back an already-running tool. Voice responses and interruption behavior must be verified in the actual browser.

## Put in Git

`.env`, virtual environments, installed packages and build output are excluded by `.gitignore`. Keep API keys and real tokens out of commits; commit `.env.example` only.

```bash
git init
git add .
git commit -m "Add voice agent application demo"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

No remote repository has been created or published by this package.

## Official API references checked 11 October 2026

- https://developers.openai.com/api/docs/guides/voice-webrtc
- https://developers.openai.com/api/docs/guides/realtime-conversations

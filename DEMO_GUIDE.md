# Next video: practical voice-agent experience

## Before recording

Start Python and React using README.md. Use headphones and a quiet room. Keep the event log visible beside the audio controls. Set your API key privately before sharing your screen; do not show `.env`, credentials or developer network headers. Restart Python to reset orders. Test microphone, agent playback and interruption once before recording.

## Suggested 8–10 minute flow

| Time | What to say/show | Evidence |
|---|---|---|
| 0:00–0:30 | “Can a voice agent check an order without guessing—and refuse an order that is not mine?” Ask for ORD-9182 live. | Real spoken answer and Python tool result |
| 0:30–0:50 | “Welcome to my channel, @AspyroNishant. Last time we traced the architecture. Today we test the actual app.” | App open; distinguish real session from conceptual walkthrough |
| 0:50–2:00 | Show browser → realtime audio → function call → Python → order data → answer. | App log next to source snippets |
| 2:00–3:15 | Ask lookup again and point to the returned processing/Monday facts. | get_order_status arguments and result |
| 3:15–4:00 | Interrupt an answer: “Wait, make that shorter.” | speech_started event and observed playback; explain if interruption fails |
| 4:00–5:15 | Request ORD-7710, another account's order. | Python denial; do not claim the prompt alone enforces permissions |
| 5:15–6:30 | Request cancellation of ORD-9182; show pending; click explicit confirmation. | State changes only after confirmation; lookup returns cancelled |
| 6:30–7:30 | Enable 4-second delay, then ask for the owned order. | Measured tool_ms; clarify this is not total voice latency |
| 7:30–8:30 | Show setup and test commands. Mention the no-key simulated tool buttons. | README and passing backend tests |
| Final 15s | “Try the repository. Which failed first: interruption, tool latency, or order-ID recognition? Comment with your result, and like and subscribe for the next practical build.” | App and channel CTA |

## Useful code highlights

1. `getUserMedia` and `addTrack` in frontend/src/main.jsx.
2. SDP/session multipart relay in backend/main.py.
3. Tool schema and request validation in backend/main.py.
4. Ownership check and pending confirmation in backend/service.py.
5. `function_call_output` and `response.create` in frontend/src/main.jsx.

Record actual results. If the model mishears an ID, repeat it or ask it to confirm; that is useful demo evidence. Do not narrate successful behavior over a failed attempt. Explain that all orders are fictional and the API voice is synthetic.

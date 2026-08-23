# NORBEAI — AI Front Desk

> **Voice receptionist widget** — answers every call in a natural cloned voice,
> books appointments, answers FAQs, and never puts a caller on hold.

Powered by Coqui XTTS-v2 (TTS), faster-whisper (STT), and Ollama (LLM brain).

This repo contains:

- `frontend/` — React + Vite branded landing page with an embedded voice chat widget
- `backend/` — Python FastAPI server powering voice synthesis, transcription, and the LLM chat brain

Everything runs locally on your machine. No third-party API keys ever touch the frontend.

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python      | 3.12.x (3.10+ minimum, **not** 3.14+) | [python.org](https://python.org/downloads) |
| Node.js     | 20+ | [nodejs.org](https://nodejs.org) |
| Ollama      | latest | [ollama.com](https://ollama.com) — runs the LLM chat brain |
| ffmpeg      | any recent | **Linux:** `apt install ffmpeg` · **macOS:** `brew install ffmpeg` · **Windows:** [ffmpeg.org](https://ffmpeg.org/download.html) (add to PATH) |

### Install and pull the LLM model

```bash
# 1. Install Ollama (see ollama.com for platform-specific instructions)

# 2. Start the Ollama server (runs as a background service on macOS/Windows)
ollama serve

# 3. Pull the default lightweight model (~ 1.6 GB download)
ollama pull gemma2:2b
```

> **Note:** The first pull takes a minute or two. Subsequent starts are instant.
> If you skip this step the widget falls back to keyword-matched local answers
> (kb.js) — the voice still works, just without the LLM brain.

---

## Backend setup

```bash
cd backend

# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
#    Windows PowerShell:   .\.venv\Scripts\Activate.ps1
#    macOS / Linux:        source .venv/bin/activate

# 3. Install CPU PyTorch first (≈ 200 MB — skip if you have CUDA torch already)
pip install -r requirements-cpu.txt

# 4. Install the rest
pip install -r requirements.txt

# 5. Copy and edit environment config
cp ../.env.example ../.env
#     (defaults work out of the box for localhost dev)

# 6. Generate FAQ audio cache (recommended — eliminates ~16s TTS latency for FAQ answers)
python generate_faq_audio.py

# 7. Run the server
uvicorn main:app --reload --port 8000
```

The server starts at **http://localhost:8000**.

On first run it will:

- **Seed two demo voices** (Aditya & Priya) by downloading two short reference
  clips from a public HuggingFace space (~ 2 MB total). This only happens once;
  the files are stored in `backend/voices/` and reused on subsequent starts.
- **Log FAQ audio cache status** — prints how many pre-generated WAVs are
  available per industry (e.g. `FAQ audio cache: 50/50 WAVs ready`).
  If you see `0/50`, run `python generate_faq_audio.py` to pre-generate them.
- **Download the XTTS-v2 model** (~ 1.9 GB) on first `/synthesize` request.
  Cached in `~/.local/share/tts/` (Linux), `~/Library/Application Support/tts/`
  (macOS), or `%LOCALAPPDATA%\tts\` (Windows).
- **Download the Whisper STT model** (~ 500 MB for `small`) on first `/transcribe`
  request. Cached in `~/.cache/huggingface/`.
- **Check Ollama** for the configured model. If unavailable, all chat requests
  fall back to keyword-matched local answers.

All model downloads happen over HTTPS from HuggingFace and are fully local after
the first run. No API keys are required.

### Backend API

| Endpoint | Method | Body / Query | Returns |
|----------|--------|--------------|---------|
| `/health` | GET | — | `{"status": "ok"}` |
| `/health/ollama` | GET | — | `{"status": "ok", "model": "gemma2:2b"}` or error |
| `/voices` | GET | — | `[{"id","display_name","source","created_at"}, ...]` |
| `/voices/{voice_id}` | PATCH | `{"display_name": "New Name"}` | `{"id","display_name","source"}` |
| `/voices/{voice_id}` | DELETE | — | `{"status": "deleted", "id": "..."}` |
| `/synthesize` | POST | `{"text": "…", "voice_id": "aditya", "language": "en"}` | WAV audio (`audio/wav`) |
| `/transcribe` | POST | `multipart/form-data` field `file` (wav/mp3/webm) | `{"text": "…"}` |
| `/chat` | POST | `{"message": "…", "history": [], "voice_id": "aditya", "language": "en", "industry": "hospital"}` | `{"reply": "…", "source": "llm"}` |
| `/chat-stream` | POST | Same as `/chat` | NDJSON stream (see below) |
| `/clone-voice` | POST | `multipart/form-data` fields: `name`, `display_name` (optional), `file` (wav/mp3/flac/ogg) | `{"id","display_name","source"}` |

### `/chat-stream` streaming protocol

Returns `application/x-ndjson` — one JSON object per line:

```
{"type":"token","text":"We're open "}
{"type":"token","text":"Monday through Friday "}
{"type":"audio","data":"<base64 encoded WAV>"}
{"type":"audio","data":"<base64 encoded WAV>"}
{"type":"done","reply":"We're open Monday through Friday, eight a.m. to six p.m.", "tier":"faq"}
```

| Event | Description |
|-------|-------------|
| `token` | Partial response text — appended to the chat bubble in real time |
| `audio` | Base64-encoded WAV for one complete sentence — played sequentially |
| `done` | Stream finished; `reply` contains the full response; `tier` indicates source: `faq` (instant keyword match), `llm` (Ollama generated), or `decline` (honest fallback) |
| `error` | Something went wrong; `detail` has the error message |

### Industry-aware tiered response

The `/chat-stream` endpoint accepts an `industry` parameter (`hospital`, `enterprise`, or `store`) and runs a three-tier pipeline for every query:

1. **Tier 1 — FAQ match:** The query is scored against the industry's FAQ set using keyword overlap + fuzzy similarity. If a confident match is found, the answer is returned instantly — no LLM call. This covers the most common questions (hours, policies, procedures) with sub-millisecond latency.
2. **Tier 2 — LLM fallback:** If no FAQ match is found, the query is sent to the Ollama model with an industry-scoped system prompt. The LLM is instructed to only answer from general knowledge appropriate to that role and never fabricate specific facts.
3. **Tier 3 — Honest decline:** If the LLM itself is uncertain or the query is outside its scope, the agent responds: *"I'm sorry, I don't have that information right now. Would you like me to connect you with someone who can help?"*

### Recording and cloning a new voice

1. Record 20–30 seconds of clean speech (no background noise, single speaker).
   WAV or MP3 format. Longer clips (up to 60s) are fine but 20–30s is the sweet
   spot for XTTS-v2 voice quality.
2. Go to the admin page at **http://localhost:5173/admin** (or call
   `POST /clone-voice` directly via curl/Postman).
3. Enter an **internal name** (e.g. `monica`) and an optional **display name**
   (e.g. `Monica`).
4. Upload the audio file and submit.
5. The new voice appears in the widget's voice dropdown immediately.

---

## Frontend setup

```bash
cd frontend

npm install          # install dependencies
cp .env.example .env # optional — defaults point to localhost:8000

npm run dev          # starts Vite dev server at http://localhost:5173
```

Open **http://localhost:5173** to see the branded landing page with the live
voice widget.

### Pages

| Path | Description |
|------|-------------|
| `/` | Branded landing page + live voice widget |
| `/admin` | Voice cloning admin panel (unlinked from main navigation, no auth) |

### Project structure

```
.
├── backend/
│   ├── main.py            # FastAPI app, routes, CORS, startup
│   ├── engine.py          # Lazy-loaded XTTS + Whisper engines, latent caching
│   ├── llm.py             # Ollama client — industry-scoped system prompts, streaming
│   ├── faq_data.py        # Industry FAQ datasets (hospital, enterprise, store)
│   ├── faq_matcher.py     # Keyword + fuzzy similarity FAQ matching (Tier 1)
│   ├── generate_faq_audio.py  # One-time XTTS synthesis for FAQ audio cache
│   ├── kb_rules.py        # Python port of kb.js keyword rules (legacy fallback)
│   ├── voices.py          # JSON-backed voice profile store
│   ├── seed_voices.py     # Downloads the two demo reference voices
│   ├── requirements.txt   # Pinned app dependencies
│   ├── requirements-cpu.txt
│   ├── voices/            # Generated at runtime (gitignored)
│   └── faq_audio/         # Pre-generated FAQ WAVs: hospital/, enterprise/, store/
├── frontend/
│   ├── src/
│   │   ├── main.jsx       # Entry point
│   │   ├── App.jsx        # Router
│   │   ├── api.js         # Backend API helpers (incl. chatStream, voice mgmt)
│   │   ├── kb.js          # Frontend knowledge base (legacy fallback rules)
│   │   ├── styles.css     # Global branded styles
│   │   ├── components/
│   │   │   ├── Nav.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── IndustryWidget.jsx   # Industry-specific voice widget (3 instances)
│   │   │   └── icons.jsx
│   │   └── pages/
│   │       ├── Landing.jsx
│   │       └── Admin.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── .env.example
├── .gitignore
├── index.html            # Legacy static prototype (reference only)
└── README.md
```

---

## End-to-end walkthrough

1. Start the Ollama server: `ollama serve` (or let it run as a system service)
2. Start the backend: `cd backend && uvicorn main:app --reload`
3. Start the frontend: `cd frontend && npm run dev`
4. Open http://localhost:5173
5. Pick an industry (Hospital, Enterprises, or Store) and click "Start Speaking"
6. NORBEAI greets you and starts listening — speak your question
7. The tiered system answers: FAQ match first, LLM fallback second, honest decline last
8. NORBEAI speaks the answer aloud and listens for your next question
9. Try cloning a new voice at http://localhost:5173/admin

### What happens when you ask a question

```
User speaks → /transcribe (faster-whisper)
              → /chat-stream (industry router)
                → Tier 1: FAQ match → cached WAV (instant, no TTS)
                → Tier 2: LLM fallback (gemma2:2b, industry-scoped prompt)
                → Tier 3: Honest decline ("I don't have that info...")
              → Backend: response → base64 WAV
              → Frontend: text appears word-by-word, audio plays sequentially
              → Auto-listens for the next question
```

If Ollama is unavailable, the backend returns the kb.js keyword-matched answer
as a single streaming response — the voice still works, just without the LLM.

---

## Configuration reference

All backend settings are controlled via environment variables (or `.env` at the
project root). See `.env.example` for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | FastAPI bind address |
| `PORT` | `8000` | FastAPI bind port |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Allowed CORS origins |
| `DEVICE` | `cpu` | `cpu` or `cuda` (requires CUDA PyTorch) |
| `XTTS_MODEL_NAME` | `tts_models/multilingual/multi-dataset/xtts_v2` | XTTS model id |
| `WHISPER_MODEL_SIZE` | `small` | Whisper model size (`tiny` / `base` / `small` / `medium` / `large-v3`) |
| `VOICES_DIR` | `voices` | Voice profiles directory (relative to `backend/`) |
| `OLLAMA_MODEL` | `gemma2:2b` | Ollama model for the chat brain (set blank to disable LLM) |

---

## Notes

- **FAQ audio cache:** Running `python generate_faq_audio.py` pre-generates WAV
  files for all 50 FAQ answers (18 hospital + 16 enterprise + 16 store). These
  are served instantly on Tier 1 FAQ matches — zero TTS latency. Without the
  cache, FAQ answers are synthesized live (~5–16s on CPU). Use `--force` to
  regenerate all WAVs, or `--voice <id>` to use a specific reference voice.
- **Latent caching:** XTTS conditioning latents are computed once per reference
  voice and cached in memory. The first request per voice takes ~30s on CPU;
  subsequent requests skip conditioning entirely (~5–8s on CPU, <1s on GPU).
- **TTS latency on CPU:** ~ 5–20 seconds per reply depending on text length and
  hardware. On a modern multi-core machine it's closer to 5–8 seconds for short
  sentences. If you have an NVIDIA GPU, set `DEVICE=cuda` for near-real-time
  responses.
- **LLM fallback:** If Ollama is not running or the model is not pulled, every
  chat request falls back to the built-in keyword-matched knowledge base (kb.js).
  No error is shown to the user — the voice simply answers from the local rules.
- **No vendor names exposed:** the UI and API responses reference "NORBEAI"
  branded voice names only. Internal model names are never sent to the client.
- **Voice cloning license:** XTTS-v2 is released under the
  [Coqui Public Model License](https://coqui.ai/cpml).

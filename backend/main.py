"""NORBEAI backend — FastAPI app for the AI front desk widget."""

from __future__ import annotations

import base64
import json
import os
import tempfile
import threading
import time as _time
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

import llm
from engine import SUPPORTED_LANGUAGES, SpeechEngine, TranscribeEngine
from voices import VoiceStore

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEVICE = os.getenv("DEVICE", "cpu")
XTTS_MODEL_NAME = os.getenv(
    "XTTS_MODEL_NAME", "tts_models/multilingual/multi-dataset/xtts_v2"
)
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
VOICES_DIR = BASE_DIR / os.getenv("VOICES_DIR", "voices")
FAQ_AUDIO_DIR = BASE_DIR / "faq_audio"

store = VoiceStore(VOICES_DIR)
tts = SpeechEngine(XTTS_MODEL_NAME, DEVICE)
stt = TranscribeEngine(WHISPER_MODEL_SIZE, DEVICE)

# Seed the two demo voices (idempotent, safe to run offline).
try:
    from seed_voices import ensure_seeded
    ensure_seeded(store, VOICES_DIR)
    print("Seeded voices:", ", ".join(v.display_name for v in store.list()))
except Exception as exc:  # noqa: BLE001
    print(f"Could not seed demo voices: {exc}")

# Log FAQ audio cache status at startup.
from faq_data import FAQ_DB  # noqa: E402

faq_cache_counts: dict[str, int] = {}
faq_cache_total = 0
faq_total_expected = 0
for _industry, _faqs in FAQ_DB.items():
    _count = len(list((FAQ_AUDIO_DIR / _industry).glob("*.wav"))) if (FAQ_AUDIO_DIR / _industry).exists() else 0
    faq_cache_counts[_industry] = _count
    faq_cache_total += _count
    faq_total_expected += len(_faqs)
print(f"FAQ audio cache: {faq_cache_total}/{faq_total_expected} WAVs ready — {faq_cache_counts}")

app = FastAPI(title="NORBEAI backend", version="1.0.0")

origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,https://voicera-ai-flame.vercel.app"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _warmup_models():
    """Pre-load XTTS model and all voice latents in a background thread."""
    def _do_warmup():
        t0 = _time.monotonic()
        print("[Warmup] Loading XTTS model...")
        tts._load()
        elapsed_model = _time.monotonic() - t0
        print(f"[Warmup] XTTS model loaded in {elapsed_model:.1f}s")

        voices = store.list()
        print(f"[Warmup] Pre-computing latents for {len(voices)} voice(s)...")
        for voice in voices:
            ref = store.resolve_file(voice)
            if ref.exists():
                tts._latents_for(ref)
                print(f"[Warmup]   - {voice.display_name} ({voice.id}) ready")

        elapsed = _time.monotonic() - t0
        print(f"[Warmup] Complete — model + {len(voices)} voice latent(s) cached in {elapsed:.1f}s")

    threading.Thread(target=_do_warmup, daemon=True).start()


ACCEPTED_AUDIO = {".wav", ".mp3", ".flac", ".ogg"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024


class SynthesizeRequest(BaseModel):
    text: str
    voice_id: str
    language: str = "en"


class ChatRequest(BaseModel):
    message: str
    history: list[dict] | None = None
    voice_id: str = "aditya"
    language: str = "en"
    industry: str = "general"


class VoiceUpdateRequest(BaseModel):
    display_name: str


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/health/ollama")
def health_ollama() -> dict:
    if not llm.is_available():
        return {"status": "unavailable", "message": "Ollama server not reachable"}
    if not llm.is_model_available(OLLAMA_MODEL):
        return {
            "status": "model_missing",
            "message": f"Model '{OLLAMA_MODEL}' not pulled. Run: ollama pull {OLLAMA_MODEL}",
        }
    return {"status": "ok", "model": OLLAMA_MODEL}


# ── Voices ────────────────────────────────────────────────────────────────────

@app.get("/voices")
def list_voices() -> list[dict]:
    return [
        {
            "id": voice.id,
            "display_name": voice.display_name,
            "source": voice.source,
            "created_at": voice.created_at,
        }
        for voice in store.list()
    ]


@app.delete("/voices/{voice_id}")
def delete_voice(voice_id: str) -> dict:
    if not store.delete(voice_id):
        raise HTTPException(status_code=404, detail="voice not found")
    return {"status": "deleted", "id": voice_id}


@app.patch("/voices/{voice_id}")
def update_voice(voice_id: str, body: VoiceUpdateRequest) -> dict:
    voice = store.update_display_name(voice_id, body.display_name.strip())
    if voice is None:
        raise HTTPException(status_code=404, detail="voice not found")
    return {"id": voice.id, "display_name": voice.display_name, "source": voice.source}


# ── TTS / STT ────────────────────────────────────────────────────────────────

@app.post("/synthesize")
def synthesize(request: SynthesizeRequest) -> Response:
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    if len(text) > 500:
        raise HTTPException(status_code=400, detail="text too long (max 500 chars)")
    if request.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400, detail=f"unsupported language '{request.language}'"
        )
    voice = store.get(request.voice_id)
    if voice is None:
        raise HTTPException(status_code=404, detail="voice not found")
    try:
        audio = tts.synthesize(text, store.resolve_file(voice), request.language)
    except Exception as exc:  # noqa: BLE001
    	import traceback
    	traceback.print_exc()
    	raise HTTPException(status_code=500, detail=f"TTS failed: {exc}") from exc
    return Response(content=audio, media_type="audio/wav")


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="missing audio file")
    suffix = Path(file.filename).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        text = stt.transcribe(Path(tmp_path))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"transcription failed: {exc}") from exc
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    if not text:
        raise HTTPException(status_code=422, detail="no speech detected")
    return {"text": text}


@app.post("/clone-voice")
async def clone_voice(
    file: UploadFile = File(...),
    name: str = Form(...),
    display_name: str | None = Form(None),
) -> dict:
    voice_id = store.slugify(name)
    if not voice_id:
        raise HTTPException(status_code=400, detail="name must be a non-empty identifier")
    ext = (Path(file.filename or "").suffix or "").lower()
    if ext not in ACCEPTED_AUDIO:
        raise HTTPException(
            status_code=400,
            detail=f"unsupported audio type '{ext or 'unknown'}'; use .wav, .mp3, .flac or .ogg",
        )
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="audio file too large (max 25 MB)")
    target = VOICES_DIR / f"{voice_id}{ext}"
    target.write_bytes(content)
    voice = store.register(voice_id, display_name or voice_id, "custom", target)
    return {"id": voice.id, "display_name": voice.display_name, "source": voice.source}


# ── Chat (LLM-powered) ───────────────────────────────────────────────────────

def _kbjs_fallback_response(message: str) -> str:
    """Return a keyword-matched response from kb.js logic (Python port).

    Mirrors the rules from frontend/src/kb.js so the backend can produce a
    reasonable fallback when Ollama is unavailable.
    """
    from kb_rules import ANSWER
    return ANSWER(message)


@app.post("/chat")
def chat(request: ChatRequest) -> dict:
    """Simple (non-streaming) chat endpoint with tiered response.

    Tier 1: FAQ match (instant, no LLM)
    Tier 2: LLM fallback (Ollama, industry-scoped)
    Tier 3: kb.js keyword fallback
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message is required")

    voice = store.get(request.voice_id)
    if voice is None:
        raise HTTPException(status_code=404, detail="voice not found")

    # ── Tier 1: FAQ match (instant, no LLM call) ──────────────────────────
    import faq_matcher
    faq_hit = faq_matcher.match(request.message, request.industry)
    if faq_hit is not None:
        return {"reply": faq_hit["answer"], "source": "faq"}

    # ── Tier 2: LLM fallback (Ollama, industry-scoped) ────────────────────
    if llm.is_available() and llm.is_model_available(OLLAMA_MODEL):
        try:
            messages = llm.build_messages(request.message, request.history, industry=request.industry)
            reply = llm.generate(OLLAMA_MODEL, messages, temperature=0.3, max_tokens=80)
            if reply:
                return {"reply": reply, "source": "llm"}
        except Exception:  # noqa: BLE001
            pass  # fall through to kb.js

    # ── Tier 3: kb.js keyword fallback ─────────────────────────────────────
    return {"reply": _kbjs_fallback_response(request.message), "source": "kb"}


@app.post("/chat-stream")
async def chat_stream(request: Request) -> StreamingResponse:
    """Streaming chat endpoint with industry-aware tiered response.

    Returns NDJSON — one JSON object per line.

    Protocol:
        {"type":"token",  "text":"We're open"}    — partial text
        {"type":"audio",  "data":"<base64>"}       — WAV chunk for one sentence
        {"type":"done",   "reply":"full text", "tier":"faq|llm|decline"}
        {"type":"error",  "detail":"..."}           — something went wrong

    Tier flow:
        1. FAQ match (instant, no LLM) — keyword + fuzzy scoring
        2. LLM fallback (Ollama) — industry-scoped system prompt
        3. Honest decline — fixed response when LLM is uncertain
    """
    body = await request.json()
    message = (body.get("message") or "").strip()
    history = body.get("history") or []
    voice_id = body.get("voice_id") or "aditya"
    language = body.get("language") or "en"
    industry = (body.get("industry") or "general").lower()

    if not message:
        return StreamingResponse(
            iter([json.dumps({"type": "error", "detail": "message is required"}) + "\n"]),
            media_type="application/x-ndjson",
        )

    voice = store.get(voice_id)
    if voice is None:
        return StreamingResponse(
            iter([json.dumps({"type": "error", "detail": "voice not found"}) + "\n"]),
            media_type="application/x-ndjson",
        )

    DECLINE_MSG = (
        "I'm sorry, I don't have that information right now. "
        "Would you like me to connect you with someone who can help?"
    )

    def _synthesize_and_yield(text: str, tier: str):
        """Synthesize a complete text response and yield token + audio + done."""
        yield json.dumps({"type": "token", "text": text}) + "\n"
        try:
            wav_chunks = tts.synthesize_all(
                [text], store.resolve_file(voice), language
            )
            if wav_chunks:
                b64 = base64.b64encode(wav_chunks[0]).decode()
                yield json.dumps({"type": "audio", "data": b64}) + "\n"
        except Exception:  # noqa: BLE001
            pass
        yield json.dumps({"type": "done", "reply": text, "tier": tier}) + "\n"

    def _stream_llm_response(reply_text: str, tier: str):
        """Stream an LLM response sentence-by-sentence with progressive audio."""
        accumulated = ""
        for sentence in _split_sentences(reply_text):
            yield json.dumps({"type": "token", "text": sentence + " "}) + "\n"
            accumulated += sentence + " "
            try:
                wav_chunks = tts.synthesize_all(
                    [sentence], store.resolve_file(voice), language
                )
                if wav_chunks:
                    b64 = base64.b64encode(wav_chunks[0]).decode()
                    yield json.dumps({"type": "audio", "data": b64}) + "\n"
            except Exception:  # noqa: BLE001
                pass
        yield json.dumps({"type": "done", "reply": accumulated.strip(), "tier": tier}) + "\n"

    def _split_sentences(text: str) -> list[str]:
        """Split text into sentences for progressive TTS."""
        import re as _re
        parts = _re.split(r'(?<=[.!?])\s+', text.strip())
        return [p for p in parts if p.strip()]

    def generate_stream():
        # ── Tier 1: FAQ match (instant, no LLM call) ─────────────────────
        import faq_matcher
        faq_hit = faq_matcher.match(message, industry)
        if faq_hit is not None:
            cached = FAQ_AUDIO_DIR / industry / faq_hit.get("audio_file", "")
            if cached.exists() and cached.stat().st_size > 0:
                wav_bytes = cached.read_bytes()
                yield json.dumps({"type": "token", "text": faq_hit["answer"]}) + "\n"
                yield json.dumps({"type": "audio", "data": base64.b64encode(wav_bytes).decode()}) + "\n"
                yield json.dumps({"type": "done", "reply": faq_hit["answer"], "tier": "faq"}) + "\n"
                print(f"[TIER] faq — query: {message}")
            else:
                yield from _synthesize_and_yield(faq_hit["answer"], "faq")
                print(f"[TIER] faq (synthesized) — query: {message}")
            return

        # ── Tier 2: LLM fallback (Ollama, industry-scoped) ──────────────
        ollama_ok = llm.is_available() and llm.is_model_available(OLLAMA_MODEL)
        if ollama_ok:
            try:
                messages = llm.build_messages(message, history, industry=industry)
                # Non-streaming generate to detect if LLM declines
                reply = llm.generate(OLLAMA_MODEL, messages, temperature=0.3, max_tokens=80)
                if reply:
                    # Check if the LLM effectively declined (contains the decline phrase)
                    reply_lower = reply.lower()
                    if ("i'm sorry" in reply_lower and "don't have" in reply_lower) or \
                       ("don't have that information" in reply_lower):
                        # LLM itself declined → Tier 3
                        yield from _synthesize_and_yield(DECLINE_MSG, "decline")
                        print(f"[TIER] decline (llm declined) — query: {message}")
                        return
                    # LLM answered → stream it sentence-by-sentence
                    yield from _stream_llm_response(reply, "llm")
                    print(f"[TIER] llm — query: {message}")
                    return
            except Exception:  # noqa: BLE001
                pass

        # ── Tier 3: Honest decline (LLM unavailable or uncertain) ─────────
        yield from _synthesize_and_yield(DECLINE_MSG, "decline")
        print(f"[TIER] decline (fallback) — query: {message}")

    return StreamingResponse(
        generate_stream(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    uvicorn.run("main:
", host=HOST, port=PORT)

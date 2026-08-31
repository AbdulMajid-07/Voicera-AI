"""Lazy-loaded TTS + STT engines.

Models are loaded on first use and stay cached for the process lifetime.
Conditioning latents (the voice "embedding") are computed once per reference
audio file and reused across requests — including across multiple sentences
within a single streaming response — which keeps replies fast on CPU.
"""

from __future__ import annotations

import io
import os
import tempfile
import threading
from pathlib import Path

os.environ.setdefault("COQUI_TOS_AGREED", "1")

import torch  # noqa: E402
import torchaudio  # noqa: E402

from TTS.tts.configs.xtts_config import XttsConfig  # noqa: E402
from TTS.tts.models.xtts import Xtts  # noqa: E402
from pathlib import Path

def get_user_data_dir(name: str) -> str:
    path = Path.home() / f".{name}"
    path.mkdir(parents=True, exist_ok=True)
    return str(path)  # noqa: E402
from TTS.utils.manage import ModelManager  # noqa: E402

XTTS_SAMPLE_RATE = 24000

SUPPORTED_LANGUAGES = [
    "ar", "cs", "de", "en", "es", "fr", "hi", "hu",
    "it", "ja", "ko", "nl", "pl", "pt", "ru", "tr", "zh-cn",
]


class SpeechEngine:
    """XTTS-v2 text-to-speech with per-voice latent caching.

    Latents are computed once per reference audio file and reused across all
    subsequent synthesize() calls — including sentence-by-sentence streaming
    synthesis via synthesize_all().
    """

    def __init__(self, model_name: str, device: str = "cpu") -> None:
        self.model_name = model_name
        self.device = device
        self._lock = threading.Lock()
        self._model: Xtts | None = None
        self._latents: dict[str, tuple] = {}

    def _load(self) -> Xtts:
        if self._model is None:
            model_path = os.path.join(
    		os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")),
    		"tts",
    		self.model_name.replace("/", "--"),
	    )
            config = XttsConfig()
            config.load_json(os.path.join(model_path, "config.json"))
            model = Xtts.init_from_config(config)
            model.load_checkpoint(
                config,
                checkpoint_path=os.path.join(model_path, "model.pth"),
                vocab_path=os.path.join(model_path, "vocab.json"),
                eval=True,
            )
            model.to(self.device)
            self._model = model
        return self._model

    def _latents_for(self, reference: Path) -> tuple:
        """Get or compute conditioning latents for a reference audio file.

        Results are cached in memory so repeated calls for the same voice
        (e.g. multiple sentences in a streaming response) are instant.
        """
        key = str(reference)
        if key not in self._latents:
            model = self._load()
            gpt_cond, speaker_embedding = model.get_conditioning_latents(
                audio_path=[str(reference)],
                gpt_cond_len=30,
                gpt_cond_chunk_len=4,
                max_ref_length=60,
            )
            self._latents[key] = (gpt_cond, speaker_embedding)
        return self._latents[key]

    def _to_wav_bytes(self, wav: torch.Tensor | object) -> bytes:
        """Convert a raw XTTS output tensor to WAV bytes."""
        if isinstance(wav, torch.Tensor):
            wav = wav.squeeze().detach().cpu()
        else:
            import numpy as np
            wav = torch.from_numpy(np.asarray(wav)).squeeze()

        fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            torchaudio.save(tmp_path, wav.unsqueeze(0), XTTS_SAMPLE_RATE)
            with open(tmp_path, "rb") as handle:
                return handle.read()
        finally:
            os.unlink(tmp_path)

    # ── Public API ────────────────────────────────────────────────────────────

    def synthesize(self, text: str, reference: Path, language: str = "en") -> bytes:
        """Synthesize a single block of text. Used by the /synthesize endpoint."""
        with self._lock:
            model = self._load()
            gpt_cond, speaker_embedding = self._latents_for(reference)
            out = model.inference(
                text, language, gpt_cond, speaker_embedding,
                temperature=0.75, repetition_penalty=5.0,
            )
            wav = out["wav"] if isinstance(out, dict) else out.wav
            return self._to_wav_bytes(wav)

    def synthesize_all(
        self,
        sentences: list[str],
        reference: Path,
        language: str = "en",
    ) -> list[bytes]:
        """Synthesize multiple sentences in one lock hold.

        Pre-loads the voice latents once, then iterates — avoids the per-call
        overhead of acquiring the lock and re-computing latents for each sentence.
        Used by the /chat-stream endpoint for progressive audio synthesis.

        Returns a list of WAV byte strings, one per sentence.
        """
        if not sentences:
            return []
        with self._lock:
            model = self._load()
            gpt_cond, speaker_embedding = self._latents_for(reference)
            results: list[bytes] = []
            for sentence in sentences:
                out = model.inference(
                    sentence, language, gpt_cond, speaker_embedding,
                    temperature=0.75, repetition_penalty=5.0,
                )
                wav = out["wav"] if isinstance(out, dict) else out.wav
                results.append(self._to_wav_bytes(wav))
            return results


class TranscribeEngine:
    """faster-whisper speech-to-text."""

    def __init__(self, model_size: str, device: str = "cpu") -> None:
        self.model_size = model_size
        self.device = device
        self._lock = threading.Lock()
        self._model = None

    def _load(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            compute_type = "int8" if self.device == "cpu" else "float16"
            self._model = WhisperModel(
                self.model_size, device=self.device, compute_type=compute_type
            )
        return self._model

    def transcribe(self, audio_bytes: bytes) -> str:
        with self._lock:
            model = self._load()
            segments, _info = model.transcribe(
                io.BytesIO(audio_bytes),
                beam_size=1,
                vad_filter=True,
                language="en",
                condition_on_previous_text=False,
            )
            return " ".join(segment.text.strip() for segment in segments).strip()

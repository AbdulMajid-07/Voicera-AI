"""NORBEAI voice profile store.

A tiny JSON-backed registry for voice profiles. No database needed — each voice
is a reference audio file plus a metadata entry in voices.json.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from pydantic import BaseModel


class Voice(BaseModel):
    id: str
    display_name: str
    source: str  # "seeded" | "custom"
    file: str    # filename relative to the voices directory
    created_at: float


class VoiceStore:
    def __init__(self, voices_dir: Path) -> None:
        self.dir = voices_dir
        self.dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.dir / "voices.json"
        self._registry: dict[str, Voice] = self._load()

    def _load(self) -> dict[str, Voice]:
        if not self.registry_path.exists():
            return {}
        data = json.loads(self.registry_path.read_text("utf-8"))
        return {key: Voice(**value) for key, value in data.items()}

    def _save(self) -> None:
        payload = {key: voice.model_dump() for key, voice in self._registry.items()}
        self.registry_path.write_text(json.dumps(payload, indent=2), "utf-8")

    def register(self, voice_id: str, display_name: str, source: str, file: Path) -> Voice:
        voice = Voice(
            id=voice_id,
            display_name=display_name,
            source=source,
            file=file.name,
            created_at=time.time(),
        )
        self._registry[voice_id] = voice
        self._save()
        return voice

    def get(self, voice_id: str) -> Voice | None:
        return self._registry.get(voice_id)

    def resolve_file(self, voice: Voice) -> Path:
        return self.dir / voice.file

    def list(self) -> list[Voice]:
        return sorted(self._registry.values(), key=lambda voice: voice.created_at)

    def delete(self, voice_id: str) -> bool:
        """Remove a voice entry and its audio file. Returns True if found."""
        voice = self._registry.pop(voice_id, None)
        if voice is None:
            return False
        audio_path = self.dir / voice.file
        if audio_path.exists():
            audio_path.unlink()
        self._save()
        return True

    def update_display_name(self, voice_id: str, new_name: str) -> Voice | None:
        """Update a voice's display_name. Returns the updated Voice or None."""
        voice = self._registry.get(voice_id)
        if voice is None:
            return None
        voice.display_name = new_name
        self._save()
        return voice

    @staticmethod
    def slugify(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
        return slug or ""

"""Seed the two bundled demo voices.

Downloads two short, clean reference clips that ship with the public XTTS-v2
demo so the widget works out of the box. This runs once (idempotent) — the
files are cached in the voices directory and all synthesis stays local.

Run directly with:  python seed_voices.py
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

from voices import VoiceStore

SAMPLES = {
    "aditya": (
        "https://huggingface.co/spaces/coqui/xtts/resolve/main/examples/male.wav",
        "Aditya",
    ),
    "priya": (
        "https://huggingface.co/spaces/coqui/xtts/resolve/main/examples/female.wav",
        "Priya",
    ),
}


def ensure_seeded(store: VoiceStore, voices_dir: Path, force: bool = False) -> list[str]:
    seeded: list[str] = []
    for voice_id, (url, display_name) in SAMPLES.items():
        if store.get(voice_id) and not force:
            continue
        target = voices_dir / f"{voice_id}.wav"
        if not target.exists() or force:
            print(f"  · downloading reference audio for '{display_name}' …")
            urllib.request.urlretrieve(url, target)
        store.register(voice_id, display_name, "seeded", target)
        seeded.append(voice_id)
    return seeded


def main() -> None:
    base = Path(__file__).resolve().parent
    voices_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else base / "voices"
    store = VoiceStore(voices_dir)
    ensure_seeded(store, voices_dir)
    print("Current voices:", ", ".join(voice.display_name for voice in store.list()))


if __name__ == "__main__":
    main()

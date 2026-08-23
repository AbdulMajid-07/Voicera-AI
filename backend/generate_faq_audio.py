"""Generate cached WAV files for all FAQ answers using XTTS.

Run once after voice seeding:
    python generate_faq_audio.py            # skip existing WAVs
    python generate_faq_audio.py --force    # regenerate everything

Audio is saved to:
    backend/faq_audio/<industry>/<index>.wav

The first voice in VoiceStore is used as the reference speaker.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

# Ensure voices are seeded before we try to pick a reference voice.
from seed_voices import ensure_seeded  # noqa: E402
from voices import VoiceStore  # noqa: E402

VOICES_DIR = BASE_DIR / "voices"
store = VoiceStore(VOICES_DIR)
try:
    ensure_seeded(store, VOICES_DIR)
except Exception:
    pass

from engine import SpeechEngine  # noqa: E402
from faq_data import FAQ_DB  # noqa: E402

FAQ_AUDIO_DIR = BASE_DIR / "faq_audio"


def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-generate FAQ audio cache")
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing WAV files"
    )
    parser.add_argument(
        "--voice",
        type=str,
        default=None,
        help="Voice ID to use as reference (default: first available voice)",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        help="Language code for TTS (default: en)",
    )
    args = parser.parse_args()

    voices = store.list()
    if not voices:
        print("ERROR: No voices available. Run seed_voices.py first.")
        sys.exit(1)

    if args.voice:
        voice = store.get(args.voice)
        if voice is None:
            print(f"ERROR: Voice '{args.voice}' not found.")
            sys.exit(1)
        voice_path = store.resolve_file(voice)
    else:
        voice = voices[0]
        voice_path = store.resolve_file(voice)

    print(f"Using voice: {voice.display_name} ({voice.id})")
    print(f"Language: {args.language}")
    print()

    tts = SpeechEngine(
        "tts_models/multilingual/multi-dataset/xtts_v2", "cpu"
    )

    total = sum(len(faqs) for faqs in FAQ_DB.values())
    done = 0
    skipped = 0
    generated = 0
    t_start = time.time()

    for industry, faqs in FAQ_DB.items():
        ind_dir = FAQ_AUDIO_DIR / industry
        ind_dir.mkdir(parents=True, exist_ok=True)

        for idx, faq in enumerate(faqs):
            filename = faq["audio_file"]
            target = ind_dir / filename
            done += 1

            if target.exists() and not args.force:
                skipped += 1
                print(f"  [{done}/{total}] {industry}/{filename} — exists, skipping")
                continue

            answer = faq["answer"]
            print(f"  [{done}/{total}] {industry}/{filename} — synthesizing…")
            try:
                wav_bytes = tts.synthesize(answer, voice_path, args.language)
                target.write_bytes(wav_bytes)
                generated += 1
            except Exception as exc:
                print(f"    ERROR: {exc}")

    elapsed = time.time() - t_start
    print()
    print(f"Done in {elapsed:.1f}s")
    print(f"  Generated: {generated}")
    print(f"  Skipped:   {skipped}")
    print(f"  Total:     {total}")
    print(f"  Output:    {FAQ_AUDIO_DIR}")


if __name__ == "__main__":
    main()

import json, re, os
from pathlib import Path

import torchaudio as ta
import torch

from chatterbox.tts_turbo import ChatterboxTurboTTS

SPEAKER_RE = re.compile(r"^\[(.+?)\]\s*$")

def parse_script(text: str):
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    blocks = []
    speaker = None
    buf = []

    def flush():
        nonlocal buf, speaker
        if speaker and any(x.strip() for x in buf):
            blocks.append({"speaker": speaker, "text": "\n".join(buf).strip()})
        buf = []

    for ln in lines:
        m = SPEAKER_RE.match(ln.strip())
        if m:
            flush()
            speaker = m.group(1).strip()
            continue
        buf.append(ln)

    flush()
    return blocks

def chunk_text(text: str, max_chars: int = 280):
    """
    Chatterbox Turbo can get unstable with long chunks.
    Keep under ~300 chars. Split mostly on sentence boundaries.
    """
    text = re.sub(r"[ \t]+", " ", text.strip())
    parts = re.split(r"(?<=[\.\!\?])\s+", text)
    chunks, cur = [], ""

    for p in parts:
        if not p:
            continue
        if len(cur) + len(p) + 1 <= max_chars:
            cur = (cur + " " + p).strip()
        else:
            if cur:
                chunks.append(cur)
            while len(p) > max_chars:
                chunks.append(p[:max_chars])
                p = p[max_chars:]
            cur = p.strip()

    if cur:
        chunks.append(cur)
    return chunks

def load_manifest(path: Path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"done": {}, "clips": []}

def save_manifest(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def slugify_filename(title: str) -> str:
    # Keep letters/numbers/space/_/-, drop everything else
    title = title.strip()
    title = re.sub(r"[^\w\s-]", "", title, flags=re.UNICODE)
    title = re.sub(r"\s+", "_", title)
    title = re.sub(r"_+", "_", title)
    return title[:80] or "story"

def get_title_from_blocks(blocks) -> str | None:
    for blk in blocks:
        if blk["speaker"].strip().upper() == "TITLE":
            return blk["text"].strip()
    return None

def main():
    script_path = Path("story.script.txt")
    voices_dir = Path("voices")
    out_dir = Path("out_audio")

    ensure_dir(out_dir)

    blocks = parse_script(script_path.read_text(encoding="utf-8"))
    print(f"Script blocks: {len(blocks)}")

    title = get_title_from_blocks(blocks) or "story"
    story_slug = slugify_filename(title)
    print(f"Story title: {title}")
    print(f"Output slug: {story_slug}")

    # Put each story in its own subfolder (recommended)
    story_dir = out_dir / story_slug
    clips_dir = story_dir / "clips"
    ensure_dir(clips_dir)

    # Story-specific manifest so runs don’t collide
    manifest_path = story_dir / f"manifest_{story_slug}.json"
    manifest = load_manifest(manifest_path)

    # Load model once
    print("Loading Chatterbox-Turbo (CUDA)...")
    model = ChatterboxTurboTTS.from_pretrained(device="cuda")
    sr = model.sr

    # Make a silence clip once (0.7s)
    silence_path = clips_dir / "silence_700ms.wav"
    if not silence_path.exists():
        silence = torch.zeros(1, int(sr * 0.7))
        ta.save(str(silence_path), silence, sr)

    clip_index = 1

    for blk in blocks:
        speaker = blk["speaker"].upper()

        # Skip title blocks
        if speaker in ("TITLE",):
            continue

        # Turbo requires a reference audio file
        ref = voices_dir / f"{speaker.lower()}.wav"
        if not ref.exists():
            ref = voices_dir / "narrator_male_base.wav"
        if not ref.exists():
            raise FileNotFoundError("Missing voices/narrator.wav (Turbo needs a reference clip).")

        for piece in chunk_text(blk["text"], max_chars=280):
            key = f"{clip_index:05d}"
            if manifest["done"].get(key):
                clip_index += 1
                continue

            out_clip = clips_dir / f"{clip_index:05d}_{speaker.lower()}.wav"
            print(f"Generating {out_clip.name}")

            wav = model.generate(piece, audio_prompt_path=str(ref))
            ta.save(str(out_clip), wav, sr)

            manifest["done"][key] = True
            manifest["clips"].append(str(out_clip))
            manifest["clips"].append(str(silence_path))
            save_manifest(manifest_path, manifest)

            clip_index += 1

    print("All clips generated.")

    # Stitch into <story_slug>.wav using ffmpeg
    concat_txt = story_dir / "concat.txt"
    lines = [f"file '{Path(p).resolve().as_posix()}'" for p in manifest["clips"]]
    concat_txt.write_text("\n".join(lines), encoding="utf-8")

    final_wav = story_dir / f"{story_slug}.wav"
    os.system(f'ffmpeg -y -f concat -safe 0 -i "{concat_txt}" -c copy "{final_wav}"')
    print("Wrote:", final_wav)

if __name__ == "__main__":
    main()

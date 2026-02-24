# ️ StoryTurbo

### Chatterbox Turbo TTS Script → Clips → Final WAV

Built for the **Clarity Coders** YouTube channel.

StoryTurbo is a restart-safe renderer for **Chatterbox Turbo TTS** that turns structured story scripts into polished narration audio.

It:

- Parses `[SPEAKER]` formatted scripts
- Splits long text into safe Turbo-sized chunks
- Generates numbered WAV clips
- Inserts consistent ASMR-style pauses
- Uses a manifest for crash-safe resumes
- Stitches everything into one final WAV using ffmpeg

Perfect for:

- ASMR storytelling
- Sleepy game lore
- Mario walkthrough narrations
- Audiobooks
- Calm explainer content

---

# 易 How It Works

1. Reads `story.script.txt`
2. Detects speaker blocks like:
   ```
   [TITLE]
   [NARRATOR_MALE_BASE]
   [NARRATOR_FEMALE_DIALOGUE]
   ```
3. Generates safe-sized TTS clips
4. Inserts a reusable pause clip between segments
5. Concatenates everything into:

```
out_audio/<story_slug>/<story_slug>.wav
```

---

#  Project Structure

```
StoryTurbo/
│
├── tts_render.py
├── story.script.txt
├── voices/
│   └── narrator_male_base.wav
│
└── out_audio/        (generated, gitignored)
```

---

#  Installation

## 1️⃣ Clone Repo

```bash
git clone https://github.com/<your-username>/StoryTurbo.git
cd StoryTurbo
```

---

## 2️⃣ Create Virtual Environment (Recommended)

### Windows (PowerShell)

```powershell
python -m venv chatterbox-env
.\chatterbox-env\Scripts\Activate.ps1
```

### Mac/Linux

```bash
python3 -m venv chatterbox-env
source chatterbox-env/bin/activate
```

---

## 3️⃣ Install Dependencies

### Install PyTorch + Torchaudio

### GPU (CUDA example)

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### CPU Only

```bash
pip install torch torchaudio
```

---

## Install Chatterbox Turbo

If available via pip:

```bash
pip install chatterbox
```

Or from local source:

```bash
pip install -e path/to/chatterbox
```

---

## 4️⃣ Install ffmpeg

Check if installed:

```bash
ffmpeg -version
```

If not:

### Windows

Download from:
https://www.gyan.dev/ffmpeg/builds/

Add the `/bin` folder to PATH.

### Mac

```bash
brew install ffmpeg
```

### Linux

```bash
sudo apt install ffmpeg
```

---

#  Add Voice Reference

Turbo requires a reference voice sample.

Create folder:

```bash
mkdir voices
```

Add at least:

```
voices/narrator_male_base.wav
```

Optional additional speakers:

```
voices/narrator_female_base.wav
voices/narrator_female_dialogue.wav
voices/narrator_male_dialogue.wav
```

---

#  Script Format

Example `story.script.txt`:

```
[TITLE]
Paper Mario: The Thousand-Year Door — Prelude

[NARRATOR_MALE_BASE]
Welcome… and thank you for joining me.

[PAUSE]

[NARRATOR_FEMALE_DIALOGUE]
“Are you sure this is safe?”
```

Rules:

- `[SPEAKER_NAME]` starts a block
- Everything until next speaker tag is spoken by that voice
- Speaker file must exist in `voices/`
- Falls back to `narrator_male_base.wav` if missing

---

# ▶️ Run StoryTurbo

```bash
python tts_render.py
```

Output:

```
out_audio/<story_slug>/
  clips/
  manifest_<story_slug>.json
  concat.txt
  <story_slug>.wav
```

---

#  Restart-Safe Rendering

StoryTurbo creates:

```
manifest_<story_slug>.json
```

This means:

- You can stop mid-render
- Re-run safely
- Previously completed clips will NOT regenerate

---

# ⏸️ Pause Handling

StoryTurbo generates one silence file per story:

```
silence_700ms.wav
```

It reuses this between all clips.

To change pause length, edit:

```python
silence = torch.zeros(1, int(sr * 0.7))
```

Change `0.7` to desired seconds.

---

#  Device Mode (GPU vs CPU)

Currently:

```python
model = ChatterboxTurboTTS.from_pretrained(device="cuda")
```

For CPU mode:

```python
model = ChatterboxTurboTTS.from_pretrained(device="cpu")
```

---

# 識 Recommended .gitignore

```
/chatterbox-env/
/Test/
/out_audio/
/out_audio/*

__pycache__/
*.pyc
.DS_Store
Thumbs.db
```

---

#  Post-Processing Workflow (Optional)

After generating:

```
out_audio/<story_slug>/<story_slug>.wav
```

Enhance clarity here:

https://podcast.adobe.com/en/enhance

Typical workflow:

1. Render via StoryTurbo
2. Upload WAV to Adobe Enhance
3. Download enhanced WAV
4. Import into DaVinci / Premiere / Final Cut

---

#  Why StoryTurbo?

Most TTS scripts:

- Break on long passages
- Crash on reruns
- Don’t manage clips cleanly
- Don’t handle structured scripts

StoryTurbo fixes all of that.

It is built specifically for:

- Long-form narration
- ASMR pacing
- Multi-speaker storytelling
- YouTube content pipelines

---

#  License

Recommended: MIT License

Add a `LICENSE` file in the repo root.

---

#  Credits

- Chatterbox Turbo TTS
- PyTorch + Torchaudio
- ffmpeg

---

#  Built For

Clarity Coders  
Sleepy game lore.  
Calm walkthroughs.  
High-quality narration pipelines.

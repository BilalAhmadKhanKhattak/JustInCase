# 🎧 JustInCase — Subtitle Generator



**JustInCase** is a tool that generates `.srt` subtitles from any given audio file — *just in case* you need them. Built using OpenAI's Whisper model, it's a way to caption voiceovers, dialogues, lectures, or any spoken content.

---

## 🧠 What It Does

- Transcribes audio to text using Whisper (`small` model).
- Formats time into standard `.srt` style (HH:MM:SS,mmm).
- Outputs an editable `.srt` file alongside your audio.
- Friendly CLI interface with colored prompts for clarity.

---

## Screenshot
(!image)[https://github.com/BilalAhmadKhanKhattak/JustInCase/blob/main/ScreenshotJustInCase.png]
## ⚙️ Requirements
Download The Tool First:
```bash
git clone https://github.com/BilalAhmadKhanKhattak/JustInCase
```
Open the folder:
```bash
cd JustInCase
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Ensure ffmpeg is installed and available in system PATH.
You can check by running:
```
ffmpeg -version
```

If ffmpeg is not installed:
Windows: Download FFmpeg and add it to your PATH.
https://ffmpeg.org/download.html

macOS: 
```bash
brew install ffmpeg
```
Linux: 
```bash
sudo apt install ffmpeg (Debian/Ubuntu)
```

## Things To Pay Attention
Subtitle accuracy depends on audio quality, speaker clarity, background noise, and language.
May mishear fast, slurred, or gibberish speech.
Recommended for English and clean voiceovers.
You can edit the .srt manually if needed (And sometimes you may need to correct them)


> "Some mistakes are not mistakes." — *Mr. BILRED*

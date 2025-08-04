import os

import whisper
from datetime import timedelta
from colorama import Fore, init

init(autoreset=True)

model = whisper.load_model("small")

banner = """
 _____ _     _ _______ _______ _____ __   _ _______ _______ _______ _______
   |   |     | |______    |      |   | \  | |       |_____| |______ |______
 __|   |_____| ______|    |    __|__ |  \_| |_____  |     | ______| |______
                                                            Version 1.1
                                                            By Mr. BILRED
JustInCase generates subtitles, just in case you need them!
"""

# just in case u don't understand what this is below, this is the timestamp formatter like (HH:MM:SS,mmm) e.g 00:33:21,987

def format_timestampt(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    milliseconds = int((td.total_seconds() -total_seconds) * 1000)
    return str(td).split(".")[0].zfill(8) + f",{milliseconds:03d}"

    # I know above line seems a bit weird (somehow), but listen, it creates HH:MM:SS,mmm format which is going to be used in .srt subtitle file
    # .split removes the fractional seconds (milliseconds part)
    # like 0:01:23.456000 to 0:01:23

    # .zfill(8) adds leading zeroes
    # 00:01:23

    # f", {milliseconds:03d)} appends the milliseconds as a 3-digit number (zero-padded) e,g ',456'

    # now if input seconds = 83.456 it will produce '00:01:23,456'

# print(format_timestampt(83.456))  # i tried to check with this too!

def listern_and_generate_srt(audio_path):
    result = model.transcribe(audio_path)

    base, _ = os.path.splitext(audio_path)
    srt_output_path = f"{base}_subtitles.srt"

    with open(srt_output_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(result["segments"], start=1):
            start = format_timestampt(segment["start"])
            end = format_timestampt(segment["end"])
            text = segment["text"].strip()

            srt_file.write(f"{i}\n")
            srt_file.write(f"{start} --> {end}\n")
            srt_file.write(f"{text}\n\n")

    print(f"SRT file saved: {srt_output_path}")
    print(Fore.LIGHTYELLOW_EX + "Note: Review the subtitles. Some words may be inaccurate or misheard ")

if __name__ == "__main__":
    print(Fore.LIGHTCYAN_EX + banner)
    audio_path =input(Fore.LIGHTMAGENTA_EX + "Enter the audio file path: ")
    print(Fore.LIGHTYELLOW_EX + "\nWait for a while... (This should work as intended, if things go right, obviously)")
    print(Fore.LIGHTYELLOW_EX + f"If you are getting any FP16 Warning. Just ignore it, and wait for a while...\n")
    listern_and_generate_srt(audio_path)

# Mr. BILRED
# Some mistakes are not mistakes.!
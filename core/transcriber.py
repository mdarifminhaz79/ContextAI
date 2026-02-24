import yt_dlp
import os
import whisper

# Downloading the audio
def download_audio(video_url):

    print(f"Downloading audio from: {video_url}")

    FFMPEG_PATH = r"C:\Users\PC-PC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"

    options = {
        "format": "bestaudio/best",
        "ffmpeg_location": FFMPEG_PATH,
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
        "outtmpl": "temp_audio.%(ext)s"
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([video_url])
        return "temp_audio.mp3"
    
    except Exception as e:
        print(f"An error occured: {e}")
        return None

print("--- Initializing Whisper Model (Once) ---")
model = whisper.load_model("base")

def transcribe_audio(file_path):

    if not os.path.exists(file_path):
        print(f"Audio file not found: {file_path}")
        return None

    print("Transcription started. It may take 2/3 minuted... ")
    result = model.transcribe(file_path,fp16=False)

    # Store the result in a text file
    with open("context.txt","w",encoding="utf-8") as f:
        f.write(result['text'])
    
    return result['text']
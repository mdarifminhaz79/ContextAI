from fastapi import FastAPI, BackgroundTasks, HTTPException
from core.transcriber import download_audio, transcribe_audio
from core.generator import identify_video_type, get_final_verified_reply
from pydantic import BaseModel
import os

app = FastAPI()

# ইন-মেমোরি স্টোর (সেশন হ্যান্ডলিংয়ের জন্য)
app_state = {
    "context": None,
    "video_type": None,
    "status": "idle"
}

class VideoRequest(BaseModel):
    url: str

class CommentRequest(BaseModel):
    comment: str

@app.get("/")
def run():
    return {"message": "ContextAI API is running successfully"}

# --- ব্যাকগ্রাউন্ডে ট্রান্সক্রিপশন ফাংশন ---
def background_processing(url: str):
    app_state["status"] = "processing"
    audio_file = download_audio(url)
    if audio_file:
        context = transcribe_audio(audio_file)
        app_state["context"] = context
        # ভিডিও টাইপ একবারই ডিটেক্ট করে সেভ করে রাখা হচ্ছে (এপিআই কল সেভ করার জন্য)
        app_state["video_type"] = identify_video_type(context=context)
        app_state["status"] = "ready"
    else:
        app_state["status"] = "error"

@app.post("/process-video/")
async def process_video(request: VideoRequest, background_tasks: BackgroundTasks):
    # বড় ভিডিওর জন্য আমরা BackgroundTasks ব্যবহার করছি
    background_tasks.add_task(background_processing, request.url)
    return {"message": "Transcription started in background. Check /status for updates."}

@app.get("/status/")
async def get_status():
    return {"status": app_state["status"], "video_type": app_state["video_type"]}

@app.post("/get-reply/")
async def get_reply(request: CommentRequest):
    # কন্টেক্সট চেক করা (DVC tracked file বা memory থেকে)
    if not app_state["context"]:
        if os.path.exists('context.txt'):
            with open("context.txt", "r", encoding="utf-8") as f:
                app_state["context"] = f.read()
            app_state["video_type"] = identify_video_type(app_state["context"])
        else:
            raise HTTPException(status_code=400, detail="No context found. Process a video first.")

    # এখন জেনারেটর কল করা (রেট লিমিটার আপনার generator.py-তেই আছে)
    reply = get_final_verified_reply(
        request.comment, 
        app_state["context"], 
        app_state["video_type"]
    ) 
    return {"ai_reply": reply}
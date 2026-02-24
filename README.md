# ContextAI 🤖🎥
**High-Performance YouTube Content Analysis & Smart Reply Generator**

ContextAI is a specialized backend system designed to handle long-form YouTube content (2-3 hour videos). It transcribes audio, identifies the context/tone of the video, and generates human-like, verified replies to user comments using Large Language Models (LLMs).

## 🏗️ System Architecture



The system follows a modular MLOps approach:
1.  **Ingestion:** Downloads audio from YouTube via `yt-dlp`.
2.  **Transcription:** Uses OpenAI's **Whisper** for high-accuracy speech-to-text.
3.  **Data Versioning:** Managed by **DVC** to handle large transcript files without bloating the Git repository.
4.  **Inference:** Powered by **Groq (Llama 3.1)** for ultra-fast response generation.
5.  **Resilience:** Implemented `tenacity` retry logic to handle API rate limits and network flakiness.

## 🚀 Key Features
* **Scalable MLOps Pipeline:** Separates code (Git) from data (DVC).
* **Background Processing:** Utilizes FastAPI `BackgroundTasks` to handle long transcription jobs without blocking the API.
* **Context-Aware Personality:** Automatically detects if a video is a *Tutorial, Vlog, or Podcast* to adjust the reply tone.
* **Dockerized Deployment:** Ready to be deployed in any environment with a single command.

## 🛠️ Tech Stack
- **Framework:** FastAPI
- **LLM API:** Groq Cloud
- **MLOps Tools:** DVC (Data Versioning Control), Git
- **Containerization:** Docker
- **Libraries:** yt-dlp, OpenAI Whisper, Tenacity, Pydantic

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/mdarifminhaz79/ContextAI.git](https://github.com/mdarifminhaz79/ContextAI.git)
   cd ContextAI
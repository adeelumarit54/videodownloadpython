

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import yt_dlp
import os
import uuid

# ✅ Initialize app
app = FastAPI(title="Adeel Video Downloader")

# ✅ CORS setup (for local + production)
origins = [
    "http://localhost:5173",
    "https://prodownloadfrontend.vercel.app",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # includes OPTIONS for preflight
    allow_headers=["*"],
    expose_headers=["*"],
)

# ✅ Health check route
@app.get("/")
def home():
    """Health check route"""
    return {"message": "Adeel Video Downloader API is running 🚀"}

# ✅ Define request model
class VideoRequest(BaseModel):
    url: str

# ✅ Main download route
# @app.post("/download")
@app.post("/download")
def download_video(request: VideoRequest):
    """Download a video from YouTube, TikTok, Instagram, or Facebook"""
    try:
        url = request.url.strip()
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")

        os.makedirs("downloads", exist_ok=True)

        output_template = os.path.join("downloads", "%(title)s.%(ext)s")

        ydl_opts = {
            "outtmpl": output_template,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "quiet": True,
            "noplaylist": True,
        }

        if "tiktok.com" in url:
            ydl_opts.update({
                "user_agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/117.0.0.0 Safari/537.36"
                ),
                "extractor_args": {"tiktok": {"app_version": ["35.5.2"]}},
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get("title", "video")
            file_ext = info.get("ext", "mp4")
            output_path = os.path.join("downloads", f"{video_title}.{file_ext}")

        return FileResponse(
            path=output_path,
            filename=f"{video_title}.mp4",
            media_type="video/mp4",
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")
# def download_video(request: VideoRequest):
#     """Download a video from YouTube, TikTok, Instagram, or Facebook"""
#     try:
#         url = request.url.strip()
#         if not url:
#             raise HTTPException(status_code=400, detail="No URL provided")

#         os.makedirs("downloads", exist_ok=True)

#         # Unique filename for output
#         output_filename = f"{uuid.uuid4()}.mp4"
#         output_path = os.path.join("downloads", output_filename)

#         # Base yt_dlp options
#         ydl_opts = {
#             "outtmpl": output_path,
#             "format": "best[ext=mp4]/best",
#             "quiet": True,
#             "noplaylist": True,
#         }

#         # TikTok specific handling
#         if "tiktok.com" in url:
#             ydl_opts.update({
#                 "user_agent": (
#                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                     "AppleWebKit/537.36 (KHTML, like Gecko) "
#                     "Chrome/117.0.0.0 Safari/537.36"
#                 ),
#                 "extractor_args": {"tiktok": {"app_version": ["35.5.2"]}},
#             })

#         # YouTube specific handling
#         elif "youtube.com" in url or "youtu.be" in url:
#             ydl_opts.update({
#                 "format": "bestvideo+bestaudio/best",
#                 "merge_output_format": "mp4",
#             })

#         # ✅ Download video using yt_dlp
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             ydl.download([url])

#         # ✅ Return file for download
#         return FileResponse(
#             path=output_path,
#             filename="video.mp4",
#             media_type="video/mp4",
#         )

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")


# ✅ Explicit CORS preflight handler (important for Render)
@app.options("/download")
async def download_options(request: Request):
    """Handle CORS preflight for /download"""
    response = JSONResponse(content={"message": "CORS preflight OK"})
    response.headers["Access-Control-Allow-Origin"] = "https://prodownloadfrontend.vercel.app"
    
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response



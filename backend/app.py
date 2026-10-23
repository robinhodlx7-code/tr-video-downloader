import asyncio
import os
import re
import tempfile
import time
from collections import defaultdict, deque
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp

app = FastAPI(title="TR Video Downloader API", docs_url=None, redoc_url=None)
ORIGIN = os.getenv("SITE_ORIGIN", "https://robinhodlx7-code.github.io")
app.add_middleware(CORSMiddleware, allow_origins=[ORIGIN], allow_methods=["POST", "GET"], allow_headers=["Content-Type"])
ALLOWED = ("tiktok.com", "instagram.com", "pinterest.com", "pin.it")
MAX_BYTES = 100 * 1024 * 1024
semaphore = asyncio.Semaphore(2)
hits = defaultdict(deque)

class VideoRequest(BaseModel):
    url: str

def valid_url(raw):
    if len(raw) > 2048:
        return False
    try:
        u = urlparse(raw)
        host = (u.hostname or "").lower().rstrip(".")
        return u.scheme == "https" and not u.username and not u.password and u.port is None and any(host == d or host.endswith("." + d) for d in ALLOWED)
    except ValueError:
        return False

def download(url, folder):
    opts = {
        "outtmpl": str(Path(folder) / "video.%(ext)s"),
        "format": "best[ext=mp4][height<=1080]/best[ext=mp4]/best",
        "noplaylist": True,
        "max_filesize": MAX_BYTES,
        "socket_timeout": 12,
        "retries": 1,
        "fragment_retries": 1,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "cachedir": False,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    candidates = [p for p in Path(folder).iterdir() if p.is_file() and p.suffix.lower() == ".mp4"]
    if not candidates:
        raise ValueError("Não foi possível obter MP4 deste vídeo.")
    p = candidates[0]
    if p.stat().st_size > MAX_BYTES:
        raise ValueError("Vídeo acima do limite de 100 MB.")
    return p

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/download")
async def get_video(data: VideoRequest, request: Request):
    if not valid_url(data.url):
        raise HTTPException(400, "Informe um link HTTPS válido do TikTok, Instagram ou Pinterest.")
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    q = hits[ip]
    while q and now - q[0] > 3600:
        q.popleft()
    if len(q) >= 10:
        raise HTTPException(429, "Limite de 10 downloads por hora atingido.")
    q.append(now)
    import shutil
    folder = tempfile.mkdtemp(prefix="trvideo-")
    try:
        async with semaphore:
            path = await asyncio.wait_for(asyncio.to_thread(download, data.url, folder), timeout=90)
        return FileResponse(str(path), media_type="video/mp4", filename="tr-video.mp4", background=BackgroundTask(shutil.rmtree, folder, ignore_errors=True))
    except asyncio.TimeoutError:
        shutil.rmtree(folder, ignore_errors=True)
        raise HTTPException(504, "Tempo limite atingido.")
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise HTTPException(422, "Não foi possível baixar este vídeo público. Pode haver restrições da plataforma, tamanho ou formato.")

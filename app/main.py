from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import asyncio

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"
MEDIA_ROOT = BASE_DIR / "media" / "galleries"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://192.168.1.249:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.get("/api/galleries")
def get_galleries():
    return [
        {"id": "weddings", "title": "Weddings"},
        {"id": "portraits", "title": "Portraits"}
    ]

app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

@app.get("/api/galleries/{gallery_name}")
async def get_gallery(gallery_name: str):
    folder = MEDIA_ROOT / gallery_name

    if not folder.exists() or not folder.is_dir():
        raise HTTPException(status_code=404, detail="Gallery not found")

    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    images = [
        f"/media/galleries/{gallery_name}/{file.name}"
        for file in sorted(folder.iterdir())
        if file.suffix.lower() in allowed_extensions
    ]

    return {
        "gallery": gallery_name,
        "images": images
    }
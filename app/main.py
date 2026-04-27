from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from pathlib import Path
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"
MEDIA_ROOT = BASE_DIR / "media" / "galleries"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONTACT FORM

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str
    website: str | None = None   # 🐝 honeypot field


EMAIL_TO = "JonathanCarlson3712@Hotmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = (os.getenv("SMTP_PASSWORD") or "").replace(" ", "")


@app.post("/api/contact")
async def submit_contact(msg: ContactMessage):

    # 🐝 Honeypot check (bot detection)
    if msg.website:
        return {"status": "sent"}  # silently ignore bots

    email = EmailMessage()
    email["Subject"] = f"Website Contact - {msg.name}"
    email["From"] = SMTP_USERNAME
    email["To"] = EMAIL_TO
    email["Reply-To"] = msg.email

    email.set_content(
        f"""
Name: {msg.name}
Email: {msg.email}

Message:
{msg.message}
"""
    )

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(email)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "sent"}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.get("/api/galleries")
def get_galleries():
    return [
        {"id": "weddings", "title": "Weddings"},
        {"id": "portraits", "title": "Portraits"}
    ]


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
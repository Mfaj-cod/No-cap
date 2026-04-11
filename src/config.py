import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    store_name: str
    database_path: Path
    session_secret: str
    razorpay_key_id: str
    razorpay_key_secret: str
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str
    owner_email: str
    groq_api_key: str
    groq_model: str
    resend_api_key: str


settings = Settings(
    store_name="NoCaps",
    database_path=BASE_DIR / "store.db",
    session_secret=os.getenv("SESSION_SECRET") or os.getenv("SECRET_KEY", "devsecret"),
    razorpay_key_id=os.getenv("RAZORPAY_KEY_ID", ""),
    razorpay_key_secret=os.getenv("RAZORPAY_KEY_SECRET", ""),
    smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    smtp_port=int(os.getenv("SMTP_PORT", "587")),
    smtp_user=os.getenv("SMTP_USER"),
    smtp_pass=os.getenv("SMTP_PASS"),
    owner_email=os.getenv("OWNER_EMAIL"),
    groq_api_key=os.getenv("GROQ_API_KEY", ""),
    groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    resend_api_key=os.getenv("RESEND_API_KEY", ""),
)

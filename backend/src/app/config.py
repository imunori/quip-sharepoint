import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR / 'app.db'}"

DATA_DIR.mkdir(exist_ok=True)
STORAGE_DIR.mkdir(exist_ok=True)

# JWT - read from env or generate a random secret (persisted to file for restarts)
_secret_file = DATA_DIR / ".jwt_secret"


def _get_jwt_secret() -> str:
    env_val = os.environ.get("JWT_SECRET")
    if env_val and env_val != "change-me-in-production":
        return env_val
    # Persist a random secret so it survives restarts
    if _secret_file.exists():
        return _secret_file.read_text().strip()
    secret = secrets.token_urlsafe(48)
    _secret_file.write_text(secret)
    return secret


JWT_SECRET = _get_jwt_secret()
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.environ.get("JWT_EXPIRE_HOURS", "24"))

# Default site info (SharePoint compat)
SITE_TITLE = "Quip-SharePoint"
SITE_DESCRIPTION = "Self-hosted collaborative document platform"

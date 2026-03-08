from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR / 'app.db'}"

DATA_DIR.mkdir(exist_ok=True)
STORAGE_DIR.mkdir(exist_ok=True)

# JWT
JWT_SECRET = "change-me-in-production"
JWT_ALGORITHM = "HS256"

# Default site info (SharePoint compat)
SITE_TITLE = "Quip-SharePoint"
SITE_DESCRIPTION = "Self-hosted collaborative document platform"

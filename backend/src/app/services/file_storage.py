import shutil
from pathlib import Path

from ..config import STORAGE_DIR


def _safe_path(relative: str) -> Path:
    """Resolve path and ensure it stays within STORAGE_DIR."""
    resolved = (STORAGE_DIR / relative).resolve()
    if not str(resolved).startswith(str(STORAGE_DIR.resolve())):
        raise ValueError("Path traversal detected")
    return resolved


def save_file(folder_path: str, filename: str, data: bytes) -> str:
    """Save file to local storage, return relative path."""
    target_dir = _safe_path(folder_path.strip("/"))
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = _safe_path(f"{folder_path.strip('/')}/{filename}")
    file_path.write_bytes(data)
    return str(file_path.relative_to(STORAGE_DIR))


def read_file(relative_path: str) -> bytes:
    file_path = _safe_path(relative_path)
    return file_path.read_bytes()


def delete_file(relative_path: str) -> bool:
    file_path = _safe_path(relative_path)
    if file_path.exists():
        file_path.unlink()
        return True
    return False


def get_file_size(relative_path: str) -> int:
    file_path = _safe_path(relative_path)
    return file_path.stat().st_size if file_path.exists() else 0

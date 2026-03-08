import shutil
from pathlib import Path

from ..config import STORAGE_DIR


def save_file(folder_path: str, filename: str, data: bytes) -> str:
    """Save file to local storage, return relative path."""
    target_dir = STORAGE_DIR / folder_path.strip("/")
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / filename
    file_path.write_bytes(data)
    return str(file_path.relative_to(STORAGE_DIR))


def read_file(relative_path: str) -> bytes:
    file_path = STORAGE_DIR / relative_path
    return file_path.read_bytes()


def delete_file(relative_path: str) -> bool:
    file_path = STORAGE_DIR / relative_path
    if file_path.exists():
        file_path.unlink()
        return True
    return False


def get_file_size(relative_path: str) -> int:
    file_path = STORAGE_DIR / relative_path
    return file_path.stat().st_size if file_path.exists() else 0

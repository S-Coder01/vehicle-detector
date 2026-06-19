import os
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile

UPLOAD_DIR = Path("uploads")

def ensure_upload_dir():
    UPLOAD_DIR.mkdir(exist_ok=True)

async def save_upload_file(file: UploadFile, user_id: int) -> str:
    ensure_upload_dir()
    user_folder = UPLOAD_DIR / f"user_{user_id}"
    user_folder.mkdir(exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    unique_id = uuid.uuid4().hex[:8]
    filename = f"{now}_{unique_id}.jpg"
    file_path = user_folder / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Нормализуем путь: заменяем обратные слеши на прямые
    relative_path = str(file_path.relative_to(UPLOAD_DIR)).replace("\\", "/")
    return relative_path

def delete_file(relative_path: str) -> bool:
    full_path = UPLOAD_DIR / relative_path
    if full_path.exists():
        os.remove(full_path)
        return True
    return False
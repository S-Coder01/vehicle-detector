import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import UserInfo, History, ModelName
from app.api.schemas.detect import DetectResponse, DetectionBox
from app.core.security import get_current_user
from app.services import storage
from app.services.detector import predict

router = APIRouter(prefix="/detect", tags=["detect"])

@router.post("/", response_model=DetectResponse)
async def detect_vehicles(
    file: UploadFile = File(...),
    model_name: ModelName = Form(...),
    conf_threshold: float = Form(0.25, ge=0.0, le=1.0),
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Загружает изображение, выполняет детекцию выбранной моделью,
    сохраняет результат в историю пользователя и возвращает результат.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    relative_path = await storage.save_upload_file(file, current_user.id)

    try:
        full_path = Path("uploads") / relative_path
        result = predict(str(full_path), model_name.value, conf_threshold)
    except Exception as e:
        storage.delete_file(relative_path)
        raise HTTPException(status_code=500, detail=f"Ошибка детекции: {str(e)}")

    history_entry = History(
        user_id=current_user.id,
        image_path=relative_path,
        model_used=model_name.value,
        results_json=json.dumps(result, default=str)
    )
    db.add(history_entry)
    await db.commit()
    await db.refresh(history_entry)

    detections = [
        DetectionBox(
            class_id=d["class_id"],
            class_name=d["class_name"],
            confidence=d["confidence"],
            x1=d["x1"],
            y1=d["y1"],
            x2=d["x2"],
            y2=d["y2"]
        )
        for d in result["detections"]
    ]

    return DetectResponse(
        model_used=model_name.value,
        detections=detections,
        image_width=result["image_width"],
        image_height=result["image_height"]
    )
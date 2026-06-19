from pathlib import Path
from ultralytics import YOLO
from typing import List, Dict, Any
import json

# Путь к папке с моделями (корневая папка /models)
MODELS_DIR = Path("models")

# Словарь для загрузки моделей (кэширование)
_model_cache = {}

def load_model(model_name: str) -> YOLO:
    """Загружает модель по имени (с кэшированием)"""
    if model_name not in _model_cache:
        model_path = MODELS_DIR / f"{model_name}.pt"
        if not model_path.exists():
            raise FileNotFoundError(f"Модель {model_name} не найдена по пути {model_path}")
        _model_cache[model_name] = YOLO(str(model_path))
    return _model_cache[model_name]

def predict(image_path: str, model_name: str, conf_threshold: float = 0.25) -> Dict[str, Any]:
    """
    Выполняет инференс на изображении.
    Возвращает словарь с детекциями и размерами изображения.
    """
    model = load_model(model_name)
    results = model(image_path, conf=conf_threshold)[0]
    img_width, img_height = results.orig_shape[1], results.orig_shape[0]

    detections = []
    if results.boxes is not None:
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            # Имена классов берутся из модели (можно захардкодить, но лучше взять из names)
            class_name = model.model.names[cls_id] if hasattr(model.model, 'names') else str(cls_id)
            detections.append({
                "class_id": cls_id,
                "class_name": class_name,
                "confidence": conf,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            })

    return {
        "image_width": img_width,
        "image_height": img_height,
        "detections": detections
    }
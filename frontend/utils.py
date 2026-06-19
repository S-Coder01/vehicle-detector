import io
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any

CLASS_COLORS = {
    0: (255, 0, 0),
    1: (0, 255, 0),
    2: (0, 0, 255),
    3: (255, 255, 0),
    4: (255, 0, 255),
    5: (0, 255, 255)
}

CLASS_NAMES_RU = {
    0: 'легковое авто',
    1: 'фургон',
    2: 'грузовик',
    3: 'трицикл с тентом',
    4: 'автобус',
    5: 'мотоцикл'
}

def get_font(size: int = 12):
    """Загружает шрифт с поддержкой кириллицы, определяя ОС."""
    font_paths = [
        # Linux (включая Docker)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # Windows
        "C:/Windows/Fonts/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        # macOS
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttf",
    ]
    # Добавляем пути в зависимости от ОС
    if sys.platform == "win32":
        # Windows уже имеет Arial по указанным выше путям
        pass
    elif sys.platform == "darwin":
        # macOS также имеет Arial
        pass

    for path in font_paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    # Если ничего не найдено, используем встроенный шрифт (без кириллицы)
    return ImageFont.load_default()

def draw_bboxes_on_image(image_bytes: bytes, detections: List[Dict[str, Any]],
                         show_labels: bool = True, show_class_ids: bool = False,
                         filter_classes: List[int] = None) -> bytes:
    """Рисует боксы с фильтрацией по классам."""
    if filter_classes:
        detections = [d for d in detections if d["class_id"] in filter_classes]

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)

    font = get_font(12)

    for det in detections:
        cls_id = det["class_id"]
        x1 = det["x1"]
        y1 = det["y1"]
        x2 = det["x2"]
        y2 = det["y2"]
        color = CLASS_COLORS.get(cls_id, (128, 128, 128))

        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

        if show_labels or show_class_ids:
            label_parts = []
            if show_class_ids:
                label_parts.append(str(cls_id))
            if show_labels:
                label_parts.append(CLASS_NAMES_RU.get(cls_id, f"class_{cls_id}"))
            label = ": ".join(label_parts) if label_parts else ""
            if label:
                try:
                    bbox = draw.textbbox((x1, y1 - 15), label, font=font)
                except AttributeError:
                    # Для старых версий Pillow
                    text_width, text_height = draw.textsize(label, font=font)
                    bbox = (x1, y1 - 15, x1 + text_width, y1 - 15 + text_height)
                draw.rectangle(bbox, fill=color)
                draw.text((x1, y1 - 15), label, fill="white", font=font)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()
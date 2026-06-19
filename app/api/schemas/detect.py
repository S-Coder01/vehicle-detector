from typing import List
from app.api.schemas.base import BaseSchema

class DetectionBox(BaseSchema):
    class_id: int
    class_name: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int

class DetectResponse(BaseSchema):
    model_used: str
    detections: List[DetectionBox]
    image_width: int
    image_height: int
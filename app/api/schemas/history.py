from datetime import datetime
from typing import List, Optional
from app.api.schemas.base import BaseSchema

class HistoryEntry(BaseSchema):
    id: int
    image_path: str
    model_used: str
    created_at: datetime
    results_json: str  # добавляем поле с JSON-строкой

class HistoryListResponse(BaseSchema):
    entries: List[HistoryEntry]
    total: int
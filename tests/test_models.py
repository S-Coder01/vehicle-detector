import pytest
from pydantic import ValidationError
from datetime import datetime
from app.api.schemas.auth import User
from app.api.schemas.detect import DetectionBox, DetectResponse
from app.api.schemas.history import HistoryEntry, HistoryListResponse

def test_user_schema_valid():
    user = User(username="validuser", password="pass123")
    assert user.username == "validuser"

def test_user_schema_invalid_username():
    with pytest.raises(ValidationError):
        User(username="invalid@user", password="pass123")  # не alphanumeric

def test_user_schema_short_password():
    with pytest.raises(ValidationError):
        User(username="test", password="123")  # меньше 6 символов

def test_detection_box_schema():
    box = DetectionBox(
        class_id=0,
        class_name="car",
        confidence=0.95,
        x1=10,
        y1=20,
        x2=30,
        y2=40
    )
    assert box.class_name == "car"

def test_detect_response_schema():
    box = DetectionBox(class_id=0, class_name="car", confidence=0.9, x1=0, y1=0, x2=10, y2=10)
    response = DetectResponse(
        model_used="yolo26n_fast",
        detections=[box],
        image_width=640,
        image_height=480
    )
    assert len(response.detections) == 1

def test_history_entry_schema():
    entry = HistoryEntry(
        id=1,
        image_path="user_1/2025-01-15.jpg",
        model_used="yolo26n_fast",
        created_at=datetime.now(),
        results_json='{"detections": []}'
    )
    assert entry.model_used == "yolo26n_fast"

def test_history_list_response():
    entries = [
        HistoryEntry(
            id=1,
            image_path="a.jpg",
            model_used="fast",
            created_at=datetime.now(),
            results_json='{}'
        )
    ]
    response = HistoryListResponse(entries=entries, total=1)
    assert response.total == 1
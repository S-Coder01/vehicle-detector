import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient

@pytest.mark.asyncio
@patch("app.services.storage.save_upload_file", new_callable=AsyncMock)  # мокаем метод модуля storage
@patch("app.api.endpoints.detect.predict")                               # мокаем локальный импорт predict
async def test_detect_success(mock_predict, mock_save_file, client: AsyncClient, auth_token):
    mock_save_file.return_value = "user_1/2025-01-15_test.jpg"
    mock_predict.return_value = {
        "image_width": 800,
        "image_height": 600,
        "detections": [
            {
                "class_id": 0,
                "class_name": "car",
                "confidence": 0.95,
                "x1": 100,
                "y1": 200,
                "x2": 300,
                "y2": 400
            }
        ]
    }
    files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}
    data = {"model_name": "yolo26n_fast", "conf_threshold": 0.25}
    response = await client.post(
        "/detect/",
        files=files,
        data=data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    result = response.json()
    assert result["model_used"] == "yolo26n_fast"
    assert len(result["detections"]) == 1
    assert result["detections"][0]["class_name"] == "car"

@pytest.mark.asyncio
@patch("app.services.storage.save_upload_file", new_callable=AsyncMock)
@patch("app.api.endpoints.detect.predict")
async def test_detect_no_objects(mock_predict, mock_save_file, client: AsyncClient, auth_token):
    mock_save_file.return_value = "user_1/empty.jpg"
    mock_predict.return_value = {
        "image_width": 800,
        "image_height": 600,
        "detections": []
    }
    files = {"file": ("empty.jpg", b"fake", "image/jpeg")}
    data = {"model_name": "yolo26n_fast"}
    response = await client.post(
        "/detect/",
        files=files,
        data=data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result["detections"]) == 0

@pytest.mark.asyncio
async def test_detect_unauthorized(client: AsyncClient):
    files = {"file": ("test.jpg", b"fake", "image/jpeg")}
    data = {"model_name": "yolo26n_fast"}
    response = await client.post("/detect/", files=files, data=data)
    assert response.status_code == 401

@pytest.mark.asyncio
@patch("app.services.storage.save_upload_file", new_callable=AsyncMock)
async def test_detect_invalid_model(mock_save_file, client: AsyncClient, auth_token):
    mock_save_file.return_value = "user_1/test.jpg"
    files = {"file": ("test.jpg", b"fake", "image/jpeg")}
    data = {"model_name": "invalid_model"}
    response = await client.post(
        "/detect/",
        files=files,
        data=data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422
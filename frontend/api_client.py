import os
import requests
from typing import Optional, Dict, Any, List

class APIClient:
    def __init__(self, base_url: str = None):
        if base_url is None:
            base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.base_url = base_url
        self.token: Optional[str] = None

    def set_token(self, token: str):
        self.token = token

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _headers_without_content_type(self) -> Dict[str, str]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def register(self, username: str, password: str) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/register/"
        response = requests.post(url, json={"username": username, "password": password})
        response.raise_for_status()
        return response.json()

    def login(self, username: str, password: str) -> str:
        url = f"{self.base_url}/auth/login"
        data = {"username": username, "password": password}
        response = requests.post(url, data=data)
        response.raise_for_status()
        token = response.json()["access_token"]
        self.token = token
        return token

    def get_user_info(self) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/me"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def detect(self, image_bytes: bytes, model_name: str, conf_threshold: float = 0.25) -> Dict[str, Any]:
        url = f"{self.base_url}/detect/"
        files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
        data = {"model_name": model_name, "conf_threshold": conf_threshold}
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(url, files=files, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_history(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/history/"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        data = response.json()
        return data["entries"]

    def delete_history_entry(self, entry_id: int) -> None:
        url = f"{self.base_url}/history/{entry_id}"
        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()

    def clear_history(self) -> None:
        url = f"{self.base_url}/history/"
        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()

    def get_uploaded_image(self, user_id: int, filename: str) -> bytes:
        url = f"{self.base_url}/uploads/{user_id}/{filename}"
        response = requests.get(url, headers=self._headers_without_content_type())
        response.raise_for_status()
        return response.content
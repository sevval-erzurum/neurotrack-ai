"""Backend API istemcisi.

Tüm HTTP çağrıları buradan geçer; sayfalar requests ile doğrudan konuşmaz.
Her çağrı (ok, payload) döndürür — payload hata durumunda okunabilir bir mesajdır.
"""

import os
from typing import Any

import requests

API_URL = os.environ.get("NEUROTRACK_API_URL", "http://127.0.0.1:8003")

TIMEOUT = 10


def _error_message(response: requests.Response) -> str:
    """FastAPI hata gövdesinden kullanıcıya gösterilebilir bir mesaj çıkarır."""
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"Sunucu {response.status_code} yanıtı döndü."

    if isinstance(payload, dict):
        detail = payload.get("detail", payload)
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list) and detail:
            first = detail[0]
            if isinstance(first, dict) and "msg" in first:
                return str(first["msg"])
        return str(detail)

    return str(payload)


def _request(method: str, path: str, **kwargs: Any) -> tuple[bool, Any]:
    try:
        response = requests.request(method, f"{API_URL}{path}", timeout=TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError:
        return False, (
            "Backend'e bağlanılamadı. Sunucunun çalıştığından emin olun: "
            "python -m uvicorn app.main:app --reload --port 8003"
        )
    except requests.exceptions.Timeout:
        return False, "Sunucu zaman aşımına uğradı. Lütfen tekrar deneyin."
    except requests.exceptions.RequestException as error:
        return False, f"Beklenmeyen bağlantı hatası: {error}"

    if response.status_code >= 400:
        return False, _error_message(response)

    try:
        return True, response.json()
    except ValueError:
        return True, response.text


def get(path: str, params: dict | None = None) -> tuple[bool, Any]:
    return _request("GET", path, params=params)


def post(path: str, json: dict | None = None, params: dict | None = None) -> tuple[bool, Any]:
    return _request("POST", path, json=json, params=params)


def health() -> bool:
    """Backend ayakta mı? Sidebar durum göstergesi için."""
    try:
        requests.get(f"{API_URL}/docs", timeout=2)
        return True
    except requests.exceptions.RequestException:
        return False

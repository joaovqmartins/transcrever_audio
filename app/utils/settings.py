"""Persistência local de configurações do usuário (ex.: chave de API da Groq)."""

import json
from typing import Optional

from app.config import SETTINGS_DIR, SETTINGS_FILE


def load_api_key() -> Optional[str]:
    """Lê a chave de API salva no disco, se existir."""
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        api_key = data.get("groq_api_key")
        return api_key or None
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def save_api_key(api_key: str) -> None:
    """Salva a chave de API no disco, em um arquivo fora do repositório."""
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps({"groq_api_key": api_key}), encoding="utf-8")

"""Motor de transcrição via API de STT da Groq (Whisper hospedado na nuvem).

Requer conexão com a internet e uma chave de API da Groq (gratuita em
https://console.groq.com/keys). O áudio é enviado para os servidores da
Groq para ser transcrito — não é mais processado localmente.
"""

from __future__ import annotations

import os
from typing import Callable, Optional

from groq import APIConnectionError, APIStatusError, Groq

from app.config import MAX_FILE_SIZE_MB
from app.utils.audio import file_size_mb


def transcribe_audio(
    file_path: str,
    api_key: str,
    model_id: str,
    language: Optional[str],
    on_status: Callable[[str], None],
) -> str:
    """Envia o áudio para a API da Groq e retorna o texto transcrito."""
    if not api_key:
        raise RuntimeError(
            "Nenhuma chave de API da Groq configurada. Clique no botão "
            "\"Configurações\" e informe sua chave."
        )

    size_mb = file_size_mb(file_path)
    if size_mb > MAX_FILE_SIZE_MB:
        raise RuntimeError(
            f"O arquivo tem {size_mb:.1f} MB, acima do limite de "
            f"{MAX_FILE_SIZE_MB} MB da API da Groq. Use um arquivo menor."
        )

    on_status("Enviando áudio...")
    client = Groq(api_key=api_key)

    request_kwargs = {"model": model_id, "response_format": "json"}
    if language:
        request_kwargs["language"] = language

    try:
        with open(file_path, "rb") as audio_file:
            on_status("Transcrevendo...")
            response = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), audio_file.read()),
                **request_kwargs,
            )
    except APIConnectionError as exc:
        raise RuntimeError(
            "Não foi possível conectar à internet para transcrever o áudio. "
            "Verifique sua conexão e tente novamente."
        ) from exc
    except APIStatusError as exc:
        if exc.status_code == 401:
            raise RuntimeError(
                "Chave de API inválida ou expirada. Verifique sua chave da "
                "Groq nas configurações."
            ) from exc
        raise RuntimeError(f"Erro da API da Groq ({exc.status_code}): {exc.message}") from exc

    on_status("Finalizando...")
    return response.text.strip()

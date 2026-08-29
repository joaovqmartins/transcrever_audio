"""Funções utilitárias para validação e inspeção de arquivos de áudio."""

import os

from app.config import SUPPORTED_EXTENSIONS


def is_supported_audio(file_path: str) -> bool:
    """Verifica se a extensão do arquivo está entre os formatos suportados."""
    return os.path.splitext(file_path)[1].lower() in SUPPORTED_EXTENSIONS


def human_readable_size(file_path: str) -> str:
    """Retorna o tamanho do arquivo em uma unidade legível (KB, MB, GB)."""
    size = float(os.path.getsize(file_path))
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def file_size_mb(file_path: str) -> float:
    """Retorna o tamanho do arquivo em megabytes."""
    return os.path.getsize(file_path) / (1024 * 1024)

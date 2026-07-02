from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = SRC_DIR / "models"
ASSETS_DIR = ROOT_DIR / "assets"
UPLOADS_DIR = ROOT_DIR / "uploads"
REPORTS_DIR = ROOT_DIR / "reports"
TEMP_DIR = ROOT_DIR / "temp"
LOGS_DIR = ROOT_DIR / "logs"
CONFIG_DIR = SRC_DIR / "config"
PAGES_DIR = ROOT_DIR / "pages"
STATIC_DIR = ROOT_DIR / "static"

for directory in (UPLOADS_DIR, REPORTS_DIR, TEMP_DIR, LOGS_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def ensure_directory(path: str | os.PathLike[str]) -> Path:
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj

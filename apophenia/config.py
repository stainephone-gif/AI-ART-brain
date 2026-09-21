"""Загрузка config.yaml и .env. Все пути в конфиге относительны корню репозитория."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: str | Path | None = None) -> Dict[str, Any]:
    path = Path(path) if path else ROOT / "config.yaml"
    path = path.resolve()
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg["_root"] = str(path.parent)
    cfg["_config_path"] = str(path)
    try:
        from dotenv import load_dotenv
        load_dotenv(path.parent / ".env")
    except ImportError:
        pass
    return cfg


def resolve(cfg: Dict[str, Any], p: str | Path) -> Path:
    p = Path(p)
    if p.is_absolute():
        return p
    return Path(cfg.get("_root", ".")) / p


def path_dir(cfg: Dict[str, Any], key: str) -> Path:
    d = resolve(cfg, cfg["paths"][key])
    d.mkdir(parents=True, exist_ok=True)
    return d


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default) or default

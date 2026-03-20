"""计划功能：文件读写工具，负责统一管理工作区文件、阶段产物和中间工件的落盘操作。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config import DEFAULT_ENCODING, DEFAULT_WORKSPACE_STAGES, ROOT_DIR


def ensure_directory(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def write_text(path: str | Path, content: str) -> Path:
    target = Path(path)
    ensure_directory(target.parent)
    target.write_text(content, encoding=DEFAULT_ENCODING)
    return target


def read_text(path: str | Path, default: str = "") -> str:
    target = Path(path)
    if not target.exists():
        return default
    return target.read_text(encoding=DEFAULT_ENCODING)


def write_json(path: str | Path, payload: Any) -> Path:
    target = Path(path)
    ensure_directory(target.parent)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding=DEFAULT_ENCODING,
    )
    return target


def render_template(template_text: str, replacements: dict[str, str]) -> str:
    rendered = template_text
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{ {key} }}}}", value)
    return rendered


class WorkspaceManager:
    """负责为单个任务创建并管理工作区目录。"""

    def __init__(self, workspace: str | Path) -> None:
        raw_path = Path(workspace)
        self.root = raw_path if raw_path.is_absolute() else ROOT_DIR / raw_path

    def ensure(self) -> Path:
        ensure_directory(self.root)
        for stage in DEFAULT_WORKSPACE_STAGES:
            ensure_directory(self.root / stage)
        return self.root

    def stage_dir(self, stage: str) -> Path:
        self.ensure()
        return ensure_directory(self.root / stage)

    def write_stage_text(self, stage: str, filename: str, content: str) -> Path:
        return write_text(self.stage_dir(stage) / filename, content)

    def write_stage_json(self, stage: str, filename: str, payload: Any) -> Path:
        return write_json(self.stage_dir(stage) / filename, payload)

    def read_stage_text(self, stage: str, filename: str, default: str = "") -> str:
        return read_text(self.stage_dir(stage) / filename, default=default)

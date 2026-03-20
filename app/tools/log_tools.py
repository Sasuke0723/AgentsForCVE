"""计划功能：日志处理工具，负责归档、裁剪、清洗和结构化构建日志、PoC 日志与验证日志。"""

from __future__ import annotations

from typing import Iterable

from app.tools.file_tools import WorkspaceManager


def join_log_lines(lines: Iterable[str]) -> str:
    return "\n".join(line.rstrip() for line in lines if line is not None)


def trim_log(log_text: str, max_chars: int = 4000) -> str:
    if len(log_text) <= max_chars:
        return log_text
    return f"{log_text[:max_chars]}\n...[truncated]"


def save_stage_log(workspace: str, stage: str, filename: str, content: str) -> str:
    manager = WorkspaceManager(workspace)
    path = manager.write_stage_text("logs", f"{stage}_{filename}", trim_log(content))
    return str(path)

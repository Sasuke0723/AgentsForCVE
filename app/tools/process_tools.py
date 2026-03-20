"""计划功能：进程执行工具，负责以受控方式运行本地命令并收集退出码、标准输出和错误输出。"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence

from app.config import DEFAULT_TIMEOUT_SECONDS


def run_command(
    command: Sequence[str],
    *,
    cwd: str | Path | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict:
    completed = subprocess.run(
        list(command),
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "command": list(command),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "success": completed.returncode == 0,
    }

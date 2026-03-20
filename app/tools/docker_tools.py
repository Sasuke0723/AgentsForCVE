"""计划功能：Docker 执行工具，负责构建镜像、运行容器并收集容器内构建与复现结果。"""

from __future__ import annotations

from app.tools.log_tools import join_log_lines


def mock_build_image(tag: str, dockerfile_path: str, build_script_path: str) -> dict:
    logs = join_log_lines(
        [
            f"[mock-docker] image tag: {tag}",
            f"[mock-docker] dockerfile: {dockerfile_path}",
            f"[mock-docker] build script: {build_script_path}",
            "[mock-docker] build completed successfully",
        ]
    )
    return {"success": True, "logs": logs}


def mock_run_container(tag: str, script_path: str) -> dict:
    logs = join_log_lines(
        [
            f"[mock-docker] image tag: {tag}",
            f"[mock-docker] run script: {script_path}",
            "[mock-docker] command executed successfully",
        ]
    )
    return {"success": True, "logs": logs}

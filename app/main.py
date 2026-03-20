"""计划功能：项目命令行入口，负责加载任务、初始化运行状态并启动 LangGraph 主流程。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

from app.config import DEFAULT_TASK_FILE
from app.orchestrator.graph import build_app_graph
from app.schemas.task import TaskModel


def load_task_data(task_path: str | Path) -> dict:
    path = Path(task_path)
    raw_text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(raw_text)
    return json.loads(raw_text)


def serialize_state(state: dict) -> dict:
    serialized = {}
    for key, value in state.items():
        if hasattr(value, "model_dump"):
            serialized[key] = value.model_dump()
        else:
            serialized[key] = value
    return serialized


def build_initial_state(task: TaskModel) -> dict:
    return {
        "task": task,
        "workspace": f"workspaces/{task.task_id}",
        "retry_count": {},
        "stage_history": [],
        "current_stage": "knowledge",
        "final_status": "running",
    }


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Run the AgentsForCVE mock MVP pipeline.")
    parser.add_argument(
        "--task",
        default=str(DEFAULT_TASK_FILE),
        help="Path to the task YAML/JSON file.",
    )
    args = parser.parse_args(argv)

    task_data = load_task_data(args.task)

    task = TaskModel(**task_data)
    graph = build_app_graph()
    initial_state = build_initial_state(task)
    result = graph.invoke(initial_state)
    print(json.dumps(serialize_state(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

"""计划功能：参考链接提取工具，负责从 CVE 页面、公告或仓库信息中抽取可继续跟进的链接。"""

from __future__ import annotations

from app.schemas.task import TaskModel


def collect_references(task: TaskModel) -> list[str]:
    candidates = [task.cve_url, task.repo_url, *task.references]
    references: list[str] = []
    for item in candidates:
        if item and item not in references:
            references.append(item)
    return references

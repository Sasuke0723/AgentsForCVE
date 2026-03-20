"""计划功能：补丁处理工具，负责读取、解析和整理漏洞修复补丁，供后续构建与验证阶段使用。"""

from __future__ import annotations


def summarize_patch(vulnerable_ref: str | None, fixed_ref: str | None) -> str:
    return (
        "Mock patch summary:\n"
        f"- vulnerable_ref: {vulnerable_ref or 'unknown'}\n"
        f"- fixed_ref: {fixed_ref or 'unknown'}\n"
        "- changed_files: inferred later"
    )

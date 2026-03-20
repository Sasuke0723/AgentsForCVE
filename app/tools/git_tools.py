"""计划功能：Git 操作工具，负责克隆仓库、切换漏洞版本/修复版本并导出差异信息。"""

from __future__ import annotations


def build_checkout_summary(repo_url: str | None, vulnerable_ref: str | None, fixed_ref: str | None) -> str:
    repo = repo_url or "unknown-repo"
    vulnerable = vulnerable_ref or "unknown-vulnerable-ref"
    fixed = fixed_ref or "unknown-fixed-ref"
    return (
        f"repo={repo}\n"
        f"vulnerable_ref={vulnerable}\n"
        f"fixed_ref={fixed}\n"
        "mode=mock"
    )

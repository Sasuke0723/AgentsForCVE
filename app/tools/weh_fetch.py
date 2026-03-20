"""计划功能：网页抓取工具，负责下载漏洞相关页面原文并转换为统一的抓取结果结构。"""

from __future__ import annotations

from app.schemas.fetched_page import FetchedPage


def fetch_pages(urls: list[str], cve_id: str) -> list[FetchedPage]:
    pages: list[FetchedPage] = []
    for index, url in enumerate(urls, start=1):
        pages.append(
            FetchedPage(
                url=url,
                title=f"{cve_id} reference {index}",
                raw_html=f"<html><body><h1>{cve_id}</h1><p>{url}</p></body></html>",
                raw_text=(
                    f"{cve_id} reference source\n"
                    f"url: {url}\n"
                    "This is a local mock fetch result for offline MVP execution."
                ),
                out_links=[],
            )
        )
    return pages

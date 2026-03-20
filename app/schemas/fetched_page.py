"""计划功能：定义网页抓取结果结构，保存原始页面内容和可继续跟踪的外链信息。"""
from typing import List

from app.compat import BaseModel


class FetchedPage(BaseModel):

    url: str

    title: str

    raw_html: str

    raw_text: str

    out_links: List[str]

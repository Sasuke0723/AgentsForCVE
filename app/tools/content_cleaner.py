"""计划功能：内容清洗工具，负责去除网页噪音并整理出适合输入模型的漏洞知识文本。"""

import re


def clean_text(raw_text: str) -> str:
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()

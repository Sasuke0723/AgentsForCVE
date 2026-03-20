"""计划功能：评审智能体，负责对阶段产物进行质量审查并提出修正建议或风险提示。"""


class CriticAgent:
    def review(self, stage: str, artifact: dict) -> dict:
        issues = []
        if not artifact:
            issues.append("产物为空，无法进入下一阶段。")
        return {
            "stage": stage,
            "passed": not issues,
            "issues": issues,
            "summary": "通过最小检查。" if not issues else "发现需要补充的内容。",
        }

"""计划功能：验证阶段智能体，负责综合前后版本运行日志判断漏洞是否被稳定触发与修复。"""
from app.config import PROMPTS_DIR
from app.schemas.knowledge import KnowledgeModel
from app.schemas.poc_artifact import PoCArtifact
from app.schemas.verify_result import VerifyResult
from app.tools.file_tools import WorkspaceManager, read_text
from app.tools.log_tools import join_log_lines, save_stage_log


class VerifierAgent:
    def render_prompt(self, pre_log: str, post_log: str, knowledge: KnowledgeModel) -> str:
        prompt_prefix = read_text(PROMPTS_DIR / "verifier_prompt.md")
        return f"""
{prompt_prefix}

EXPECTED ERROR PATTERNS:
{knowledge.expected_error_patterns}

EXPECTED STACK KEYWORDS:
{knowledge.expected_stack_keywords}

PRE PATCH LOG:
{pre_log}

POST PATCH LOG:
{post_log}
""".strip()

    def run(self, knowledge: KnowledgeModel, poc: PoCArtifact, workspace: str) -> VerifyResult:
        manager = WorkspaceManager(workspace)
        manager.ensure()

        pre_log = manager.read_stage_text("poc", "pre_patch.log")
        post_log = manager.read_stage_text("poc", "post_patch.log")
        prompt = self.render_prompt(pre_log=pre_log, post_log=post_log, knowledge=knowledge)

        matched_error_patterns = [
            pattern for pattern in knowledge.expected_error_patterns if pattern and pattern in pre_log
        ]
        matched_stack_keywords = [
            keyword for keyword in knowledge.expected_stack_keywords if keyword and keyword in pre_log
        ]

        pre_patch_triggered = bool(matched_error_patterns)
        post_patch_clean = not any(
            pattern and pattern in post_log for pattern in knowledge.expected_error_patterns
        )
        verdict = "success" if pre_patch_triggered and post_patch_clean else "failed"
        reason = (
            "修复前成功触发漏洞，修复后日志未再出现预期错误模式。"
            if verdict == "success"
            else "日志不满足最小差分验证条件。"
        )

        result = VerifyResult(
            pre_patch_triggered=pre_patch_triggered,
            post_patch_clean=post_patch_clean,
            matched_error_patterns=matched_error_patterns,
            matched_stack_keywords=matched_stack_keywords,
            verdict=verdict,
            reason=reason,
        )

        manager.write_stage_text("verify", "prompt.txt", prompt)
        manager.write_stage_json("verify", "result.json", result.model_dump())
        save_stage_log(
            workspace,
            "verify",
            "summary.log",
            join_log_lines(
                [
                    f"verdict={verdict}",
                    f"pre_patch_triggered={pre_patch_triggered}",
                    f"post_patch_clean={post_patch_clean}",
                    f"matched_error_patterns={matched_error_patterns}",
                    f"matched_stack_keywords={matched_stack_keywords}",
                    f"poc_execution_success={poc.execution_success}",
                ]
            ),
        )
        return result

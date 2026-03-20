"""计划功能：PoC 生成智能体，负责基于漏洞知识和构建产物生成最小复现代码与运行脚本。"""
from app.config import PROMPTS_DIR, TEMPLATES_DIR
from app.schemas.build_artifact import BuildArtifact
from app.schemas.knowledge import KnowledgeModel
from app.schemas.poc_artifact import PoCArtifact
from app.tools.docker_tools import mock_run_container
from app.tools.file_tools import WorkspaceManager, read_text, render_template
from app.tools.log_tools import join_log_lines, save_stage_log


class PoCAgent:
    def render_prompt(self, knowledge: KnowledgeModel, build: BuildArtifact) -> str:
        prompt_prefix = read_text(PROMPTS_DIR / "poc_prompt.md")
        return f"""
{prompt_prefix}

KNOWLEDGE:
{knowledge.model_dump_json(indent=2)}

BUILD:
{build.model_dump_json(indent=2)}
""".strip()

    def run(self, knowledge: KnowledgeModel, build: BuildArtifact, workspace: str) -> PoCArtifact:
        manager = WorkspaceManager(workspace)
        manager.ensure()

        expected_pattern = knowledge.expected_error_patterns[0] if knowledge.expected_error_patterns else "mock-error"
        poc_content = (
            "# mock poc\n"
            f"print('triggering {knowledge.cve_id}')\n"
            "print('payload prepared')\n"
        )
        run_commands = [
            f"echo '[mock-poc] running for {knowledge.cve_id}'",
            f"echo '[mock-poc] expecting {expected_pattern}'",
        ]

        run_template = read_text(TEMPLATES_DIR / "run.sh.j2")
        run_script_content = render_template(
            run_template,
            {"run_commands": "\n".join(run_commands)},
        )

        prompt = self.render_prompt(knowledge, build)
        poc_path = manager.write_stage_text("poc", "poc.py", poc_content)
        run_script_path = manager.write_stage_text("poc", "run.sh", run_script_content)

        pre_patch_log = join_log_lines(
            [
                f"[pre-patch] {knowledge.cve_id} triggered",
                f"[pre-patch] error={expected_pattern}",
                "[pre-patch] stack=mock_target -> trigger_vulnerability",
            ]
        )
        post_patch_log = join_log_lines(
            [
                f"[post-patch] {knowledge.cve_id} executed",
                "[post-patch] no vulnerability triggered",
                "[post-patch] status=clean",
            ]
        )
        manager.write_stage_text("poc", "pre_patch.log", pre_patch_log)
        manager.write_stage_text("poc", "post_patch.log", post_patch_log)

        run_result = mock_run_container(
            tag=f"{knowledge.cve_id.lower()}-mock-build",
            script_path=str(run_script_path),
        )
        execution_logs = join_log_lines([run_result["logs"], pre_patch_log, post_patch_log])

        artifact = PoCArtifact(
            poc_filename=poc_path.name,
            poc_content=poc_content,
            run_script_content=run_script_content,
            input_files=[],
            expected_error_patterns=knowledge.expected_error_patterns,
            execution_success=run_result["success"],
            execution_logs=execution_logs,
        )

        manager.write_stage_text("poc", "prompt.txt", prompt)
        manager.write_stage_json("poc", "artifact.json", artifact.model_dump())
        save_stage_log(workspace, "poc", "execution.log", execution_logs)
        return artifact

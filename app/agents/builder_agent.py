"""计划功能：构建环境智能体，负责生成 Dockerfile、构建脚本并组织漏洞版本的编译过程。"""
from app.config import PROMPTS_DIR, TEMPLATES_DIR
from app.schemas.build_artifact import BuildArtifact
from app.schemas.knowledge import KnowledgeModel
from app.tools.docker_tools import mock_build_image
from app.tools.file_tools import WorkspaceManager, read_text, render_template
from app.tools.git_tools import build_checkout_summary
from app.tools.log_tools import join_log_lines, save_stage_log


class BuilderAgent:
    def render_prompt(self, knowledge: KnowledgeModel) -> str:
        prompt_prefix = read_text(PROMPTS_DIR / "builder_prompt.md")
        return f"""
{prompt_prefix}

{knowledge.model_dump_json(indent=2)}
""".strip()

    def run(self, knowledge: KnowledgeModel, workspace: str) -> BuildArtifact:
        manager = WorkspaceManager(workspace)
        manager.ensure()

        install_packages = ["build-essential"] if knowledge.vulnerability_type == "memory-corruption" else ["python3"]
        build_commands = [
            "echo '[mock-build] preparing source tree'",
            "echo '[mock-build] compiling vulnerable target'",
            "mkdir -p /workspace/bin",
            "echo 'mock-binary' > /workspace/bin/mock_target",
        ]

        dockerfile_template = read_text(TEMPLATES_DIR / "Dockerfile.j2")
        build_template = read_text(TEMPLATES_DIR / "build.sh.j2")
        dockerfile_content = render_template(
            dockerfile_template,
            {"packages": " ".join(install_packages)},
        )
        build_script_content = render_template(
            build_template,
            {"build_commands": "\n".join(build_commands)},
        )

        prompt = self.render_prompt(knowledge)
        dockerfile_path = manager.write_stage_text("build", "Dockerfile", dockerfile_content)
        build_script_path = manager.write_stage_text("build", "build.sh", build_script_content)

        checkout_summary = build_checkout_summary(
            knowledge.repo_url,
            knowledge.vulnerable_ref,
            knowledge.fixed_ref,
        )
        docker_result = mock_build_image(
            tag=f"{knowledge.cve_id.lower()}-mock-build",
            dockerfile_path=str(dockerfile_path),
            build_script_path=str(build_script_path),
        )
        build_logs = join_log_lines([checkout_summary, docker_result["logs"]])

        artifact = BuildArtifact(
            dockerfile_content=dockerfile_content,
            build_script_content=build_script_content,
            install_packages=install_packages,
            build_commands=build_commands,
            expected_binary_path="/workspace/bin/mock_target",
            sanitizer_enabled=knowledge.vulnerability_type == "memory-corruption",
            build_success=docker_result["success"],
            build_logs=build_logs,
        )

        manager.write_stage_text("build", "prompt.txt", prompt)
        manager.write_stage_json("build", "artifact.json", artifact.model_dump())
        save_stage_log(workspace, "build", "build.log", build_logs)
        return artifact

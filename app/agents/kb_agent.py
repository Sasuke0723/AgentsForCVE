"""计划功能：知识采集智能体，负责聚合漏洞资料并生成结构化的 KnowledgeModel。"""
from pathlib import Path

from app.config import PROMPTS_DIR
from app.schemas.knowledge import KnowledgeModel
from app.schemas.knowledgeDocument import KnowledgeDocument
from app.schemas.task import TaskModel
from app.tools.content_cleaner import clean_text
from app.tools.file_tools import WorkspaceManager, read_text
from app.tools.log_tools import join_log_lines, save_stage_log
from app.tools.reference_extractor import collect_references
from app.tools.weh_fetch import fetch_pages


class KBAgent:
    def render_prompt(self, task: TaskModel, documents: str) -> str:
        prompt_prefix = read_text(PROMPTS_DIR / "kb_prompt.md")
        return f"""
{prompt_prefix}

CVE ID: {task.cve_id}
DOCUMENTS:
{documents}
""".strip()

    def run(self, task: TaskModel, workspace: str) -> KnowledgeModel:
        manager = WorkspaceManager(workspace)
        manager.ensure()

        references = collect_references(task)
        fetched_pages = fetch_pages(references, task.cve_id)

        documents = [
            KnowledgeDocument(
                url=page.url,
                title=page.title,
                cleaned_text=clean_text(page.raw_text),
            )
            for page in fetched_pages
        ]
        merged_documents = "\n\n".join(document.cleaned_text for document in documents)
        prompt = self.render_prompt(task=task, documents=merged_documents or "No documents.")

        language = (task.language or "unknown").lower()
        vulnerability_type = "memory-corruption" if language in {"c", "c++", "cpp"} else "application-error"
        expected_error = "heap-buffer-overflow" if vulnerability_type == "memory-corruption" else "unhandled-exception"
        affected_files = ["src/mock_target.c"] if vulnerability_type == "memory-corruption" else ["app/mock_target.py"]

        knowledge = KnowledgeModel(
            cve_id=task.cve_id,
            summary=f"{task.cve_id} 的离线演示知识，由本地 mock 流程根据任务信息生成。",
            vulnerability_type=vulnerability_type,
            repo_url=task.repo_url,
            vulnerable_ref=task.vulnerable_ref,
            fixed_ref=task.fixed_ref,
            affected_files=affected_files,
            reproduction_hints=[
                "先执行 build 阶段生成最小构建环境。",
                "再执行 poc 阶段触发预期错误模式并保留前后日志。",
            ],
            expected_error_patterns=[expected_error, task.cve_id.lower()],
            expected_stack_keywords=["mock_target", "trigger_vulnerability"],
            references=references,
        )

        manager.write_stage_text("knowledge", "prompt.txt", prompt)
        manager.write_stage_json(
            "knowledge",
            "fetched_pages.json",
            [page.model_dump() for page in fetched_pages],
        )
        manager.write_stage_json(
            "knowledge",
            "documents.json",
            [document.model_dump() for document in documents],
        )
        manager.write_stage_json("knowledge", "knowledge.json", knowledge.model_dump())

        save_stage_log(
            workspace,
            "knowledge",
            "summary.log",
            join_log_lines(
                [
                    f"task_id={task.task_id}",
                    f"cve_id={task.cve_id}",
                    f"references={len(references)}",
                    f"documents={len(documents)}",
                    f"vulnerability_type={knowledge.vulnerability_type}",
                ]
            ),
        )
        return knowledge

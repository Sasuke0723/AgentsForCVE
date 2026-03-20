"""计划功能：验证各阶段 Pydantic schema 的字段约束、序列化行为和兼容性。"""

import unittest

from app.schemas.build_artifact import BuildArtifact
from app.schemas.knowledge import KnowledgeModel
from app.schemas.poc_artifact import PoCArtifact
from app.schemas.task import TaskModel
from app.schemas.verify_result import VerifyResult


class SchemaTests(unittest.TestCase):
    def test_task_model_defaults(self):
        task = TaskModel(task_id="t1", cve_id="CVE-1")
        self.assertEqual(task.references, [])
        self.assertIsNone(task.repo_url)

    def test_knowledge_dump_contains_expected_fields(self):
        knowledge = KnowledgeModel(
            cve_id="CVE-1",
            summary="summary",
            vulnerability_type="memory-corruption",
        )
        dumped = knowledge.model_dump()
        self.assertEqual(dumped["cve_id"], "CVE-1")
        self.assertIn("expected_error_patterns", dumped)

    def test_artifacts_and_verify_result_dump(self):
        build = BuildArtifact(dockerfile_content="FROM x", build_script_content="echo build")
        poc = PoCArtifact(poc_filename="poc.py", poc_content="print(1)", run_script_content="echo run")
        verify = VerifyResult(
            pre_patch_triggered=True,
            post_patch_clean=True,
            verdict="success",
            reason="ok",
        )
        self.assertFalse(build.build_success)
        self.assertFalse(poc.execution_success)
        self.assertEqual(verify.model_dump()["verdict"], "success")


if __name__ == "__main__":
    unittest.main()

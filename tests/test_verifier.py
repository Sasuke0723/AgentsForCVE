"""计划功能：验证 verifier 相关逻辑是否能根据日志和知识特征输出正确的验证结论。"""

import shutil
import unittest
from pathlib import Path

from app.agents.verifier_agent import VerifierAgent
from app.schemas.knowledge import KnowledgeModel
from app.schemas.poc_artifact import PoCArtifact
from app.tools.file_tools import WorkspaceManager


class VerifierAgentTests(unittest.TestCase):
    def setUp(self):
        self.workspace = "workspaces/test-verifier"
        shutil.rmtree(Path(self.workspace), ignore_errors=True)
        manager = WorkspaceManager(self.workspace)
        manager.ensure()
        manager.write_stage_text(
            "poc",
            "pre_patch.log",
            "[pre-patch] error=heap-buffer-overflow\n[pre-patch] stack=mock_target -> trigger_vulnerability",
        )
        manager.write_stage_text(
            "poc",
            "post_patch.log",
            "[post-patch] status=clean",
        )

    def tearDown(self):
        shutil.rmtree(Path(self.workspace), ignore_errors=True)

    def test_verifier_returns_success_for_clean_post_patch_log(self):
        knowledge = KnowledgeModel(
            cve_id="CVE-1",
            summary="summary",
            vulnerability_type="memory-corruption",
            expected_error_patterns=["heap-buffer-overflow"],
            expected_stack_keywords=["mock_target"],
        )
        poc = PoCArtifact(
            poc_filename="poc.py",
            poc_content="print(1)",
            run_script_content="echo run",
            execution_success=True,
        )

        result = VerifierAgent().run(knowledge=knowledge, poc=poc, workspace=self.workspace)

        self.assertEqual(result.verdict, "success")
        self.assertTrue(result.pre_patch_triggered)
        self.assertTrue(result.post_patch_clean)


if __name__ == "__main__":
    unittest.main()

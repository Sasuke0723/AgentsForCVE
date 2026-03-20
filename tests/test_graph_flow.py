"""计划功能：验证主流程图在 mock 模式下可以从 knowledge 顺利运行到 verify。"""

import shutil
import unittest
from pathlib import Path

from app.main import build_initial_state
from app.orchestrator.graph import build_app_graph
from app.schemas.task import TaskModel


class GraphFlowTests(unittest.TestCase):
    def setUp(self):
        self.workspace = Path("workspaces/test-graph-flow")
        shutil.rmtree(self.workspace, ignore_errors=True)

    def tearDown(self):
        shutil.rmtree(self.workspace, ignore_errors=True)

    def test_mock_graph_flow_reaches_success(self):
        task = TaskModel(
            task_id="test-graph-flow",
            cve_id="CVE-2099-1000",
            cve_url="https://example.com/cve/CVE-2099-1000",
            repo_url="https://github.com/example/mock-vuln-project",
            vulnerable_ref="v1.0.0",
            fixed_ref="v1.0.1",
            language="C",
            references=["https://example.com/advisory"],
        )
        graph = build_app_graph()
        result = graph.invoke(build_initial_state(task))

        self.assertEqual(result["final_status"], "success")
        self.assertEqual(result["verify"].verdict, "success")
        self.assertEqual(len(result["stage_history"]), 4)


if __name__ == "__main__":
    unittest.main()

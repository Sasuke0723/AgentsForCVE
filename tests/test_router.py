"""计划功能：验证 graph 路由规则、重试次数判断与终止条件是否符合预期。"""

import unittest

from app.orchestrator.routers import route_after_build, route_after_poc, route_after_verify
from app.schemas.build_artifact import BuildArtifact
from app.schemas.poc_artifact import PoCArtifact
from app.schemas.verify_result import VerifyResult


class RouterTests(unittest.TestCase):
    def test_route_after_build_success(self):
        state = {
            "build": BuildArtifact(
                dockerfile_content="x",
                build_script_content="y",
                build_success=True,
            )
        }
        self.assertEqual(route_after_build(state), "poc")

    def test_route_after_build_retry(self):
        state = {"retry_count": {"build": 1}}
        self.assertEqual(route_after_build(state), "build")

    def test_route_after_poc_success(self):
        state = {
            "poc": PoCArtifact(
                poc_filename="poc.py",
                poc_content="print(1)",
                run_script_content="echo run",
                execution_success=True,
            )
        }
        self.assertEqual(route_after_poc(state), "verify")

    def test_route_after_verify_success(self):
        state = {
            "verify": VerifyResult(
                pre_patch_triggered=True,
                post_patch_clean=True,
                verdict="success",
                reason="ok",
            )
        }
        self.assertEqual(route_after_verify(state), "success")


if __name__ == "__main__":
    unittest.main()

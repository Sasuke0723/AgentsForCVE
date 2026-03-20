"""计划功能：验证 Docker 工具层的构建、运行和日志采集接口在最小场景下可正常工作。"""

import unittest

from app.tools.docker_tools import mock_build_image, mock_run_container


class DockerToolTests(unittest.TestCase):
    def test_mock_build_image(self):
        result = mock_build_image("demo", "Dockerfile", "build.sh")
        self.assertTrue(result["success"])
        self.assertIn("build completed successfully", result["logs"])

    def test_mock_run_container(self):
        result = mock_run_container("demo", "run.sh")
        self.assertTrue(result["success"])
        self.assertIn("command executed successfully", result["logs"])


if __name__ == "__main__":
    unittest.main()

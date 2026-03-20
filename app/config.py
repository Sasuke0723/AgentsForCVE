"""计划功能：集中管理项目配置项，例如模型参数、目录路径、超时、重试策略与外部服务开关。"""

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "app"
DATA_DIR = ROOT_DIR / "data"
TASKS_DIR = DATA_DIR / "tasks"
SAMPLES_DIR = DATA_DIR / "samples"
WORKSPACES_DIR = ROOT_DIR / "workspaces"
REPORTS_DIR = ROOT_DIR / "reports"
PROMPTS_DIR = APP_DIR / "prompts"
TEMPLATES_DIR = APP_DIR / "templates"

DEFAULT_TASK_FILE = TASKS_DIR / "demo.yaml"
DEFAULT_TIMEOUT_SECONDS = 15
DEFAULT_ENCODING = "utf-8"
DEFAULT_WORKSPACE_STAGES = ("knowledge", "build", "poc", "verify", "logs")

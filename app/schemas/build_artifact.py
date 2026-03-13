from pydantic import BaseModel, Field
from typing import List, Optional


class BuildArtifact(BaseModel):
    dockerfile_content: str
    build_script_content: str
    run_env_script_content: Optional[str] = None
    install_packages: List[str] = Field(default_factory=list)
    build_commands: List[str] = Field(default_factory=list)
    expected_binary_path: Optional[str] = None
    sanitizer_enabled: bool = False
    build_success: bool = False
    build_logs: str = ""
from pydantic import BaseModel, Field
from typing import List


class PoCArtifact(BaseModel):
    poc_filename: str
    poc_content: str
    run_script_content: str
    input_files: List[str] = Field(default_factory=list)
    expected_error_patterns: List[str] = Field(default_factory=list)
    expected_stack_keywords: List[str] = Field(default_factory=list)
    execution_success: bool = False
    execution_logs: str = ""
from pydantic import BaseModel, Field
from typing import List


class VerifyResult(BaseModel):
    pre_patch_triggered: bool = False
    post_patch_clean: bool = False
    matched_error_patterns: List[str] = Field(default_factory=list)
    matched_stack_keywords: List[str] = Field(default_factory=list)
    verdict: str
    reason: str
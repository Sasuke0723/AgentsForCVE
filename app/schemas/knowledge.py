from pydantic import BaseModel, Field
from typing import List, Optional


class KnowledgeModel(BaseModel):
    cve_id: str
    summary: str
    repo_url: str
    language: str
    vulnerability_type: str
    vulnerable_ref: Optional[str] = None
    fixed_ref: Optional[str] = None
    affected_files: List[str] = Field(default_factory=list)
    reproduction_hints: List[str] = Field(default_factory=list)
    sanitizer: Optional[str] = None
    expected_error_patterns: List[str] = Field(default_factory=list)
    expected_stack_keywords: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
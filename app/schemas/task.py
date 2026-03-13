from pydantic import BaseModel, Field
from typing import List, Optional


class TaskModel(BaseModel):
    task_id: str
    cve_id: str
    repo_url: Optional[str] = None
    language: Optional[str] = None
    vulnerable_ref: Optional[str] = None
    fixed_ref: Optional[str] = None
    target_binary: Optional[str] = None
    vulnerability_type: Optional[str] = None
    references: List[str] = Field(default_factory=list)
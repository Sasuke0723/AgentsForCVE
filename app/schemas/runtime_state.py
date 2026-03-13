from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class RuntimeState(BaseModel):
    task_id: str
    current_stage: str = "knowledge"
    retry_count: Dict[str, int] = Field(default_factory=dict)
    stage_history: List[dict] = Field(default_factory=list)
    last_error: Optional[str] = None
    workspace: Optional[str] = None
    final_status: str = "running"
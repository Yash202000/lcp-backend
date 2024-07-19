# schemas.py
from pydantic import BaseModel
from typing import Optional

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: str
    project_scope: str
    starred: str
    in_progress: Optional[bool] = True

class ProjectCreate(ProjectBase):
    user_id: int

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    user_id: int
    project_schema: str

    class Config:
        orm_mode: True

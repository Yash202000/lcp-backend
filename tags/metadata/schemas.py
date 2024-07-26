from pydantic import BaseModel
from typing import List, Optional

class ForeignKeyCreate(BaseModel):
    referenced_table: str
    referenced_column: str

class ColumnCreate(BaseModel):
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: Optional[str] = None  # Using Optional[str] to allow for nullable default values
    autoincrement: bool = False
    foreign_key: Optional[ForeignKeyCreate] = None

class TableCreate(BaseModel):
    name: str
    columns: List[ColumnCreate]

class CreateTableRequest(BaseModel):
    user_id: int
    table: TableCreate



class ForeignKeyMetadataCreate(BaseModel):
    referenced_table: str
    referenced_column: str

class ColumnMetadataCreate(BaseModel):
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[ForeignKeyMetadataCreate] = None

class TableMetadataCreate(BaseModel):
    name: str
    columns: List[ColumnMetadataCreate]
    project_id: int

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: str
    project_scope: str
    starred: str
    in_progress: bool = True
    user_id: int
    project_schema: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[str] = None
    project_scope: Optional[str] = None
    starred: Optional[str] = None
    in_progress: Optional[bool] = None
    user_id: Optional[int] = None
    project_schema: Optional[str] = None
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
    foreign_key: Optional[ForeignKeyCreate] = None

class TableCreate(BaseModel):
    name: str
    columns: List[ColumnCreate]

class CreateTableRequest(BaseModel):
    user_id: int
    table: TableCreate

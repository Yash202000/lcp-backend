from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db_connections import get_db
from . import schemas, crud


table_router = APIRouter(
    prefix="/api",
    tags=['Table']
)

@table_router.get("/projects/test/trigger")
def trigger_create_function( db: Session = Depends(get_db)):
    output = crud.create_python_function()
    
    return output

#     output = crud.create_python_function()
#     return {"message": "function Created successfully"}

@table_router.post("/projects/{project_id}/tables/")
def create_table(project_id: int, table_request: schemas.CreateTableRequest, db: Session = Depends(get_db)):
    table_metadata = crud.create_project_table(db, project_id, table_request)
    return {"message": "Table created successfully", "table": table_metadata.name}

# @table_router.get("/projects/create_function")
# def create_function( db: Session = Depends(get_db)):
#     output = crud.create_python_function()
#     return {"message": "function Created successfully"}
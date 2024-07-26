from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db_connections import get_db
from . import schemas, crud


table_router = APIRouter(
    prefix="/api",
    tags=['Table']
)


@table_router.get("/projects/{project_id}/tables/")
def get_all_project_tables(project_id: int, db: Session = Depends(get_db)):
    return crud.get_all_project_tables(db, project_id)
    

@table_router.get('/projects/{project_id}/tables/{table_id}')
def get_all_table_details_for_tableid(project_id: int, table_id: int, db: Session = Depends(get_db)):
    return crud.get_table_with_columns_and_foreign_keys(db,project_id, table_id)


@table_router.post("/projects/{project_id}/tables/")
def create_table(project_id: int, table_request: schemas.CreateTableRequest, db: Session = Depends(get_db)):
    table_metadata = crud.create_project_table(db, project_id, table_request)
    return {"message": "Table created successfully", "data": table_metadata}









# @table_router.get("/projects/create_function")
# def create_function( db: Session = Depends(get_db)):
#     output = crud.create_python_function()
#     return {"message": "function Created successfully"}
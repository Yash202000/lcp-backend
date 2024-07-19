# routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, HTTPException, Request
from sqlalchemy.orm import Session
from . import crud, schemas
from db_connections import get_db



project_router = APIRouter(
    prefix="/api",
    tags=['Projects']
)


@project_router.post("/v1/projects/", summary="Project creation",
    status_code=status.HTTP_201_CREATED, response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db=db, project=project)

@project_router.get("/v1/projects/{project_id}",summary="Get perticular project",
    status_code=status.HTTP_200_OK, response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@project_router.get("/v1/projects/",summary="Get all Projects",
    status_code=status.HTTP_200_OK, response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects

@project_router.put("/v1/projects/{project_id}",summary="Update project",
    status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = crud.update_project(db, project_id=project_id, project=project)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@project_router.delete("/v1/projects/{project_id}",summary="Delete Project",
    status_code=status.HTTP_200_OK, response_model=schemas.Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.delete_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

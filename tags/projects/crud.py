# crud.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import  schemas
from models.public.public_models import  Project
from utils.db_schema_utils import check_and_create_schema
from tags.n_helpers.crud import create_n_project

def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    temp_project = db.query(Project).filter(Project.name == project.name , Project.user_id==project.user_id).first()
    
    if temp_project:
        raise HTTPException(status_code=404, detail="Project already exist")
    
    db_project = Project(
        name=project.name,
        description=project.description,
        project_type=project.project_type,
        project_scope=project.project_scope,
        starred=project.starred,
        in_progress=project.in_progress,
        user_id=project.user_id,
        project_schema=f"project-{project.user_id}-{project.name}"
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    check_and_create_schema(db_project.project_schema)
    
    create_n_project(db_project.project_schema, db_project.description)
    
    return db_project

def update_project(db: Session, project_id: int, project: schemas.ProjectUpdate):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project:
        for key, value in project.dict().items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return db_project

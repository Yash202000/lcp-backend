from fastapi import HTTPException
from sqlalchemy import DateTime, Table, Column, Integer, String, Boolean, MetaData, ForeignKey,func
from sqlalchemy.orm import Session
from . import schemas
from models.public.public_models import API, APIGroup, TableMetadata, ColumnMetadata, ForeignKeyMetadata , Project
from tags.n_helpers.crud import create_python_function


def get_column_type(column_type: str):
    column_type_mapping = {
        "Integer": Integer,
        "String": String,
        "Boolean": Boolean,
        # Add more mappings as needed
    }
    return column_type_mapping.get(column_type, String)

def create_table_in_schema(db: Session, schema_name: str, table_schema: schemas.TableCreate):
    meta = MetaData(schema=schema_name)
    columns = []

    for col in table_schema.columns:
        if col.name=='created_at':
            continue
        column_type = get_column_type(col.type)
        column_kwargs = {
            'primary_key': col.primary_key,
            'nullable': col.nullable,
            'unique': col.unique,
            'default': col.default,
            'autoincrement': col.autoincrement
        }
        if col.foreign_key:
            foreign_key = ForeignKey(f"{schema_name}.{col.foreign_key.referenced_table}.{col.foreign_key.referenced_column}")
            columns.append(Column(col.name, column_type, foreign_key, **column_kwargs))
        else:
            columns.append(Column(col.name, column_type, **column_kwargs))
            
    # Add the created_at column
    created_at_column = Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
    columns.append(created_at_column)

    new_table = Table(table_schema.name, meta, *columns)
    meta.create_all(db.bind)

def create_project_table(db: Session, project_id: int, table_request: schemas.CreateTableRequest):
    # Validate project ownership
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None or project.user_id != table_request.user_id:
        raise HTTPException(status_code=404, detail="Project not found or access denied")

    # Create table in database
    schema_name = project.project_schema
    table = db.query(TableMetadata).filter(TableMetadata.name==table_request.table.name,TableMetadata.project_id==project_id).first()
    print(table)
    if table:
        raise HTTPException(status_code=404, detail="table already exist use update api to update table")
    
    create_table_in_schema(db, schema_name, table_request.table)

    # Store metadata
    table_metadata = TableMetadata(name=table_request.table.name, project_id=project_id)
    db.add(table_metadata)
    db.commit()
    db.refresh(table_metadata)

    for column in table_request.table.columns:
        column_metadata = ColumnMetadata(
            name=column.name,
            type=column.type,
            nullable=column.nullable,
            primary_key=column.primary_key,
            table_id=table_metadata.id
        )
        db.add(column_metadata)
        db.commit()
        db.refresh(column_metadata)

        if column.foreign_key:
            foreign_key_metadata = ForeignKeyMetadata(
                column_id=column_metadata.id,
                referenced_table=column.foreign_key.referenced_table,
                referenced_column=column.foreign_key.referenced_column
            )
            db.add(foreign_key_metadata)

    db.commit()
    
    try:
        n_response = create_python_function(schema_name=schema_name, table_name=table_request.table.name)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server failed to create the function")
    
    
    # make entry in the api group and then make entries in apis that this apis are created at the end create association
    # Create APIGroup
    api_group_name = f"{table_request.table.name}_group"
    api_group = APIGroup(
        name=api_group_name,
        description=f"API group for table {table_request.table.name}",
        project_id=project_id,
    )
    db.add(api_group)
    db.commit()
    db.refresh(api_group)

    # Create APIs for GET, POST, PUT, DELETE methods
    methods = ["GET", "POST", "PUT", "DELETE"]
    base_url = n_response['status']['externalInvocationUrls'][0]
    print(base_url)
    for method in methods:
        api = API(
            name=f"{method.lower()}_{table_request.table.name}",
            endpoint=f"{base_url}",
            method=method,
            description=f"{method} method for table {table_request.table.name}",
            api_group_id=api_group.id,
        )
        db.add(api)
        db.commit()
        db.refresh(api)

    # Associate APIGroup with the table
    table_metadata.api_groups.append(api_group)
    db.commit()
    
    
    return n_response
    
    
     



def get_table_with_columns_and_foreign_keys(db: Session, project_id: int, table_id: int):
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    
    table = db.query(TableMetadata).filter(TableMetadata.id == table_id).first()

    if not table:
        return None

    columns = []
    for column in table.columns:
        foreign_key = None
        if column.foreign_key:
            foreign_key = {
                "referenced_table": column.foreign_key.referenced_table,
                "referenced_column": column.foreign_key.referenced_column
            }
        columns.append({
            "id": column.id,
            "name": column.name,
            "type": column.type,
            "nullable": column.nullable,
            "primary_key": column.primary_key,
            "foreign_key": foreign_key
        })

    return {
        "table_id": table.id,
        "table_name": table.name,
        "columns": columns
    }


def get_all_project_tables(db: Session,project_id: int):
    
    return db.query(TableMetadata).filter(TableMetadata.project_id==project_id).all()


def update_table_metadata(db: Session, table_metadata_id: int, table_metadata: schemas.TableMetadataCreate):
    db_table_metadata = db.query(TableMetadata).filter(TableMetadata.id == table_metadata_id).first()
    if not db_table_metadata:
        raise HTTPException(status_code=404, detail="Table metadata not found")

    for key, value in table_metadata.dict().items():
        setattr(db_table_metadata, key, value)

    db.commit()
    db.refresh(db_table_metadata)
    return db_table_metadata

def delete_table_metadata(db: Session, table_metadata_id: int):
    db_table_metadata = db.query(TableMetadata).filter(TableMetadata.id == table_metadata_id).first()
    if not db_table_metadata:
        raise HTTPException(status_code=404, detail="Table metadata not found")

    db.delete(db_table_metadata)
    db.commit()
    return {"message": "Table metadata deleted successfully"}


def create_column_metadata(db: Session, column_metadata: schemas.ColumnMetadataCreate):
    db_column_metadata = ColumnMetadata(
        name=column_metadata.name,
        type=column_metadata.type,
        nullable=column_metadata.nullable,
        primary_key=column_metadata.primary_key,
        table_id=column_metadata.table_id
    )
    db.add(db_column_metadata)
    db.commit()
    db.refresh(db_column_metadata)
    return db_column_metadata



def get_columns_metadata(db: Session, skip: int = 0, limit: int = 10):
    return db.query(ColumnMetadata).offset(skip).limit(limit).all()

def get_column_metadata_by_id(db: Session, column_metadata_id: int):
    return db.query(ColumnMetadata).filter(ColumnMetadata.id == column_metadata_id).first()


def update_column_metadata(db: Session, column_metadata_id: int, column_metadata: schemas.ColumnMetadataCreate):
    db_column_metadata = db.query(ColumnMetadata).filter(ColumnMetadata.id == column_metadata_id).first()
    if not db_column_metadata:
        raise HTTPException(status_code=404, detail="Column metadata not found")

    for key, value in column_metadata.dict().items():
        setattr(db_column_metadata, key, value)

    db.commit()
    db.refresh(db_column_metadata)
    return db_column_metadata


def delete_column_metadata(db: Session, column_metadata_id: int):
    db_column_metadata = db.query(ColumnMetadata).filter(ColumnMetadata.id == column_metadata_id).first()
    if not db_column_metadata:
        raise HTTPException(status_code=404, detail="Column metadata not found")

    db.delete(db_column_metadata)
    db.commit()
    return {"message": "Column metadata deleted successfully"}






    
from fastapi import HTTPException
from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, ForeignKey
from sqlalchemy.orm import Session
from . import schemas
from models.public.public_models import TableMetadata, ColumnMetadata, ForeignKeyMetadata , Project
from security.settings import settings
import jinja2
import subprocess



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
        column_type = get_column_type(col.type)
        if col.foreign_key:
            foreign_key = ForeignKey(f"{schema_name}.{col.foreign_key.referenced_table}.{col.foreign_key.referenced_column}")
            columns.append(Column(col.name, column_type, foreign_key, primary_key=col.primary_key, nullable=col.nullable))
        else:
            columns.append(Column(col.name, column_type, primary_key=col.primary_key, nullable=col.nullable))

    new_table = Table(table_schema.name, meta, *columns)
    meta.create_all(db.bind)

def create_project_table(db: Session, project_id: int, table_request: schemas.CreateTableRequest):
    # Validate project ownership
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None or project.user_id != table_request.user_id:
        raise HTTPException(status_code=404, detail="Project not found or access denied")

    # Create table in database
    schema_name = project.project_schema
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
    return table_metadata


def execute_ssh_command(server, username, command):
    """
    Executes an SSH command on a remote server with password authentication.

    Args:
        server: The hostname or IP address of the remote server.
        username: The username for SSH login.
        password: The password for the username.
        command: The command to execute on the remote server.

    Returns:
        A tuple containing the return code of the subprocess and the captured output (stdout).

    Raises:
        subprocess.CalledProcessError: If the command execution fails.
    """

    # Build the SSH command with password argument
    ssh_command =  [
        "ssh", f"{username}@{server}", "-o", "StrictHostKeyChecking=No", r"-i C:\Users\Admin\Documents\id_rsa  ", command
    ]

    try:
        # Execute the SSH command with subprocess
        result = subprocess.run(ssh_command, capture_output=True, text=True)
        return result.returncode, result.stdout
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(f"SSH command failed: {e}") from e


def create_python_function():
    
    schema_name="project_2_test"
    table_name="product"
    
    namespace = "nuclio"
    filename_without_extension = "main"
    numWorkers = 1
    
    # 
    
    template_dir = "static/templates/nuclio/python"
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    
    
    template = env.get_template("crud_template.py.j2")
    rendered_function_content = template.render(
        n_database_url=settings.N_DATABASE_URL,
        schema_name=schema_name,
        table_name=table_name,
    )
    
    print(rendered_function_content)
    
    with open(f"test/main.py", "w") as f:
        f.write(rendered_function_content)
        f.close()
        
        
    dtemplate = env.get_template("dockerbuildfile.j2")
    rendered_dockerfile_content = dtemplate.render(    
        database_url = settings.N_DATABASE_URL
    )
    
    with open(f"test/Dockerfile", "w") as f:
        f.write(rendered_dockerfile_content)
        f.close()
        
    ftemplate = env.get_template("function.j2")
    rendered_configuration_content = ftemplate.render(    
        function_name = table_name,
        namespace = namespace,
        filename_without_extension = filename_without_extension,
        numWorkers = numWorkers
    )
    
    with open(f"test/function.yaml", "w") as f:
        f.write(rendered_configuration_content)
        f.close()
        
    rtemplate = env.get_template("requirements.j2")
    rendered_requirements_content = rtemplate.render(
        test=""
    )
    
    with open(f"test/requirements.txt", "w") as f:
        f.write(rendered_requirements_content)
        f.close()
        
        
    #
    server = "192.168.0.103"
    username = "ubuntu"
    command = "touch test-blabla.txt"  # Replace with your desired command

    try:
        return_code, output = execute_ssh_command(server, username, command)
        if return_code == 0:
            print("Command succeeded:", output)
        else:
            print(f"Command failed with return code: {return_code}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
            
    return "success!"
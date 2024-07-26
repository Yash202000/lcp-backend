from typing import Union
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, inspect, schema as sa_schema
from constants.plain_constants import PUBLIC_TENANT_SCHEMA
from database import engine

# Create a session factory
SessionLocal = sessionmaker(bind=engine)

def check_and_create_schema(schema: str):
    # Create a session
    session = SessionLocal()
    try:
        # Use SQLAlchemy inspector to check schema existence
        inspector = inspect(engine)
        if not inspector.has_schema(schema):
            # Create the schema if it doesn't exist
            session.execute(sa_schema.CreateSchema(schema))
            session.commit()
            print(f"Schema '{schema}' created.")
        else:
            print(f"Schema '{schema}' already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        # Close the session
        session.close()
        print("Session closed.")

def is_public_schema(schema: Union[str, None]):
    return schema is None or schema == PUBLIC_TENANT_SCHEMA



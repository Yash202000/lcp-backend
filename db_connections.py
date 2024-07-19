from typing import Optional

from starlette.requests import Request

from sqlalchemy         import  create_engine
from sqlalchemy.orm     import  sessionmaker
from constants.enums import FlavorType

from constants.plain_constants import DEFAULT_TENANT_SCHEMA, PUBLIC_TENANT_SCHEMA
from security.settings import settings

from database import engine, SessionLocal


def get_db_engine_connectable_with_schema(schema: Optional[str] = None):
    print("inside th g et db ngin connectialb eshcma")
    """
    generates a session connectable, any of db, schema should be given
    """
    
    session = engine
    if schema==None:
        connectable = session.execution_options(schema_translate_map={PUBLIC_TENANT_SCHEMA: schema})
    elif schema == DEFAULT_TENANT_SCHEMA:
        connectable = session.execution_options(schema_translate_map={DEFAULT_TENANT_SCHEMA: schema})
    else:
        connectable = session.execution_options(schema_translate_map={DEFAULT_TENANT_SCHEMA: schema})
    return connectable

# todo 
def get_db_session_with_public_schema(schema: Optional[str] = None):
    
    print("insdiet h ge db sseosin ")
    """
        This Function will change the schema to public in the db
    """
    
    connectable = get_db_engine_connectable_with_schema( schema=schema)
    # db = Session(autocommit=False, autoflush=False, bind=connectable)

    SessionLocal = sessionmaker(
        bind=connectable, autocommit=False, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        # db.connection(execution_options={"schema_translate_map": {None: schema}, "isolation_level": "READ UNCOMMITTED"})
        yield db
    except Exception as e:
        print(str(e))

    finally:
        print("I came for CLOSE2 option with schema-")
        # db.expire_all()
        db.close()


def get_public_schema_db(flavor: str = None):
    """
        This Function will change the schema to public in the db
    """
    connectable = get_db_engine_connectable_with_schema(schema=None)
    # db = Session(autocommit=False, autoflush=False, bind=connectable)

    SessionLocal = sessionmaker(
        bind=connectable, autocommit=False, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    # db.connection(execution_options={"schema_translate_map": {None: None}, "isolation_level": "READ UNCOMMITTED"})
    return db


def get_db_session_with_schema(flavor: str = None,schema: str = ''):
    """
        This Function will change the schema to public in the db
    """
    
    current_header = flavor
    connectable = get_db_engine_connectable_with_schema(current_header,schema=schema)
    # db = Session(autocommit=False, autoflush=False, bind=connectable)

    SessionLocal = sessionmaker(
        bind=connectable, autocommit=False, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    # db.connection(execution_options={"schema_translate_map": {None: schema}, "isolation_level": "READ UNCOMMITTED"})
    return db


def get_db(request: Request):
    tenant_schema = None
    connectable = get_db_engine_connectable_with_schema(schema=tenant_schema)
    # db = Session(autocommit=False, autoflush=False, bind=connectable)

    SessionLocal = sessionmaker(
        bind=connectable, autocommit=False, autoflush=False, expire_on_commit=False)
    db     = SessionLocal()
    try:
        # db.connection(execution_options={"schema_translate_map": {None: tenant_schema}, "isolation_level": "READ UNCOMMITTED"})
        yield db
    finally:
        # db.expire_all()
        db.close()

from typing import Union

import sqlalchemy

from constants.plain_constants import PUBLIC_TENANT_SCHEMA
from database import engine
from constants import enums


def check_and_create_schema(schema: str):

    session = engine

    if not session.dialect.has_schema(session, schema):
            session.execute(sqlalchemy.schema.CreateSchema(schema))


def is_public_schema(schema: Union[str, None]):
    if schema is None or schema == PUBLIC_TENANT_SCHEMA:
        return True
    return False


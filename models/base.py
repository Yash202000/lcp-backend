from sqlalchemy.sql import func
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String
)
from sqlalchemy.orm import declarative_mixin, declared_attr

from utils.get_random_id_string import get_random_uuid_string_for_primary_key


@declarative_mixin
class BaseMixin:
    __abstract__ = True

    id = Column(
        String(50), primary_key=True, index=True, nullable=False, unique=True,
        default=get_random_uuid_string_for_primary_key
    )
    is_active = Column(Boolean, server_default='t')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @declared_attr
    def __tablename__(cls):
        given_table_name = cls.__name__
        converted_table_name = ''.join(
            ['_' + char.lower() if char.isupper() else char for char in given_table_name]
        ).lstrip('_')
        converted_table_name += 's'
        return converted_table_name


class BaseMixinWithCreatedBy(BaseMixin):
    @declared_attr
    def created_by_id(cls):
        return Column(String(50), ForeignKey("users.id", ondelete='CASCADE'), nullable=True)

    @declared_attr
    def updated_by_id(cls):
        return Column(String(50), ForeignKey("users.id", ondelete='CASCADE'), nullable=True)

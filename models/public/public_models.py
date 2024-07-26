import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Table, Text, ForeignKey,Integer, func
from sqlalchemy.orm import relationship
from database import Base

# Association table for many-to-many relationship between APIGroup and TableMetadata
api_group_table_association = Table(
    'api_group_table_association',
    Base.metadata,
    Column('api_group_id', Integer, ForeignKey('api_groups.id', ondelete="CASCADE"), primary_key=True),
    Column('table_metadata_id', Integer, ForeignKey('table_metadata.id', ondelete="CASCADE"), primary_key=True)
)

class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role = Column(String(20), unique=True, nullable=False)
    description = Column(String(100), nullable=True)

    def __repr__(self):
        return f"{self.role}"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25), nullable=False)
    password = Column(String(256), nullable=True)
    verification_id = Column(String(70), unique=True)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True))
    last_login_ip = Column(String(16))
    avatar = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    street_address = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    user_role_id = Column(Integer, ForeignKey("user_roles.id", ondelete="CASCADE"), nullable=True)
    user_role = relationship("UserRole", backref="users")
    projects = relationship("Project", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String(50), nullable=False)
    project_scope = Column(String(50), nullable=False)
    starred = Column(String(50), nullable=False)
    in_progress = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_schema = Column(String(100), nullable=False)
    tables = relationship("TableMetadata", back_populates="project")
    api_groups = relationship("APIGroup", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.name} - {self.description}"

    def generate_schema_name(self):
        return f"project_{self.user_id}_{self.id}"


class APIGroup(Base):
    __tablename__ = "api_groups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    project = relationship("Project", back_populates="api_groups")
    tables = relationship("TableMetadata", secondary=api_group_table_association, back_populates="api_groups")
    apis = relationship("API", back_populates="api_group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"APIGroup(name={self.name}, description={self.description})"

class API(Base):
    __tablename__ = "apis"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    description = Column(Text, nullable=True)
    api_group_id = Column(Integer, ForeignKey("api_groups.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    api_group = relationship("APIGroup", back_populates="apis")
    enabled = Column(Boolean, default=True)

    def __repr__(self):
        return f"API(name={self.name}, endpoint={self.endpoint}, method={self.method}, description={self.description}, enabled={self.enabled})"



class TableMetadata(Base):
    __tablename__ = "table_metadata"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="tables")
    columns = relationship("ColumnMetadata", back_populates="table")
    api_groups = relationship("APIGroup", secondary=api_group_table_association, back_populates="tables")


class ColumnMetadata(Base):
    __tablename__ = "column_metadata"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    nullable = Column(Boolean, default=True)
    primary_key = Column(Boolean, default=False)
    unique = Column(Boolean, default=False)
    default = Column(Text, nullable=True)  # Using Text to store any default value as a string
    autoincrement = Column(Boolean, default=False)
    table_id = Column(Integer, ForeignKey("table_metadata.id"), nullable=False)
    table = relationship("TableMetadata", back_populates="columns")
    foreign_key = relationship("ForeignKeyMetadata", uselist=False, back_populates="column")


class ForeignKeyMetadata(Base):
    __tablename__ = "foreign_key_metadata"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    column_id = Column(Integer, ForeignKey("column_metadata.id"), nullable=False)
    referenced_table = Column(String, nullable=False)
    referenced_column = Column(String, nullable=False)
    column = relationship("ColumnMetadata", back_populates="foreign_key")

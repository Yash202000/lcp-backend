from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey,Integer
from sqlalchemy.orm import relationship
from database import Base

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

    def __repr__(self):
        return f"{self.name} - {self.description}"

    def generate_schema_name(self):
        return f"project_{self.user_id}_{self.id}"

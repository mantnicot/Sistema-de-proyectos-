from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="general")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class FormFieldModel(Base):
    __tablename__ = "form_fields"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    label = Column(String(255), nullable=False)
    field_type = Column(String(50), nullable=False)
    placeholder = Column(String(255), nullable=True)
    required = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    width = Column(Integer, default=100)
    height = Column(Integer, default=1)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    max_length = Column(Integer, nullable=True)
    list_options = Column(JSON, default=list)
    list_multiple = Column(Boolean, default=False)
    section = Column(String(100), default="general")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    data = Column(JSON, default=dict)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    user_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=settings.DEBUG,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    import app.infrastructure.persistence.work_models  # noqa: F401 — registra tablas work_*
    Base.metadata.create_all(bind=engine)
    _migrate_schema()


def _migrate_schema() -> None:
    """Agrega columnas nuevas en bases de datos existentes."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "form_fields" in tables:
        columns = {col["name"] for col in inspector.get_columns("form_fields")}
        with engine.begin() as conn:
            if "list_multiple" not in columns:
                conn.execute(text("ALTER TABLE form_fields ADD COLUMN list_multiple BOOLEAN DEFAULT FALSE"))
            conn.execute(
                text("UPDATE form_fields SET list_multiple = TRUE WHERE name = 'recursos' AND field_type = 'list'")
            )
            conn.execute(text("DELETE FROM form_fields WHERE name = 'Recursos'"))

    if "work_projects" not in tables:
        return

    project_columns = {col["name"] for col in inspector.get_columns("work_projects")}
    is_postgres = settings.DATABASE_URL.startswith("postgresql")

    with engine.begin() as conn:
        if "folder_id" not in project_columns and "folder" in project_columns:
            rows = conn.execute(text("SELECT DISTINCT folder FROM work_projects WHERE folder IS NOT NULL")).fetchall()
            for i, (folder_name,) in enumerate(rows):
                if not folder_name:
                    continue
                existing = conn.execute(
                    text("SELECT id FROM work_folders WHERE name = :name"),
                    {"name": folder_name},
                ).fetchone()
                if not existing:
                    conn.execute(
                        text("INSERT INTO work_folders (name, order_index) VALUES (:name, :idx)"),
                        {"name": folder_name, "idx": i},
                    )
            conn.execute(text("ALTER TABLE work_projects ADD COLUMN folder_id INTEGER"))
            conn.execute(
                text(
                    "UPDATE work_projects SET folder_id = "
                    "(SELECT id FROM work_folders WHERE work_folders.name = work_projects.folder) "
                    "WHERE folder IS NOT NULL"
                )
            )

        if "folder" in project_columns:
            if is_postgres:
                conn.execute(text("ALTER TABLE work_projects DROP COLUMN IF EXISTS folder"))
            else:
                conn.execute(text("ALTER TABLE work_projects DROP COLUMN folder"))

    _reset_work_projects_once(tables)


def _reset_work_projects_once(tables: list[str]) -> None:
    """Vacía proyectos en proceso una sola vez para empezar desde cero."""
    from sqlalchemy import text

    if "work_projects" not in tables:
        return

    migration_key = "work_data_reset_v2"

    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS app_migrations ("
                "key VARCHAR(100) PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )
        )
        applied = conn.execute(
            text("SELECT key FROM app_migrations WHERE key = :key"),
            {"key": migration_key},
        ).fetchone()
        if applied:
            return

        if "work_evidences" in tables:
            conn.execute(text("DELETE FROM work_evidences"))
        if "work_subfolders" in tables:
            conn.execute(text("DELETE FROM work_subfolders"))
        if "work_projects" in tables:
            conn.execute(text("DELETE FROM work_projects"))
        if "work_folders" in tables:
            conn.execute(text("DELETE FROM work_folders"))

        conn.execute(
            text("INSERT INTO app_migrations (key) VALUES (:key)"),
            {"key": migration_key},
        )

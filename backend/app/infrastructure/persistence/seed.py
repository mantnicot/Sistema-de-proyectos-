"""Datos iniciales del sistema OATI."""
import logging

from sqlalchemy.orm import Session

from app.domain.entities import FieldType, FormField, User, UserRole
from app.infrastructure.persistence.database import FormFieldModel, UserModel, init_db
from app.infrastructure.persistence.repositories import SQLFormFieldRepository, SQLUserRepository
from app.infrastructure.security.jwt_handler import hash_password

logger = logging.getLogger(__name__)

DEFAULT_FIELDS = [
    FormField(name="objeto", label="Objeto del proyecto", field_type=FieldType.TEXTAREA, required=True, order_index=0, height=3),
    FormField(name="alcance", label="Alcance", field_type=FieldType.TEXT, required=True, order_index=1),
    FormField(name="recursos", label="Recursos", field_type=FieldType.LIST, required=False, order_index=2,
              list_options=["Ingeniero sistemas", "Presupuesto", "Infraestructura", "Licencias"], list_multiple=True),
    FormField(name="estimacion_numero", label="Estimación - Números", field_type=FieldType.INTEGER, required=False, order_index=3, min_value=1),
    FormField(name="estimacion_medida", label="Estimación - Medida", field_type=FieldType.LIST, required=False, order_index=4, list_options=["Días", "Semanas", "Meses"]),
    FormField(name="justificacion", label="Justificación (Necesidad)", field_type=FieldType.TEXT, required=True, order_index=5),
    FormField(name="impacto", label="Impacto", field_type=FieldType.TEXT, required=False, order_index=6, width=50),
    FormField(name="alineacion", label="Alineación", field_type=FieldType.TEXT, required=False, order_index=7, width=50),
    FormField(name="descripcion", label="Descripción", field_type=FieldType.TEXTAREA, required=False, order_index=8, height=4),
]

DEFAULT_USERS = [
    ("admin", "admin@udistrital.edu.co", "admin123", UserRole.ADMIN),
    ("general", "general@udistrital.edu.co", "general123", UserRole.GENERAL),
]


def seed_database(db: Session) -> None:
    user_repo = SQLUserRepository(db)
    field_repo = SQLFormFieldRepository(db)

    for username, email, password, role in DEFAULT_USERS:
        if not user_repo.get_by_username(username):
            user_repo.create(User(username=username, email=email, role=role), hash_password(password))
            logger.info("Usuario creado: %s (%s)", username, role.value)

    if not field_repo.list_all():
        for field in DEFAULT_FIELDS:
            field_repo.create(field)
        logger.info("Campos de formulario por defecto creados")


def run_seed() -> None:
    init_db()
    from app.infrastructure.persistence.database import SessionLocal

    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

import json
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities import AuditLog, FormField, Project, User, UserRole
from app.domain.repositories import AuditRepository, FormFieldRepository, ProjectRepository, UserRepository
from app.infrastructure.persistence.database import AuditLogModel, FormFieldModel, ProjectModel, UserModel


def _user_to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        username=model.username,
        email=model.email,
        role=UserRole(model.role),
        is_active=model.is_active,
        created_at=model.created_at,
    )


def _field_to_entity(model: FormFieldModel) -> FormField:
    return FormField(
        id=model.id,
        name=model.name,
        label=model.label,
        field_type=model.field_type,
        placeholder=model.placeholder,
        required=model.required,
        order_index=model.order_index,
        width=model.width,
        height=model.height,
        min_value=model.min_value,
        max_value=model.max_value,
        max_length=model.max_length,
        list_options=model.list_options or [],
        list_multiple=bool(model.list_multiple),
        section=model.section,
    )


def _project_to_entity(model: ProjectModel) -> Project:
    return Project(
        id=model.id,
        name=model.name,
        description=model.description,
        data=model.data or {},
        created_at=model.created_at,
        updated_at=model.updated_at,
        created_by=model.created_by,
    )


class SQLUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.username == username).first()
        return _user_to_entity(model) if model else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return _user_to_entity(model) if model else None

    def create(self, user: User, password_hash: str) -> User:
        model = UserModel(
            username=user.username,
            email=user.email,
            password_hash=password_hash,
            role=user.role.value,
            is_active=user.is_active,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _user_to_entity(model)


class SQLFormFieldRepository(FormFieldRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[FormField]:
        models = self.db.query(FormFieldModel).order_by(FormFieldModel.order_index).all()
        return [_field_to_entity(m) for m in models]

    def get_by_id(self, field_id: int) -> Optional[FormField]:
        model = self.db.query(FormFieldModel).filter(FormFieldModel.id == field_id).first()
        return _field_to_entity(model) if model else None

    def create(self, field: FormField) -> FormField:
        model = FormFieldModel(
            name=field.name,
            label=field.label,
            field_type=field.field_type.value if hasattr(field.field_type, "value") else field.field_type,
            placeholder=field.placeholder,
            required=field.required,
            order_index=field.order_index,
            width=field.width,
            height=field.height,
            min_value=field.min_value,
            max_value=field.max_value,
            max_length=field.max_length,
            list_options=field.list_options,
            list_multiple=field.list_multiple,
            section=field.section,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _field_to_entity(model)

    def update(self, field: FormField) -> FormField:
        model = self.db.query(FormFieldModel).filter(FormFieldModel.id == field.id).first()
        if not model:
            raise ValueError("Campo no encontrado")
        model.name = field.name
        model.label = field.label
        model.field_type = field.field_type.value if hasattr(field.field_type, "value") else field.field_type
        model.placeholder = field.placeholder
        model.required = field.required
        model.order_index = field.order_index
        model.width = field.width
        model.height = field.height
        model.min_value = field.min_value
        model.max_value = field.max_value
        model.max_length = field.max_length
        model.list_options = field.list_options
        model.list_multiple = field.list_multiple
        model.section = field.section
        self.db.commit()
        self.db.refresh(model)
        return _field_to_entity(model)

    def delete(self, field_id: int) -> bool:
        model = self.db.query(FormFieldModel).filter(FormFieldModel.id == field_id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True

    def reorder(self, field_ids: list[int]) -> list[FormField]:
        for idx, fid in enumerate(field_ids):
            model = self.db.query(FormFieldModel).filter(FormFieldModel.id == fid).first()
            if model:
                model.order_index = idx
        self.db.commit()
        return self.list_all()


class SQLProjectRepository(ProjectRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_all(
        self, search: Optional[str] = None, sort_by: str = "name", sort_dir: str = "asc"
    ) -> list[Project]:
        query = self.db.query(ProjectModel)
        if search:
            term = f"%{search.lower()}%"
            query = query.filter(
                (ProjectModel.name.ilike(term)) | (ProjectModel.description.ilike(term))
            )
        sort_col = getattr(ProjectModel, sort_by, ProjectModel.name)
        query = query.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
        return [_project_to_entity(m) for m in query.all()]

    def get_by_id(self, project_id: int) -> Optional[Project]:
        model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        return _project_to_entity(model) if model else None

    def create(self, project: Project) -> Project:
        model = ProjectModel(
            name=project.name,
            description=project.description,
            data=project.data,
            created_by=project.created_by,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _project_to_entity(model)

    def update(self, project: Project) -> Project:
        model = self.db.query(ProjectModel).filter(ProjectModel.id == project.id).first()
        if not model:
            raise ValueError("Proyecto no encontrado")
        model.name = project.name
        model.description = project.description
        model.data = project.data
        self.db.commit()
        self.db.refresh(model)
        return _project_to_entity(model)

    def delete(self, project_id: int) -> bool:
        model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True


class SQLAuditRepository(AuditRepository):
    def __init__(self, db: Session):
        self.db = db

    def log(self, entry: AuditLog) -> AuditLog:
        model = AuditLogModel(
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            action=entry.action,
            user_id=entry.user_id,
            details=entry.details,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return AuditLog(
            id=model.id,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            action=model.action,
            user_id=model.user_id,
            details=model.details,
            created_at=model.created_at,
        )

    def list_recent(self, limit: int = 100) -> list[AuditLog]:
        models = self.db.query(AuditLogModel).order_by(AuditLogModel.created_at.desc()).limit(limit).all()
        return [
            AuditLog(
                id=m.id,
                entity_type=m.entity_type,
                entity_id=m.entity_id,
                action=m.action,
                user_id=m.user_id,
                details=m.details,
                created_at=m.created_at,
            )
            for m in models
        ]

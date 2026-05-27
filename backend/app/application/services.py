import json
import logging
from typing import Any, Optional

from app.domain.entities import AuditLog, FieldType, FormField, Project, UserRole
from app.domain.repositories import AuditRepository, FormFieldRepository, ProjectRepository
from app.infrastructure.export.document_exporter import DocumentExporter

logger = logging.getLogger(__name__)


class FormFieldService:
    def __init__(self, repo: FormFieldRepository, audit: AuditRepository):
        self.repo = repo
        self.audit = audit

    def list_fields(self) -> list[FormField]:
        return self.repo.list_all()

    def get_field(self, field_id: int) -> Optional[FormField]:
        return self.repo.get_by_id(field_id)

    def create_field(self, field: FormField, user_id: Optional[int] = None) -> FormField:
        created = self.repo.create(field)
        self.audit.log(
            AuditLog(entity_type="form_field", entity_id=created.id or 0, action="create", user_id=user_id)
        )
        return created

    def update_field(self, field: FormField, user_id: Optional[int] = None) -> FormField:
        updated = self.repo.update(field)
        self.audit.log(
            AuditLog(entity_type="form_field", entity_id=updated.id or 0, action="update", user_id=user_id)
        )
        return updated

    def delete_field(self, field_id: int, user_id: Optional[int] = None) -> bool:
        ok = self.repo.delete(field_id)
        if ok:
            self.audit.log(AuditLog(entity_type="form_field", entity_id=field_id, action="delete", user_id=user_id))
        return ok

    def duplicate_field(self, field_id: int, user_id: Optional[int] = None) -> Optional[FormField]:
        original = self.repo.get_by_id(field_id)
        if not original:
            return None
        copy = FormField(
            name=f"{original.name}_copia",
            label=f"{original.label} (copia)",
            field_type=original.field_type,
            placeholder=original.placeholder,
            required=original.required,
            order_index=original.order_index + 1,
            width=original.width,
            height=original.height,
            min_value=original.min_value,
            max_value=original.max_value,
            max_length=original.max_length,
            list_options=list(original.list_options),
            list_multiple=original.list_multiple,
            section=original.section,
        )
        return self.create_field(copy, user_id)

    def reorder(self, field_ids: list[int], user_id: Optional[int] = None) -> list[FormField]:
        result = self.repo.reorder(field_ids)
        self.audit.log(
            AuditLog(
                entity_type="form_field",
                entity_id=0,
                action="reorder",
                user_id=user_id,
                details=json.dumps(field_ids),
            )
        )
        return result


class ProjectService:
    def __init__(
        self,
        repo: ProjectRepository,
        field_repo: FormFieldRepository,
        audit: AuditRepository,
        exporter: DocumentExporter,
    ):
        self.repo = repo
        self.field_repo = field_repo
        self.audit = audit
        self.exporter = exporter

    def list_projects(
        self, search: Optional[str] = None, sort_by: str = "name", sort_dir: str = "asc"
    ) -> list[Project]:
        return self.repo.list_all(search=search, sort_by=sort_by, sort_dir=sort_dir)

    def get_project(self, project_id: int) -> Optional[Project]:
        return self.repo.get_by_id(project_id)

    def validate_project_data(self, data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        fields = self.field_repo.list_all()
        for field in fields:
            key = field.name
            value = data.get(key)
            ft = field.field_type.value if hasattr(field.field_type, "value") else field.field_type

            if field.required and (value is None or value == "" or value == []):
                errors.append(f"El campo '{field.label}' es obligatorio.")
                continue

            if value is None or value == "":
                continue

            if ft in ("integer", "decimal", "percentage", "time"):
                try:
                    num = float(value) if ft != "integer" else int(value)
                    if field.min_value is not None and num < field.min_value:
                        errors.append(f"'{field.label}' debe ser mayor o igual a {field.min_value}.")
                    if field.max_value is not None and num > field.max_value:
                        errors.append(f"'{field.label}' debe ser menor o igual a {field.max_value}.")
                except (TypeError, ValueError):
                    errors.append(f"'{field.label}' debe ser un valor numérico válido.")

            if field.max_length and isinstance(value, str) and len(value) > field.max_length:
                errors.append(f"'{field.label}' excede el máximo de {field.max_length} caracteres.")

        return errors

    def create_project(self, project: Project, user_id: Optional[int] = None) -> tuple[Optional[Project], list[str]]:
        errors = self.validate_project_data(project.data)
        if errors:
            return None, errors
        project.created_by = user_id
        created = self.repo.create(project)
        self.audit.log(
            AuditLog(entity_type="project", entity_id=created.id or 0, action="create", user_id=user_id)
        )
        return created, []

    def update_project(self, project: Project, user_id: Optional[int] = None) -> tuple[Optional[Project], list[str]]:
        errors = self.validate_project_data(project.data)
        if errors:
            return None, errors
        updated = self.repo.update(project)
        self.audit.log(
            AuditLog(entity_type="project", entity_id=updated.id or 0, action="update", user_id=user_id)
        )
        return updated, []

    def delete_project(self, project_id: int, user_id: Optional[int] = None) -> bool:
        ok = self.repo.delete(project_id)
        if ok:
            self.audit.log(AuditLog(entity_type="project", entity_id=project_id, action="delete", user_id=user_id))
        return ok

    def duplicate_project(self, project_id: int, user_id: Optional[int] = None) -> Optional[Project]:
        original = self.repo.get_by_id(project_id)
        if not original:
            return None
        copy = Project(
            name=f"{original.name} copia",
            description=original.description,
            data=dict(original.data),
            created_by=user_id,
        )
        created, _ = self.create_project(copy, user_id)
        return created

    def export_pdf(self, project_id: int) -> Optional[bytes]:
        project = self.repo.get_by_id(project_id)
        if not project:
            return None
        fields = [f.model_dump() for f in self.field_repo.list_all()]
        return self.exporter.export_pdf(project.model_dump(), fields)

    def export_word(self, project_id: int) -> Optional[bytes]:
        project = self.repo.get_by_id(project_id)
        if not project:
            return None
        fields = [f.model_dump() for f in self.field_repo.list_all()]
        return self.exporter.export_word(project.model_dump(), fields)

    def export_excel_all(self) -> bytes:
        projects = [p.model_dump() for p in self.repo.list_all()]
        fields = [f.model_dump() for f in self.field_repo.list_all()]
        return self.exporter.export_excel_all(projects, fields)

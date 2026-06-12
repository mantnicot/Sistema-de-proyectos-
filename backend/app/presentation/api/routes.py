import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.application.schemas import (
    FormFieldCreate,
    FormFieldResponse,
    FormFieldUpdate,
    LoginRequest,
    MessageResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ReorderFieldsRequest,
    TokenResponse,
    UserResponse,
)
from app.application.services import FormFieldService, ProjectService
from app.domain.entities import FormField, Project, User
from app.infrastructure.export.document_exporter import DocumentExporter
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories import (
    SQLAuditRepository,
    SQLFormFieldRepository,
    SQLProjectRepository,
    SQLUserRepository,
)
from app.infrastructure.security.jwt_handler import create_access_token, user_to_token_payload, verify_password
from app.presentation.dependencies import get_current_user, require_admin
from app.presentation.api.work_routes import router as work_router

logger = logging.getLogger(__name__)

router = APIRouter()
router.include_router(work_router)


def _field_service(db: Session) -> FormFieldService:
    return FormFieldService(SQLFormFieldRepository(db), SQLAuditRepository(db))


def _project_service(db: Session) -> ProjectService:
    return ProjectService(
        SQLProjectRepository(db),
        SQLFormFieldRepository(db),
        SQLAuditRepository(db),
        DocumentExporter(),
    )


@router.post("/auth/login", response_model=TokenResponse, tags=["Autenticación"])
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user_repo = SQLUserRepository(db)
    user = user_repo.get_by_username(body.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    from app.infrastructure.persistence.database import UserModel

    model = db.query(UserModel).filter(UserModel.username == body.username).first()
    if not model or not verify_password(body.password, model.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token(user_to_token_payload(user))
    return TokenResponse(access_token=token, role=user.role, username=user.username)


@router.get("/auth/me", response_model=UserResponse, tags=["Autenticación"])
def me(user: User = Depends(get_current_user)):
    return UserResponse(id=user.id or 0, username=user.username, email=user.email, role=user.role)


def _to_field_response(field: FormField) -> FormFieldResponse:
    ft = field.field_type.value if hasattr(field.field_type, "value") else field.field_type
    return FormFieldResponse(
        id=field.id or 0,
        name=field.name,
        label=field.label,
        field_type=ft,
        placeholder=field.placeholder,
        required=bool(field.required),
        order_index=field.order_index,
        width=field.width,
        height=field.height,
        min_value=field.min_value,
        max_value=field.max_value,
        max_length=field.max_length,
        list_options=field.list_options or [],
        list_multiple=bool(field.list_multiple),
        section=field.section,
    )


@router.get("/form-fields", response_model=list[FormFieldResponse], tags=["Formulario"])
def list_form_fields(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    fields = _field_service(db).list_fields()
    return [_to_field_response(f) for f in fields]


@router.post("/form-fields", response_model=FormFieldResponse, tags=["Formulario"])
def create_form_field(
    body: FormFieldCreate, db: Session = Depends(get_db), user: User = Depends(require_admin)
):
    field = FormField(**body.model_dump())
    created = _field_service(db).create_field(field, user.id)
    return _to_field_response(created)


@router.put("/form-fields/{field_id}", response_model=FormFieldResponse, tags=["Formulario"])
def update_form_field(
    field_id: int, body: FormFieldCreate, db: Session = Depends(get_db), user: User = Depends(require_admin)
):
    svc = _field_service(db)
    existing = svc.get_field(field_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    field = FormField(id=field_id, **body.model_dump())
    updated = svc.update_field(field, user.id)
    return _to_field_response(updated)


@router.delete("/form-fields/{field_id}", response_model=MessageResponse, tags=["Formulario"])
def delete_form_field(field_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    ok = _field_service(db).delete_field(field_id, user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    return MessageResponse(message="Campo eliminado correctamente")


@router.post("/form-fields/{field_id}/duplicate", response_model=FormFieldResponse, tags=["Formulario"])
def duplicate_form_field(field_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    dup = _field_service(db).duplicate_field(field_id, user.id)
    if not dup:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    return _to_field_response(dup)


@router.put("/form-fields/reorder", response_model=list[FormFieldResponse], tags=["Formulario"])
def reorder_form_fields(
    body: ReorderFieldsRequest, db: Session = Depends(get_db), user: User = Depends(require_admin)
):
    fields = _field_service(db).reorder(body.field_ids, user.id)
    return [_to_field_response(f) for f in fields]


@router.get("/projects", response_model=list[ProjectResponse], tags=["Proyectos"])
def list_projects(
    search: Optional[str] = Query(None),
    sort_by: str = Query("name"),
    sort_dir: str = Query("asc"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    projects = _project_service(db).list_projects(search=search, sort_by=sort_by, sort_dir=sort_dir)
    return [
        ProjectResponse(
            id=p.id or 0,
            name=p.name,
            description=p.description,
            data=p.data,
            created_at=p.created_at.isoformat() if p.created_at else None,
            updated_at=p.updated_at.isoformat() if p.updated_at else None,
        )
        for p in projects
    ]


@router.get("/projects/{project_id}", response_model=ProjectResponse, tags=["Proyectos"])
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = _project_service(db).get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return ProjectResponse(
        id=project.id or 0,
        name=project.name,
        description=project.description,
        data=project.data,
        created_at=project.created_at.isoformat() if project.created_at else None,
        updated_at=project.updated_at.isoformat() if project.updated_at else None,
    )


@router.post("/projects", response_model=ProjectResponse, tags=["Proyectos"])
def create_project(body: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    project, errors = _project_service(db).create_project(Project(**body.model_dump()), user.id)
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    assert project
    return ProjectResponse(
        id=project.id or 0,
        name=project.name,
        description=project.description,
        data=project.data,
        created_at=project.created_at.isoformat() if project.created_at else None,
        updated_at=project.updated_at.isoformat() if project.updated_at else None,
    )


@router.put("/projects/{project_id}", response_model=ProjectResponse, tags=["Proyectos"])
def update_project(
    project_id: int, body: ProjectUpdate, db: Session = Depends(get_db), user: User = Depends(require_admin)
):
    project, errors = _project_service(db).update_project(
        Project(id=project_id, **body.model_dump()), user.id
    )
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    assert project
    return ProjectResponse(
        id=project.id or 0,
        name=project.name,
        description=project.description,
        data=project.data,
        created_at=project.created_at.isoformat() if project.created_at else None,
        updated_at=project.updated_at.isoformat() if project.updated_at else None,
    )


@router.delete("/projects/{project_id}", response_model=MessageResponse, tags=["Proyectos"])
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    ok = _project_service(db).delete_project(project_id, user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return MessageResponse(message="Proyecto eliminado correctamente")


@router.post("/projects/{project_id}/duplicate", response_model=ProjectResponse, tags=["Proyectos"])
def duplicate_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    dup = _project_service(db).duplicate_project(project_id, user.id)
    if not dup:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return ProjectResponse(
        id=dup.id or 0,
        name=dup.name,
        description=dup.description,
        data=dup.data,
        created_at=dup.created_at.isoformat() if dup.created_at else None,
        updated_at=dup.updated_at.isoformat() if dup.updated_at else None,
    )


@router.get("/projects/{project_id}/export/pdf", tags=["Exportación"])
def export_project_pdf(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    content = _project_service(db).export_pdf(project_id)
    if not content:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="proyecto_{project_id}.pdf"'},
    )


@router.get("/projects/{project_id}/export/word", tags=["Exportación"])
def export_project_word(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    content = _project_service(db).export_word(project_id)
    if not content:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="proyecto_{project_id}.docx"'},
    )


@router.get("/projects/export/excel", tags=["Exportación"])
def export_all_excel(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    content = _project_service(db).export_excel_all()
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="proyectos_oati.xlsx"'},
    )

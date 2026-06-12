from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.application.work_schemas import (
    ReorderRequest,
    WorkEvidenceCreateJson,
    WorkEvidenceResponse,
    WorkEvidenceUpdate,
    WorkProjectCreate,
    WorkProjectResponse,
    WorkProjectUpdate,
    WorkSubfolderCreate,
    WorkSubfolderUpdate,
)
from app.application.work_service import (
    WorkProjectService,
    build_project_response,
    build_evidence_response,
    build_subfolder_response,
)
from app.domain.entities import User
from app.infrastructure.persistence.database import get_db
from app.presentation.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/work-projects", tags=["Proyectos en proceso"])


def _svc(db: Session) -> WorkProjectService:
    return WorkProjectService(db)


def _api_base() -> str:
    return "/api/v1"


@router.get("", response_model=list[WorkProjectResponse])
def list_work_projects(
    folder: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = _svc(db)
    projects = svc.list_by_folder(folder.upper())
    base = _api_base()
    return [build_project_response(p, base) for p in projects]


@router.get("/{project_id}", response_model=WorkProjectResponse)
def get_work_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = _svc(db)
    project = svc.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return build_project_response(project, _api_base())


@router.post("", response_model=WorkProjectResponse, status_code=201)
def create_work_project(
    body: WorkProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    svc = _svc(db)
    try:
        project = svc.create(body.name, body.folder.upper())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    project = svc.get(project.id)
    return build_project_response(project, _api_base())


@router.put("/{project_id}", response_model=WorkProjectResponse)
def update_work_project(
    project_id: int,
    body: WorkProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    svc = _svc(db)
    try:
        project = svc.update(project_id, body.name, body.folder.upper() if body.folder else None)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return build_project_response(project, _api_base())


@router.delete("/{project_id}")
def delete_work_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    if not _svc(db).delete(project_id):
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"message": "Proyecto eliminado"}


@router.post("/{project_id}/logo")
def upload_logo(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    content = file.file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="El logo no puede superar 5 MB")
    try:
        path = _svc(db).save_logo(project_id, file.filename or "logo.png", content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not path:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"message": "Logo actualizado", "logo_url": f"{_api_base()}/work-projects/{project_id}/logo"}


@router.get("/{project_id}/logo")
def get_logo(project_id: int, db: Session = Depends(get_db)):
    path = _svc(db).get_logo_path(project_id)
    if not path:
        raise HTTPException(status_code=404, detail="Logo no encontrado")
    return FileResponse(path)


@router.post("/{project_id}/subfolders", status_code=201)
def create_subfolder(
    project_id: int,
    body: WorkSubfolderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    sf = _svc(db).create_subfolder(project_id, body.name)
    if not sf:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return build_subfolder_response(sf, _api_base())


@router.put("/subfolders/{subfolder_id}")
def update_subfolder(
    subfolder_id: int,
    body: WorkSubfolderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    sf = _svc(db).update_subfolder(subfolder_id, body.name)
    if not sf:
        raise HTTPException(status_code=404, detail="Subcarpeta no encontrada")
    return build_subfolder_response(sf, _api_base())


@router.delete("/subfolders/{subfolder_id}")
def delete_subfolder(
    subfolder_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    if not _svc(db).delete_subfolder(subfolder_id):
        raise HTTPException(status_code=404, detail="Subcarpeta no encontrada")
    return {"message": "Subcarpeta eliminada"}


@router.post("/subfolders/{subfolder_id}/evidences", status_code=201)
async def create_evidence(
    subfolder_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
    evidence_type: str = Form(...),
    name: str = Form(...),
    progress_percent: float = Form(0),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    svc = _svc(db)
    if evidence_type == "url":
        if not url:
            raise HTTPException(status_code=400, detail="URL requerida")
        ev = svc.create_evidence_url(subfolder_id, name, url, progress_percent)
    elif evidence_type == "document":
        if not file:
            raise HTTPException(status_code=400, detail="Archivo requerido")
        content = await file.read()
        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Archivo no puede superar 20 MB")
        ev = svc.create_evidence_document(subfolder_id, name, progress_percent, file.filename or "doc", content)
    else:
        raise HTTPException(status_code=400, detail="Tipo inválido: document o url")
    if not ev:
        raise HTTPException(status_code=404, detail="Subcarpeta no encontrada")
    return build_evidence_response(ev, _api_base())


@router.post("/subfolders/{subfolder_id}/evidences/json", status_code=201)
def create_evidence_json(
    subfolder_id: int,
    body: WorkEvidenceCreateJson,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    if body.evidence_type != "url":
        raise HTTPException(status_code=400, detail="Solo URL por JSON; use multipart para documentos")
    ev = _svc(db).create_evidence_url(subfolder_id, body.name, body.url or "", body.progress_percent)
    if not ev:
        raise HTTPException(status_code=404, detail="Subcarpeta no encontrada")
    return build_evidence_response(ev, _api_base())


@router.put("/evidences/{evidence_id}")
def update_evidence(
    evidence_id: int,
    body: WorkEvidenceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    ev = _svc(db).update_evidence(evidence_id, body.name, body.progress_percent, body.url, body.group_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")
    return build_evidence_response(ev, _api_base())


@router.delete("/evidences/{evidence_id}")
def delete_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    if not _svc(db).delete_evidence(evidence_id):
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")
    return {"message": "Evidencia eliminada"}


@router.put("/evidences/reorder")
def reorder_evidences(
    body: ReorderRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    items = [{"id": i.id, "order_index": i.order_index, "group_id": i.group_id} for i in body.items]
    _svc(db).reorder_evidences(items)
    return {"message": "Orden actualizado"}


@router.get("/evidences/{evidence_id}/file")
def download_evidence_file(
    evidence_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = _svc(db).get_file_path(evidence_id)
    if not result:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    path, filename = result
    return FileResponse(path, filename=filename)

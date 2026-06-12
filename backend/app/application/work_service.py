import os
import shutil
import uuid
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.domain.work_entities import EvidenceType
from app.infrastructure.persistence.work_models import (
    WorkEvidenceModel,
    WorkFolderModel,
    WorkProjectModel,
    WorkSubfolderModel,
)

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "work_projects"


def _ensure_upload_dir(project_id: int) -> Path:
    path = UPLOAD_ROOT / str(project_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _avg_progress(evidences: list[WorkEvidenceModel]) -> float:
    if not evidences:
        return 0.0
    return round(sum(e.progress_percent or 0 for e in evidences) / len(evidences), 1)


def _project_progress(subfolders: list[WorkSubfolderModel]) -> float:
    all_evidences = [e for sf in subfolders for e in sf.evidences]
    return _avg_progress(all_evidences)


class WorkProjectService:
    def __init__(self, db: Session):
        self.db = db

    def list_folders(self) -> list[WorkFolderModel]:
        return self.db.query(WorkFolderModel).order_by(WorkFolderModel.order_index, WorkFolderModel.id).all()

    def get_folder(self, folder_id: int) -> Optional[WorkFolderModel]:
        return self.db.query(WorkFolderModel).filter(WorkFolderModel.id == folder_id).first()

    def create_folder(self, name: str) -> WorkFolderModel:
        name = name.strip()
        if not name:
            raise ValueError("El nombre de la carpeta es obligatorio.")
        if self.db.query(WorkFolderModel).filter(WorkFolderModel.name == name).first():
            raise ValueError("Ya existe una carpeta con ese nombre.")
        count = self.db.query(WorkFolderModel).count()
        folder = WorkFolderModel(name=name, order_index=count)
        self.db.add(folder)
        self.db.commit()
        self.db.refresh(folder)
        return folder

    def update_folder(self, folder_id: int, name: Optional[str]) -> Optional[WorkFolderModel]:
        folder = self.get_folder(folder_id)
        if not folder:
            return None
        if name is not None:
            name = name.strip()
            if not name:
                raise ValueError("El nombre de la carpeta es obligatorio.")
            existing = self.db.query(WorkFolderModel).filter(WorkFolderModel.name == name, WorkFolderModel.id != folder_id).first()
            if existing:
                raise ValueError("Ya existe una carpeta con ese nombre.")
            folder.name = name
        self.db.commit()
        self.db.refresh(folder)
        return folder

    def delete_folder(self, folder_id: int) -> bool:
        folder = self.get_folder(folder_id)
        if not folder:
            return False
        count = self.db.query(WorkProjectModel).filter(WorkProjectModel.folder_id == folder_id).count()
        if count > 0:
            raise ValueError("No se puede eliminar una carpeta que contiene proyectos.")
        self.db.delete(folder)
        self.db.commit()
        return True

    def list_by_folder_id(self, folder_id: int) -> list[WorkProjectModel]:
        return (
            self.db.query(WorkProjectModel)
            .options(
                joinedload(WorkProjectModel.folder),
                joinedload(WorkProjectModel.subfolders).joinedload(WorkSubfolderModel.evidences),
            )
            .filter(WorkProjectModel.folder_id == folder_id)
            .order_by(WorkProjectModel.order_index, WorkProjectModel.id)
            .all()
        )

    def get(self, project_id: int) -> Optional[WorkProjectModel]:
        return (
            self.db.query(WorkProjectModel)
            .options(
                joinedload(WorkProjectModel.folder),
                joinedload(WorkProjectModel.subfolders).joinedload(WorkSubfolderModel.evidences),
            )
            .filter(WorkProjectModel.id == project_id)
            .first()
        )

    def create(self, name: str, folder_id: int) -> WorkProjectModel:
        if not self.get_folder(folder_id):
            raise ValueError("Carpeta no encontrada.")
        max_order = (
            self.db.query(WorkProjectModel)
            .filter(WorkProjectModel.folder_id == folder_id)
            .count()
        )
        project = WorkProjectModel(name=name.strip(), folder_id=folder_id, order_index=max_order)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project_id: int, name: Optional[str], folder_id: Optional[int]) -> Optional[WorkProjectModel]:
        project = self.db.query(WorkProjectModel).filter(WorkProjectModel.id == project_id).first()
        if not project:
            return None
        if name is not None:
            project.name = name.strip()
        if folder_id is not None:
            if not self.get_folder(folder_id):
                raise ValueError("Carpeta no encontrada.")
            project.folder_id = folder_id
        self.db.commit()
        self.db.refresh(project)
        return self.get(project_id)

    def delete(self, project_id: int) -> bool:
        project = self.db.query(WorkProjectModel).filter(WorkProjectModel.id == project_id).first()
        if not project:
            return False
        upload_dir = UPLOAD_ROOT / str(project_id)
        self.db.delete(project)
        self.db.commit()
        if upload_dir.exists():
            shutil.rmtree(upload_dir, ignore_errors=True)
        return True

    def save_logo(self, project_id: int, filename: str, content: bytes) -> Optional[str]:
        project = self.db.query(WorkProjectModel).filter(WorkProjectModel.id == project_id).first()
        if not project:
            return None
        ext = Path(filename).suffix.lower() or ".png"
        if ext not in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
            raise ValueError("Formato de imagen no permitido.")
        dest_dir = _ensure_upload_dir(project_id)
        if project.logo_path:
            old = UPLOAD_ROOT.parent / project.logo_path if not Path(project.logo_path).is_absolute() else Path(project.logo_path)
            if old.exists():
                old.unlink(missing_ok=True)
        logo_name = f"logo_{uuid.uuid4().hex[:8]}{ext}"
        dest = dest_dir / logo_name
        dest.write_bytes(content)
        rel = f"work_projects/{project_id}/{logo_name}"
        project.logo_path = rel
        self.db.commit()
        return rel

    def create_subfolder(self, project_id: int, name: str) -> Optional[WorkSubfolderModel]:
        project = self.db.query(WorkProjectModel).filter(WorkProjectModel.id == project_id).first()
        if not project:
            return None
        count = self.db.query(WorkSubfolderModel).filter(WorkSubfolderModel.project_id == project_id).count()
        sf = WorkSubfolderModel(project_id=project_id, name=name.strip(), order_index=count)
        self.db.add(sf)
        self.db.commit()
        self.db.refresh(sf)
        return sf

    def update_subfolder(self, subfolder_id: int, name: Optional[str]) -> Optional[WorkSubfolderModel]:
        sf = self.db.query(WorkSubfolderModel).filter(WorkSubfolderModel.id == subfolder_id).first()
        if not sf:
            return None
        if name is not None:
            sf.name = name.strip()
        self.db.commit()
        self.db.refresh(sf)
        return sf

    def delete_subfolder(self, subfolder_id: int) -> bool:
        sf = self.db.query(WorkSubfolderModel).filter(WorkSubfolderModel.id == subfolder_id).first()
        if not sf:
            return False
        self.db.delete(sf)
        self.db.commit()
        return True

    def create_evidence_url(
        self, subfolder_id: int, name: str, url: str, progress_percent: float
    ) -> Optional[WorkEvidenceModel]:
        sf = self.db.query(WorkSubfolderModel).filter(WorkSubfolderModel.id == subfolder_id).first()
        if not sf:
            return None
        count = self.db.query(WorkEvidenceModel).filter(WorkEvidenceModel.subfolder_id == subfolder_id).count()
        ev = WorkEvidenceModel(
            subfolder_id=subfolder_id,
            evidence_type=EvidenceType.URL.value,
            name=name.strip(),
            url=url.strip(),
            progress_percent=min(100, max(0, progress_percent)),
            order_index=count,
        )
        self.db.add(ev)
        self.db.commit()
        self.db.refresh(ev)
        return ev

    def create_evidence_document(
        self, subfolder_id: int, name: str, progress_percent: float, filename: str, content: bytes
    ) -> Optional[WorkEvidenceModel]:
        sf = self.db.query(WorkSubfolderModel).filter(WorkSubfolderModel.id == subfolder_id).first()
        if not sf:
            return None
        dest_dir = _ensure_upload_dir(sf.project_id)
        safe_name = f"doc_{uuid.uuid4().hex[:8]}_{Path(filename).name}"
        dest = dest_dir / safe_name
        dest.write_bytes(content)
        count = self.db.query(WorkEvidenceModel).filter(WorkEvidenceModel.subfolder_id == subfolder_id).count()
        rel = f"work_projects/{sf.project_id}/{safe_name}"
        ev = WorkEvidenceModel(
            subfolder_id=subfolder_id,
            evidence_type=EvidenceType.DOCUMENT.value,
            name=name.strip(),
            file_path=rel,
            file_name=Path(filename).name,
            progress_percent=min(100, max(0, progress_percent)),
            order_index=count,
        )
        self.db.add(ev)
        self.db.commit()
        self.db.refresh(ev)
        return ev

    def update_evidence(
        self,
        evidence_id: int,
        name: Optional[str],
        progress_percent: Optional[float],
        url: Optional[str],
        group_id: Optional[int],
    ) -> Optional[WorkEvidenceModel]:
        ev = self.db.query(WorkEvidenceModel).filter(WorkEvidenceModel.id == evidence_id).first()
        if not ev:
            return None
        if name is not None:
            ev.name = name.strip()
        if progress_percent is not None:
            ev.progress_percent = min(100, max(0, progress_percent))
        if url is not None and ev.evidence_type == EvidenceType.URL.value:
            ev.url = url.strip()
        if group_id is not None:
            ev.group_id = group_id if group_id > 0 else None
        self.db.commit()
        self.db.refresh(ev)
        return ev

    def delete_evidence(self, evidence_id: int) -> bool:
        ev = self.db.query(WorkEvidenceModel).filter(WorkEvidenceModel.id == evidence_id).first()
        if not ev:
            return False
        if ev.file_path:
            full = UPLOAD_ROOT.parent / ev.file_path
            if full.exists():
                full.unlink(missing_ok=True)
        self.db.delete(ev)
        self.db.commit()
        return True

    def reorder_evidences(self, items: list[dict]) -> None:
        for item in items:
            ev = self.db.query(WorkEvidenceModel).filter(WorkEvidenceModel.id == item["id"]).first()
            if ev:
                ev.order_index = item["order_index"]
                if "group_id" in item:
                    gid = item["group_id"]
                    ev.group_id = gid if gid and gid > 0 else None
        self.db.commit()

    def get_file_path(self, evidence_id: int) -> Optional[tuple[Path, str]]:
        ev = self.db.query(WorkEvidenceModel).filter(WorkEvidenceModel.id == evidence_id).first()
        if not ev or not ev.file_path or ev.evidence_type != EvidenceType.DOCUMENT.value:
            return None
        full = UPLOAD_ROOT.parent / ev.file_path
        if not full.exists():
            return None
        return full, ev.file_name or full.name

    def get_logo_path(self, project_id: int) -> Optional[Path]:
        project = self.db.query(WorkProjectModel).filter(WorkProjectModel.id == project_id).first()
        if not project or not project.logo_path:
            return None
        full = UPLOAD_ROOT.parent / project.logo_path
        return full if full.exists() else None


def build_evidence_response(ev: WorkEvidenceModel, _base_api: str = "") -> dict:
    file_url = None
    if ev.evidence_type == EvidenceType.DOCUMENT.value and ev.id:
        file_url = f"work-projects/evidences/{ev.id}/file"
    return {
        "id": ev.id,
        "subfolder_id": ev.subfolder_id,
        "evidence_type": ev.evidence_type,
        "name": ev.name,
        "progress_percent": ev.progress_percent or 0,
        "url": ev.url,
        "file_name": ev.file_name,
        "file_url": file_url,
        "order_index": ev.order_index,
        "group_id": ev.group_id,
    }


def build_subfolder_response(sf: WorkSubfolderModel, base_api: str = "") -> dict:
    evidences = [build_evidence_response(e, base_api) for e in sorted(sf.evidences, key=lambda x: x.order_index)]
    return {
        "id": sf.id,
        "project_id": sf.project_id,
        "name": sf.name,
        "order_index": sf.order_index,
        "progress_percent": _avg_progress(list(sf.evidences)),
        "evidences": evidences,
    }


def build_folder_response(folder: WorkFolderModel) -> dict:
    return {"id": folder.id, "name": folder.name, "order_index": folder.order_index}


def build_project_response(project: WorkProjectModel, base_api: str = "") -> dict:
    subfolders = [build_subfolder_response(sf, base_api) for sf in sorted(project.subfolders, key=lambda x: x.order_index)]
    logo_url = f"work-projects/{project.id}/logo" if project.logo_path else None
    folder_name = project.folder.name if project.folder else ""
    return {
        "id": project.id,
        "name": project.name,
        "folder_id": project.folder_id,
        "folder_name": folder_name,
        "logo_url": logo_url,
        "order_index": project.order_index,
        "progress_percent": _project_progress(list(project.subfolders)),
        "subfolders": subfolders,
    }

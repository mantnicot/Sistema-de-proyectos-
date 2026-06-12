from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.infrastructure.persistence.database import Base


class WorkProjectModel(Base):
    __tablename__ = "work_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    folder = Column(String(50), nullable=False, index=True)
    logo_path = Column(String(500), nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subfolders = relationship(
        "WorkSubfolderModel",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="WorkSubfolderModel.order_index",
    )


class WorkSubfolderModel(Base):
    __tablename__ = "work_subfolders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("work_projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    order_index = Column(Integer, default=0)

    project = relationship("WorkProjectModel", back_populates="subfolders")
    evidences = relationship(
        "WorkEvidenceModel",
        back_populates="subfolder",
        cascade="all, delete-orphan",
        order_by="WorkEvidenceModel.order_index",
    )


class WorkEvidenceModel(Base):
    __tablename__ = "work_evidences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subfolder_id = Column(Integer, ForeignKey("work_subfolders.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    progress_percent = Column(Float, default=0)
    url = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    order_index = Column(Integer, default=0)
    group_id = Column(Integer, nullable=True)

    subfolder = relationship("WorkSubfolderModel", back_populates="evidences")

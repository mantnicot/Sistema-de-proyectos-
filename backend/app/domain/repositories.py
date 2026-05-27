from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities import AuditLog, FormField, Project, User


class UserRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]: ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]: ...

    @abstractmethod
    def create(self, user: User, password_hash: str) -> User: ...


class FormFieldRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[FormField]: ...

    @abstractmethod
    def get_by_id(self, field_id: int) -> Optional[FormField]: ...

    @abstractmethod
    def create(self, field: FormField) -> FormField: ...

    @abstractmethod
    def update(self, field: FormField) -> FormField: ...

    @abstractmethod
    def delete(self, field_id: int) -> bool: ...

    @abstractmethod
    def reorder(self, field_ids: list[int]) -> list[FormField]: ...


class ProjectRepository(ABC):
    @abstractmethod
    def list_all(self, search: Optional[str] = None, sort_by: str = "name", sort_dir: str = "asc") -> list[Project]: ...

    @abstractmethod
    def get_by_id(self, project_id: int) -> Optional[Project]: ...

    @abstractmethod
    def create(self, project: Project) -> Project: ...

    @abstractmethod
    def update(self, project: Project) -> Project: ...

    @abstractmethod
    def delete(self, project_id: int) -> bool: ...


class AuditRepository(ABC):
    @abstractmethod
    def log(self, entry: AuditLog) -> AuditLog: ...

    @abstractmethod
    def list_recent(self, limit: int = 100) -> list[AuditLog]: ...

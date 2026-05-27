"""Configuración centralizada del sistema OATI."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Sistema de Gestión de Proyectos OATI"
    APP_VERSION: str = "1.0.1"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./oati_proyectos.db"

    JWT_SECRET_KEY: str = "oati-secret-key-cambiar-en-produccion"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    CORS_ORIGINS: str = "http://localhost:4200,http://127.0.0.1:4200"

    INSTITUCION_NOMBRE: str = "UNIVERSIDAD DISTRITAL FRANCISCO JOSÉ DE CALDAS"
    OATI_NOMBRE: str = "OFICINA ASESORA DE TECNOLOGÍAS E INFORMACIÓN"
    MACROPROCESO: str = "Gestión de Recursos"
    PROCESO: str = "de Apoyo"
    DOCUMENTO_VERSION: str = "02"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()

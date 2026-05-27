# Sistema de Gestión de Proyectos OATI

Plataforma web institucional para la creación, administración y exportación de proyectos de sistemas de la **Universidad Distrital Francisco José de Caldas** (OATI).

## Inicio rápido (un clic)

Doble clic en **`iniciar-sistema.bat`** — instala dependencias, levanta backend y frontend, y abre el navegador.

## URLs

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:4200 |
| API REST | http://localhost:8000/api/v1 |
| Swagger | http://localhost:8000/api/docs |

## Usuarios de prueba

| Rol | Usuario | Contraseña | Permisos |
|-----|---------|------------|----------|
| Admin | `admin` | `admin123` | Acceso total |
| General | `general` | `general123` | Solo ver y descargar proyectos |

## Documentación

| Documento | Descripción |
|-----------|-------------|
| [Manual de usuario](docs/MANUAL_USUARIO.md) | Guía completa de uso del sistema |
| [Diagramas de flujo](docs/DIAGRAMA_FLUJO.md) | Flujos de navegación, roles, proyectos y exportación |

## Módulos

- **Proyectos existentes** — listar, buscar, ordenar, ver detalle, exportar PDF/Word/Excel
- **Gestión de proyectos** — crear, editar, eliminar, duplicar con vista previa en tiempo real
- **Gestión de formulario** — constructor visual con drag & drop, tipos de campo configurables

## Stack

- **Frontend:** Angular 19, Standalone Components, Signals, Angular Material
- **Backend:** Python FastAPI, arquitectura hexagonal, JWT, SQLAlchemy
- **BD:** SQLite (local) / PostgreSQL (Docker)
- **Exportación:** PDF (ReportLab), Word (python-docx), Excel (openpyxl)

## Docker (producción)

```bash
docker compose up --build
```

Acceso: http://localhost

## Variables de entorno

Copie `backend/.env.example` a `backend/.env` y configure:

- `DATABASE_URL` — conexión PostgreSQL o SQLite
- `JWT_SECRET_KEY` — clave secreta JWT
- `CORS_ORIGINS` — orígenes permitidos

## Logos institucionales

Coloque los logos en `backend/assets/logos/`:

- `universidad.png` — escudo Universidad Distrital
- `oati.png` — logo OATI

Se usarán automáticamente en exportaciones PDF y Word.


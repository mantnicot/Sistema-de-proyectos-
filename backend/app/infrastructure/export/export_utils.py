"""Utilidades para exportación de documentos OATI."""
import io
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

LOGOS_DIR = Path(__file__).resolve().parents[3] / "assets" / "logos"
LOGO_UNIVERSIDAD = LOGOS_DIR / "universidad.png"
LOGO_OATI = LOGOS_DIR / "oati.png"

LOGO_UNIVERSIDAD_ALT = [
    LOGOS_DIR / "universidad.jpg",
    LOGOS_DIR / "universidad.jpeg",
    LOGOS_DIR / "universidad.svg",
]
LOGO_OATI_ALT = [
    LOGOS_DIR / "oati.jpg",
    LOGOS_DIR / "oati.jpeg",
    LOGOS_DIR / "oati.svg",
]


def _is_svg_file(path: Path) -> bool:
    try:
        with open(path, "rb") as handle:
            start = handle.read(256).lstrip()
        return start.startswith(b"<svg") or start.startswith(b"<?xml")
    except OSError:
        return False


def is_valid_image(path: Path) -> bool:
    if not path.exists():
        return False
    if _is_svg_file(path) or path.suffix.lower() == ".svg":
        return True
    try:
        from PIL import Image as PILImage

        with PILImage.open(path) as img:
            img.load()
        return True
    except ImportError:
        return path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    except Exception:
        return False


def resolve_logo(primary: Path, alternatives: list[Path]) -> Path | None:
    for candidate in [primary, *alternatives]:
        if candidate.exists() and is_valid_image(candidate):
            return candidate
    return None


def get_universidad_logo() -> Path | None:
    return resolve_logo(LOGO_UNIVERSIDAD, LOGO_UNIVERSIDAD_ALT)


def get_oati_logo() -> Path | None:
    return resolve_logo(LOGO_OATI, LOGO_OATI_ALT)


def load_logo_raster(path: Path | None) -> io.BytesIO | None:
    """Convierte logo (PNG/JPG/SVG) a imagen en memoria para Word y PDF."""
    if not path or not path.exists():
        return None
    try:
        if _is_svg_file(path) or path.suffix.lower() == ".svg":
            from reportlab.graphics import renderPM
            from svglib.svglib import svg2rlg

            drawing = svg2rlg(str(path))
            if not drawing:
                return None
            buf = io.BytesIO()
            renderPM.drawToFile(drawing, buf, fmt="PNG")
            buf.seek(0)
            return buf

        try:
            from PIL import Image as PILImage

            with PILImage.open(path) as img:
                img = img.convert("RGBA")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                return buf
        except ImportError:
            data = path.read_bytes()
            if data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n":
                return io.BytesIO(data)
            return None
    except Exception as exc:
        logger.warning("No se pudo rasterizar logo %s: %s", path, exc)
        return None


def format_field_value(value: Any, empty_label: str = "N/A") -> str:
    if value is None or value == "" or value == []:
        return empty_label
    if isinstance(value, list):
        counts: dict[str, int] = {}
        for item in value:
            key = str(item)
            counts[key] = counts.get(key, 0) + 1
        parts = [f"{label} ({n})" for label, n in counts.items()]
        return ", ".join(parts) if parts else empty_label
    return str(value)


def build_content_sections(project: dict, fields: list[dict]) -> list[tuple[str, str]]:
    description = (project.get("description") or "").strip()
    intro_text = description if description else "N/A"
    sections = [("INTRODUCCIÓN", intro_text)]
    idx = 1
    for field in fields:
        label = field.get("label", field.get("name", ""))
        key = field.get("name", "")
        value = format_field_value(project.get("data", {}).get(key, ""))
        sections.append((f"{idx}. {label.upper()}", value))
        idx += 1
    return sections


def collect_excel_columns(projects: list[dict], fields: list[dict]) -> list[tuple[str, str]]:
    """Unión de TODAS las columnas: formulario actual + claves de cada proyecto."""
    label_map: dict[str, str] = {}
    for field in fields:
        name = field.get("name", "")
        if name:
            label_map[name] = field.get("label", name)

    ordered_keys: list[str] = []
    seen: set[str] = set()

    for field in fields:
        name = field.get("name", "")
        if name and name not in seen:
            ordered_keys.append(name)
            seen.add(name)

    extra_keys: list[str] = []
    for proj in projects:
        for key in (proj.get("data") or {}).keys():
            if key and key not in seen:
                extra_keys.append(key)
                seen.add(key)
    ordered_keys.extend(sorted(extra_keys))

    return [(key, label_map.get(key, key.replace("_", " ").title())) for key in ordered_keys]

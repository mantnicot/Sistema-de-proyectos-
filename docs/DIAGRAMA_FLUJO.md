# Diagramas de Flujo
## Sistema de Gestión de Proyectos OATI

Este documento describe los flujos principales del sistema mediante diagramas. Puede visualizarlos en GitHub, VS Code (extensión Mermaid) o en [mermaid.live](https://mermaid.live).

---

## 1. Flujo general del sistema

Visión de alto nivel desde el acceso hasta las operaciones principales.

```mermaid
flowchart TD
    A([Inicio]) --> B[Página de bienvenida<br/>localhost:4200]
    B --> C{Usuario hace clic en<br/>INGRESO AL SISTEMA?}
    C -->|No| B
    C -->|Sí| D[Modal de login]
    D --> E{Credenciales<br/>válidas?}
    E -->|No| F[Mensaje: Credenciales inválidas]
    F --> D
    E -->|Sí| G[Panel Home /dashboard]
    G --> H[Proyectos existentes]
    G --> I[Gestión de proyectos]
    G --> J[Gestión de formulario]
    G --> K[Salir]
    K --> B

    H --> H1[Buscar / Ordenar]
    H --> H2[Ver detalle]
    H --> H3[Vista previa]
    H --> H4[Exportar PDF / Word / Excel]

    I --> I1[Crear proyecto]
    I --> I2[Editar proyecto]
    I --> I3[Duplicar proyecto]
    I --> I4[Eliminar proyecto]

    J --> J1[Crear campo]
    J --> J2[Editar / Duplicar / Eliminar campo]
    J --> J3[Reordenar campos]

    style I fill:#fde8e8,stroke:#9B2D2D
    style J fill:#fde8e8,stroke:#9B2D2D
    style I1 fill:#fde8e8,stroke:#9B2D2D
    style I2 fill:#fde8e8,stroke:#9B2D2D
    style I3 fill:#fde8e8,stroke:#9B2D2D
    style I4 fill:#fde8e8,stroke:#9B2D2D
    style J1 fill:#fde8e8,stroke:#9B2D2D
    style J2 fill:#fde8e8,stroke:#9B2D2D
    style J3 fill:#fde8e8,stroke:#9B2D2D
```

> Los nodos en rojo claro corresponden a funciones **exclusivas del rol Admin**.

---

## 2. Flujo de autenticación

```mermaid
flowchart TD
    A([Usuario en página de inicio]) --> B[Clic en INGRESO AL SISTEMA]
    B --> C[Ingresar usuario y contraseña]
    C --> D{Campos<br/>completos?}
    D -->|No| E[Error: Ingrese usuario y contraseña]
    E --> C
    D -->|Sí| F[Enviar credenciales al servidor]
    F --> G{Servidor valida<br/>usuario y contraseña?}
    G -->|No| H[Error: Credenciales inválidas]
    H --> C
    G -->|Sí| I[Generar token de sesión JWT]
    I --> J{¿Rol del usuario?}
    J -->|admin| K[Home con acceso completo]
    J -->|general| L[Home con acceso de consulta]
    K --> M([Sesión activa — máx. 8 horas])
    L --> M
    M --> N{Usuario hace clic en Salir?}
    N -->|Sí| O[Eliminar sesión local]
    O --> A
    N -->|No| M
```

---

## 3. Flujo por rol de usuario

```mermaid
flowchart LR
    subgraph PUBLICO["Acceso público"]
        P1[Página de bienvenida]
        P2[Login]
    end

    subgraph GENERAL["Rol: General"]
        G1[Home]
        G2[Proyectos existentes]
        G3[Buscar y ordenar]
        G4[Ver detalle]
        G5[Vista previa]
        G6[Exportar PDF / Word / Excel]
    end

    subgraph ADMIN["Rol: Admin"]
        A1[Home]
        A2[Proyectos existentes]
        A3[Gestión de proyectos]
        A4[Gestión de formulario]
        A5[CRUD proyectos]
        A6[CRUD campos formulario]
    end

    P1 --> P2
    P2 -->|general| G1
    P2 -->|admin| A1
    G1 --> G2 --> G3 --> G4 --> G5 --> G6
    A1 --> A2
    A1 --> A3 --> A5
    A1 --> A4 --> A6
    A2 --> G6
```

---

## 4. Flujo de consulta y exportación (Admin y General)

```mermaid
flowchart TD
    A([Proyectos existentes]) --> B[Cargar lista de proyectos]
    B --> C{¿Hay proyectos?}
    C -->|No| D[Mensaje: No hay proyectos registrados]
    C -->|Sí| E[Mostrar tabla de proyectos]

    E --> F{Acción del usuario}
    F -->|Buscar| G[Escribir término + Buscar]
    G --> E
    F -->|Ordenar| H[Clic en columna ID / Nombre / Descripción]
    H --> E
    F -->|Ver detalle| I[Modal con todos los campos]
    F -->|Vista previa| J[Modal documento simulado]
    F -->|Generar PDF| K[Confirmar → Descargar PDF]
    F -->|Generar Word| L[Confirmar → Descargar DOCX]
    F -->|Exportar Excel| M[Confirmar → Descargar XLSX global]

    I --> N{Desde detalle}
    N -->|Vista previa| J
    N -->|Descargar PDF| K

    K --> O([Archivo descargado])
    L --> O
    M --> O
```

---

## 5. Flujo de gestión de proyectos (solo Admin)

```mermaid
flowchart TD
    A([Gestión de proyectos]) --> B[Listado de proyectos]
    B --> C{Acción}

    C -->|Crear proyecto| D[Formulario vacío + campos dinámicos]
    C -->|Editar| E[Cargar datos del proyecto]
    C -->|Duplicar| F[Confirmar duplicación]
    C -->|Eliminar| G[Confirmar eliminación]

    D --> H[Completar nombre, descripción y campos]
    E --> H

    H --> I[Vista previa en tiempo real<br/>panel derecho]
    I --> J{Guardar proyecto?}
    J -->|Cancelar| B
    J -->|Sí| K{Nombre<br/>completado?}
    K -->|No| L[Error: El nombre es obligatorio]
    L --> H
    K -->|Sí| M{Campos obligatorios<br/>válidos?}
    M -->|No| N[Mostrar errores de validación]
    N --> H
    M -->|Sí| O[Confirmar guardado]
    O --> P[Guardar en base de datos]
    P --> Q[Mensaje: Proyecto guardado correctamente]
    Q --> B

    F --> R[Crear copia con sufijo 'copia']
    R --> S[Mensaje: Proyecto duplicado]
    S --> B

    G --> T[Eliminar de base de datos]
    T --> U[Mensaje: Proyecto eliminado]
    U --> B
```

---

## 6. Flujo de gestión de formulario (solo Admin)

```mermaid
flowchart TD
    A([Gestión de formulario]) --> B[Cargar campos existentes]
    B --> C[Panel: lista de campos + vista previa]

    C --> D{Acción}

    D -->|Crear campo| E[Modal: configurar nuevo campo]
    D -->|Editar| F[Modal: modificar campo]
    D -->|Duplicar| G[Confirmar → copia _copia]
    D -->|Eliminar| H[Confirmar → eliminar campo]
    D -->|Reordenar| I[Arrastrar campo ⋮⋮]
    D -->|Cambiar ancho| J[Deslizador Ancho %]

    E --> K{Nombre y etiqueta<br/>completos?}
    F --> K
    K -->|No| L[Error: Nombre y etiqueta obligatorios]
    L --> E
    K -->|Sí| M[Confirmar guardado]
    M --> N[Actualizar formulario]
    N --> C

    G --> C
    H --> C
    I --> O[Guardar nuevo orden automáticamente]
    O --> C
    J --> P[Guardar ancho automáticamente]
    P --> C
```

---

## 7. Flujo de exportación de documentos

```mermaid
flowchart TD
    A([Solicitud de exportación]) --> B{Formato}

    B -->|PDF| C[Seleccionar proyecto]
    B -->|Word| D[Seleccionar proyecto]
    B -->|Excel| E[Todos los proyectos]

    C --> F[Confirmar: ¿Generar PDF?]
    D --> G[Confirmar: ¿Generar Word?]
    E --> H[Confirmar: ¿Generar Excel?]

    F --> I[Backend genera PDF institucional]
    G --> J[Backend genera DOCX institucional]
    H --> K[Backend genera XLSX con todos los datos]

    I --> L[Descargar proyecto_ID.pdf]
    J --> M[Descargar proyecto_ID.docx]
    K --> N[Descargar proyectos_oati.xlsx]

    L --> O([Fin])
    M --> O
    N --> O
```

### Estructura del documento PDF/Word

```mermaid
flowchart TB
    A[Documento exportado] --> B[Cabecera institucional<br/>Logos UD + OATI]
    B --> C[Portada<br/>Nombre del proyecto]
    C --> D[Tabla de contenido]
    D --> E[INTRODUCCIÓN<br/>Descripción del proyecto]
    E --> F[Sección 1 — Campo 1]
    F --> G[Sección 2 — Campo 2]
    G --> H[...]
    H --> I[Sección N — Campo N]
    I --> J[Pie de página<br/>Página X de Y]
```

---

## 8. Flujo de navegación entre pantallas

```mermaid
stateDiagram-v2
    [*] --> Landing: Abrir aplicación

    Landing --> LoginModal: INGRESO AL SISTEMA
    LoginModal --> Landing: Cancelar / Error
    LoginModal --> Home: Login exitoso

    state Dashboard {
        Home --> ProyectosExistentes: Menú / enlace
        Home --> GestionProyectos: Menú / enlace (admin)
        Home --> GestionFormulario: Menú / enlace (admin)

        ProyectosExistentes --> Home: Menú Home
        GestionProyectos --> Home: Menú Home
        GestionFormulario --> Home: Menú Home

        ProyectosExistentes --> GestionProyectos: Menú (admin)
        GestionProyectos --> ProyectosExistentes: Menú
        GestionFormulario --> ProyectosExistentes: Menú

        GestionProyectos --> FormularioProyecto: Crear / Editar
        FormularioProyecto --> GestionProyectos: Guardar / Cancelar
    }

    Home --> Landing: Salir
    ProyectosExistentes --> Landing: Salir
    GestionProyectos --> Landing: Salir
    GestionFormulario --> Landing: Salir
```

---

## 9. Flujo de validación al guardar un proyecto

```mermaid
flowchart TD
    A([Guardar Proyecto]) --> B[Enviar datos al servidor]
    B --> C{¿Nombre del proyecto<br/>informado?}
    C -->|No| D[400 — Nombre obligatorio]
    C -->|Sí| E[Validar cada campo dinámico]

    E --> F{Campo obligatorio<br/>vacío?}
    F -->|Sí| G[400 — Error: campo requerido]
    F -->|No| H{Tipo numérico<br/>válido y en rango?}
    H -->|No| I[400 — Error: valor numérico inválido]
    H -->|Sí| J{Texto supera<br/>máximo de caracteres?}
    J -->|Sí| K[400 — Error: longitud excedida]
    J -->|No| L{¿Más campos<br/>por validar?}
    L -->|Sí| E
    L -->|No| M[Guardar en base de datos]
    M --> N[Registrar auditoría]
    N --> O[200 — Proyecto guardado correctamente]

    D --> P[Mostrar error al usuario]
    G --> P
    I --> P
    K --> P
    O --> Q([Volver al listado])
```

---

## Leyenda

| Símbolo / Color | Significado |
|-----------------|-------------|
| `([  ])` | Inicio o fin de proceso |
| `{  }` | Decisión / condición |
| `[  ]` | Acción o pantalla |
| Nodos rojo claro | Solo rol **Admin** |
| Flecha → | Flujo secuencial |

---

*Diagramas del Sistema de Gestión de Proyectos OATI — Universidad Distrital Francisco José de Caldas.*

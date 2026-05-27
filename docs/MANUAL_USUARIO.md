# Manual de Usuario
## Sistema de Gestión de Proyectos OATI

**Universidad Distrital Francisco José de Caldas**  
**Oficina Asesora de Tecnologías e Información (OATI)**

| Versión del documento | 1.0 |
|-----------------------|-----|
| Versión del sistema   | 1.0.1 |
| Fecha                 | Mayo 2026 |

---

## Tabla de contenido

1. [Introducción](#1-introducción)
2. [Requisitos y acceso al sistema](#2-requisitos-y-acceso-al-sistema)
3. [Roles de usuario](#3-roles-de-usuario)
4. [Pantalla de inicio e ingreso al sistema](#4-pantalla-de-inicio-e-ingreso-al-sistema)
5. [Panel principal (Home)](#5-panel-principal-home)
6. [Proyectos existentes](#6-proyectos-existentes)
7. [Gestión de proyectos (solo Admin)](#7-gestión-de-proyectos-solo-admin)
8. [Gestión de formulario (solo Admin)](#8-gestión-de-formulario-solo-admin)
9. [Exportación de documentos](#9-exportación-de-documentos)
10. [Vista previa del documento](#10-vista-previa-del-documento)
11. [Mensajes del sistema](#11-mensajes-del-sistema)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Soporte](#13-soporte)

---

## 1. Introducción

El **Sistema de Gestión de Proyectos OATI** es una plataforma web institucional que permite registrar, consultar, administrar y exportar proyectos de sistemas de forma estandarizada, con documentos en formato institucional de la Universidad Distrital.

### Objetivo del sistema

Brindar una forma automática y uniforme de generar proyectos, reduciendo tiempos de elaboración documental y garantizando consistencia en la estructura de los entregables.

### Módulos principales

| Módulo | Descripción |
|--------|-------------|
| **Proyectos existentes** | Consulta, búsqueda, detalle y descarga de proyectos |
| **Gestión de proyectos** | Creación, edición, duplicación y eliminación de proyectos |
| **Gestión de formulario** | Diseño del formulario dinámico que alimenta los proyectos |

---

## 2. Requisitos y acceso al sistema

### Requisitos

- Navegador web actualizado (Chrome, Edge, Firefox o Safari).
- Conexión a la red donde esté desplegado el sistema.
- Usuario y contraseña asignados por el administrador.

### Acceso

| Entorno local | URL |
|---------------|-----|
| Aplicación web | http://localhost:4200 |
| API (referencia técnica) | http://localhost:8000/api/v1 |

### Inicio del sistema (entorno local)

Ejecute el archivo **`iniciar-sistema.bat`** en la carpeta del proyecto. El script instalará dependencias, iniciará backend y frontend, y abrirá el navegador automáticamente.

---

## 3. Roles de usuario

El sistema maneja dos perfiles con permisos diferenciados:

### Usuario Admin

Acceso completo al sistema. Puede:

- Consultar y exportar proyectos.
- Crear, editar, duplicar y eliminar proyectos.
- Configurar los campos del formulario (tipos, orden, obligatoriedad).

### Usuario General

Acceso de consulta y exportación. Puede:

- Consultar la lista de proyectos.
- Buscar, ordenar y ver el detalle de cada proyecto.
- Generar documentos PDF, Word y Excel.

**No puede** crear, modificar ni eliminar proyectos ni campos del formulario.

### Matriz de permisos

| Acción | Admin | General |
|--------|:-----:|:-------:|
| Iniciar / cerrar sesión | ✓ | ✓ |
| Ver panel principal (Home) | ✓ | ✓ |
| Proyectos existentes | ✓ | ✓ |
| Buscar y ordenar proyectos | ✓ | ✓ |
| Ver detalle y vista previa | ✓ | ✓ |
| Exportar PDF / Word / Excel | ✓ | ✓ |
| Gestión de proyectos (CRUD) | ✓ | ✗ |
| Gestión de formulario | ✓ | ✗ |

### Usuarios de demostración

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Admin | `admin` | `admin123` |
| General | `general` | `general123` |

> **Nota:** En producción, use las credenciales asignadas por el administrador del sistema. Cambie las contraseñas de demostración antes de un despliegue real.

---

## 4. Pantalla de inicio e ingreso al sistema

Al abrir la aplicación se muestra la **página de bienvenida** con la identidad institucional de la Universidad Distrital y la OATI.

### Elementos de la pantalla

- Título: *Sistema de gestión de proyectos*
- Descripción del propósito del sistema.
- Botón **INGRESO AL SISTEMA**
- Pie de página con datos de contacto de la OATI:
  - Horario: Lunes a viernes, 8:00 a.m. – 5:00 p.m.
  - Teléfono: 323 93 00 Ext. 1112
  - Dirección: Cra 8 # 40-78 Piso 1
  - Correo: Computo@udistrital.edu.co

### Procedimiento: iniciar sesión

1. Haga clic en **INGRESO AL SISTEMA**.
2. Se abrirá una ventana con los campos **Usuario** y **Contraseña**.
3. Digite sus credenciales.
4. Haga clic en **Ingresar** (o presione Enter).
5. Si las credenciales son correctas, será redirigido al panel principal.
6. Si son incorrectas, verá el mensaje *Credenciales inválidas.*

Para cancelar el ingreso, use **Cancelar** o el botón **×** de la ventana.

### Cerrar sesión

En cualquier pantalla del panel, haga clic en **Salir** (parte superior derecha). Será redirigido a la página de inicio.

---

## 5. Panel principal (Home)

Tras iniciar sesión accede al **Home**, el punto de entrada del sistema.

### Información mostrada

- Mensaje de bienvenida: *Bienvenido, [nombre de usuario].*
- Rol asignado: *Rol: admin* o *Rol: general*
- Accesos rápidos según su perfil

### Accesos rápidos

| Enlace | Disponible para |
|--------|-----------------|
| Ver proyectos existentes | Todos |
| Gestión de proyectos | Solo Admin |
| Gestión de formulario | Solo Admin |

### Menú lateral

El menú lateral permanece visible en todas las pantallas del panel:

| Opción | Descripción |
|--------|-------------|
| **Home** | Panel principal |
| **Proyectos existentes** | Consulta y exportación |
| **Gestión Proyectos** | CRUD de proyectos *(solo Admin)* |
| **Gestión de formulario** | Constructor de campos *(solo Admin)* |

---

## 6. Proyectos existentes

Módulo disponible para **todos los usuarios autenticados**. Permite consultar el inventario de proyectos registrados.

### Funciones disponibles

| Función | Descripción |
|---------|-------------|
| **Buscar** | Filtra por nombre o descripción |
| **Ordenar** | Ordena por ID, Nombre o Descripción (clic en el encabezado de columna) |
| **Ver detalle** | Muestra todos los campos del proyecto en una ventana |
| **Vista previa** | Simula el documento institucional final |
| **Generar PDF** | Descarga el proyecto en formato PDF |
| **Generar Word** | Descarga el proyecto en formato Word (.docx) |
| **Exportar Excel** | Descarga un archivo Excel con todos los proyectos |

### Procedimiento: consultar un proyecto

1. En el menú lateral, seleccione **Proyectos existentes**.
2. *(Opcional)* Escriba un término en *Buscar proyectos...* y pulse **Buscar**.
3. *(Opcional)* Ordene la tabla haciendo clic en **ID**, **Nombre** o **Descripción**.
4. En la columna **Acciones**, use los botones disponibles:
   - **Ver detalle** — abre una ventana con todos los datos.
   - **Vista previa** — muestra el documento simulado.
   - **Generar PDF** / **Generar Word** — descarga el archivo correspondiente.

### Ventana de detalle

Muestra:

- Nombre del proyecto
- Descripción (o *Sin descripción*)
- Todos los campos dinámicos con sus valores
- Valores vacíos se indican como **N/A**

Desde esta ventana puede ir a **Vista previa** o **Descargar PDF**.

### Exportar todos los proyectos a Excel

1. En la barra superior de la lista, haga clic en **Exportar Excel**.
2. Confirme la acción en el diálogo.
3. Se descargará el archivo `proyectos_oati.xlsx`.

---

## 7. Gestión de proyectos (solo Admin)

Este módulo permite el ciclo de vida completo de los proyectos: crear, editar, duplicar y eliminar.

### Listado de proyectos

- Encabezado: **GESTIÓN DE PROYECTOS**
- Botón **Crear proyecto**
- Tabla con columnas: ID, Nombre, Descripción, Acciones
- Acciones por fila: **Editar**, **Duplicar**, **Eliminar**

### Procedimiento: crear un proyecto

1. Vaya a **Gestión Proyectos** en el menú lateral.
2. Haga clic en **Crear proyecto**.
3. Complete los campos fijos:
   - **Nombre del proyecto** *(obligatorio)*
   - **Descripción** *(opcional — aparece como INTRODUCCIÓN en el documento exportado)*
4. Complete los **campos dinámicos** definidos en el formulario. Los obligatorios llevan asterisco (*).
5. Revise la **VISTA PREVIA DOCUMENTO** en el panel derecho (se actualiza en tiempo real).
6. Haga clic en **Guardar Proyecto**.
7. Confirme la acción. Verá el mensaje *Proyecto guardado correctamente.*

### Procedimiento: editar un proyecto

1. En el listado, haga clic en **Editar** en la fila del proyecto.
2. Modifique los campos necesarios.
3. Haga clic en **Guardar Proyecto** y confirme.

### Procedimiento: duplicar un proyecto

1. En el listado, haga clic en **Duplicar**.
2. Confirme en el diálogo (*¿Duplicar el proyecto "[nombre]"?*).
3. Se creará una copia con el sufijo *copia* en el nombre.

### Procedimiento: eliminar un proyecto

1. En el listado, haga clic en **Eliminar**.
2. Confirme en el diálogo (*¿Eliminar el proyecto "[nombre]"?*).
3. El proyecto se eliminará permanentemente.

> **Advertencia:** La eliminación no se puede deshacer.

### Cancelar edición

Use el botón **Cancelar** para volver al listado sin guardar cambios.

---

## 8. Gestión de formulario (solo Admin)

Este módulo define la estructura del formulario que se usa al crear y editar proyectos. Los cambios afectan a **todos los proyectos futuros** y a la validación al guardar.

### Interfaz

| Panel | Contenido |
|-------|-----------|
| **Izquierdo — GESTIÓN DE FORMULARIO** | Lista de campos, botón Crear campo, controles de edición |
| **Derecho — VISTA PREVIA INSTANTÁNEA** | Formulario completo con datos de prueba |

### Tipos de campo disponibles

| Tipo | Uso |
|------|-----|
| **Texto** | Texto corto (una línea) |
| **Texto largo** | Párrafos o descripciones extensas |
| **Entero** | Números enteros |
| **Decimal** | Números con decimales |
| **Porcentual** | Valores de 0 a 100 |
| **Tiempo** | Duración o cantidad de tiempo |
| **Lista** | Selección única o múltiple de opciones |
| **Imagen** | Archivo de imagen referencial |
| **Hipervínculo** | URL o enlace web |

### Procedimiento: crear un campo

1. Vaya a **Gestión de formulario**.
2. Haga clic en **Crear campo**.
3. Complete los datos:
   - **Nombre (identificador)** *(obligatorio, único — no se puede cambiar después)*
   - **Etiqueta visible** *(obligatorio — texto que ve el usuario)*
   - **Tipo de campo**
   - **Placeholder** *(texto de ayuda dentro del campo)*
   - **Ancho (%)** — entre 25 y 100
   - **Obligatorio** — marque si el campo es requerido al guardar un proyecto
4. Según el tipo, configure propiedades adicionales:
   - *Texto largo:* altura en filas (1–10)
   - *Numéricos:* valor mínimo y máximo
   - *Texto:* máximo de caracteres
   - *Lista:* opciones de la lista y selección múltiple (si aplica)
5. Haga clic en **Guardar** y confirme.

### Procedimiento: reordenar campos

Arrastre el icono **⋮⋮** (*Arrastrar para reordenar*) de cada campo. El nuevo orden se guarda automáticamente y define el orden en formularios y documentos exportados.

### Procedimiento: editar, duplicar o eliminar un campo

En cada campo del listado, use el menú de acciones:

| Acción | Efecto |
|--------|--------|
| **Editar** | Modifica propiedades (excepto el identificador) |
| **Duplicar** | Crea una copia con sufijo `_copia` |
| **Eliminar** | Elimina el campo del formulario |

> **Nota:** Eliminar un campo no borra los datos ya guardados en proyectos existentes, pero el campo dejará de aparecer en formularios y exportaciones futuras.

### Campos precargados del sistema

Al instalar el sistema por primera vez se crean estos campos de ejemplo:

| Campo | Tipo | Obligatorio |
|-------|------|:-----------:|
| Objeto del proyecto | Texto largo | Sí |
| Alcance | Texto | Sí |
| Recursos | Lista (múltiple) | No |
| Estimación - Números | Entero | No |
| Estimación - Medida | Lista | No |
| Justificación (Necesidad) | Texto | Sí |
| Impacto | Texto | No |
| Alineación | Texto | No |
| Descripción | Texto largo | No |

---

## 9. Exportación de documentos

El sistema genera documentos con formato institucional de la Universidad Distrital y la OATI.

### Formatos disponibles

| Formato | Alcance | Archivo generado |
|---------|---------|------------------|
| **PDF** | Un proyecto | `proyecto_[id].pdf` |
| **Word** | Un proyecto | `proyecto_[id].docx` |
| **Excel** | Todos los proyectos | `proyectos_oati.xlsx` |

### Procedimiento: exportar PDF o Word

1. Vaya a **Proyectos existentes**.
2. Localice el proyecto en la tabla.
3. Haga clic en **Generar PDF** o **Generar Word**.
4. Confirme la acción.
5. El archivo se descargará automáticamente en su carpeta de descargas.

También puede exportar desde la ventana de **Ver detalle** usando **Descargar PDF**.

### Procedimiento: exportar Excel

1. En **Proyectos existentes**, haga clic en **Exportar Excel** (barra superior).
2. Confirme la acción.
3. Se descargará `proyectos_oati.xlsx` con todos los proyectos y sus campos.

### Contenido del documento PDF/Word

Los documentos exportados incluyen:

- Logos institucionales (Universidad Distrital y OATI)
- Cabecera con macroproceso, proceso, código y versión
- Portada con nombre del proyecto
- Tabla de contenido
- Sección **INTRODUCCIÓN** (descripción del proyecto)
- Secciones numeradas por cada campo del formulario
- Pie de página con numeración

---

## 10. Vista previa del documento

La vista previa simula el aspecto del documento final **antes de exportarlo**.

### Dónde está disponible

| Ubicación | Cuándo usarla |
|-----------|---------------|
| **Proyectos existentes → Vista previa** | Revisar un proyecto ya guardado |
| **Gestión de proyectos → panel derecho** | Ver cambios en tiempo real al crear/editar |
| **Gestión de formulario → VISTA PREVIA INSTANTÁNEA** | Probar cómo se verá el formulario |

Use la vista previa para verificar que la información esté completa y bien estructurada antes de generar PDF o Word.

---

## 11. Mensajes del sistema

### Diálogos de confirmación

Antes de acciones importantes, el sistema solicita confirmación:

| Acción | Mensaje |
|--------|---------|
| Crear proyecto | *¿Confirmar creación del proyecto?* |
| Editar proyecto | *¿Confirmar modificación del proyecto?* |
| Eliminar proyecto | *¿Eliminar el proyecto "[nombre]"?* |
| Duplicar proyecto | *¿Duplicar el proyecto "[nombre]"?* |
| Guardar campo | *¿Guardar campo?* |
| Eliminar campo | *¿Eliminar el campo "[etiqueta]"?* |
| Generar PDF | *¿Generar PDF del proyecto "[nombre]"?* |
| Generar Word | *¿Generar Word del proyecto "[nombre]"?* |
| Exportar Excel | *¿Generar Excel con todos los proyectos?* |

### Mensajes de carga

Durante operaciones, verá indicadores como:

- *Validando identidad...*
- *Cargando proyectos...*
- *Guardando...*
- *Generando PDF...*
- *Generando Excel...*

### Mensajes de éxito

- *Proyecto guardado correctamente.*
- *Proyecto eliminado.*
- *Proyecto duplicado.*
- *PDF generado correctamente.*
- *Excel generado correctamente.*

### Mensajes de error frecuentes

| Situación | Mensaje |
|-----------|---------|
| Login sin datos | *Ingrese usuario y contraseña.* |
| Credenciales incorrectas | *Credenciales inválidas.* |
| Nombre de proyecto vacío | *El nombre del proyecto es obligatorio.* |
| Campo sin nombre o etiqueta | *Nombre y etiqueta son obligatorios.* |
| Error de conexión | *No se pudieron cargar los proyectos.* |
| Validación del servidor | Detalle específico del campo con error |

---

## 12. Preguntas frecuentes

**¿Por qué no veo "Gestión Proyectos" en el menú?**  
Esa opción solo está disponible para usuarios con rol **Admin**. Si necesita esos permisos, contacte al administrador del sistema.

**¿Puedo recuperar un proyecto eliminado?**  
No. La eliminación es permanente. Use **Duplicar** antes de eliminar si desea conservar una copia.

**¿Los cambios en el formulario afectan proyectos ya creados?**  
Los proyectos existentes conservan sus datos. Los cambios en campos (nuevos, eliminados o reordenados) se reflejan en formularios y exportaciones futuras.

**¿Por qué un campo obligatorio no me deja guardar?**  
Verifique que todos los campos marcados con * estén completos. Los campos numéricos deben respetar los límites mínimo y máximo configurados.

**¿Cuánto dura la sesión?**  
La sesión expira después de **8 horas** de inactividad. Deberá iniciar sesión nuevamente.

**¿Puedo usar el sistema sin conexión a internet?**  
En entorno local (localhost), no requiere internet; solo que backend y frontend estén en ejecución.

---

## 13. Soporte

Para soporte técnico o solicitud de credenciales, contacte a la OATI:

| | |
|---|---|
| **Horario** | Lunes a viernes, 8:00 a.m. – 5:00 p.m. |
| **Teléfono** | 323 93 00 Ext. 1112 |
| **Dirección** | Cra 8 # 40-78 Piso 1 |
| **Correo** | Computo@udistrital.edu.co |

---

*Documento generado para el Sistema de Gestión de Proyectos OATI — Universidad Distrital Francisco José de Caldas.*

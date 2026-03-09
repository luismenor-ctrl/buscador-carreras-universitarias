# Informe técnico: Buscador de Carreras Universitarias (RUCT)

**Fecha:** marzo de 2026
**Tecnología principal:** Python · Streamlit · BeautifulSoup · requests
**Despliegue:** Streamlit Community Cloud

---

## 1. Qué hace la aplicación

La aplicación permite consultar en tiempo real el **RUCT** (Registro de Universidades, Centros y Títulos), el registro oficial del Ministerio de Educación de España donde se encuentran catalogadas todas las titulaciones universitarias del país.

El usuario puede:

1. **Buscar titulaciones** filtrando por nombre, nivel académico (Grado, Máster, Doctorado), rama de conocimiento y universidad.
2. **Ver los resultados** paginados con el nombre del título y la universidad que lo imparte.
3. **Consultar el plan de estudios** de cualquier titulación haciendo clic en el botón «Ver» — la app obtiene y muestra automáticamente las asignaturas, créditos y carácter (obligatoria, optativa, etc.) tal como aparecen en la publicación oficial del BOE.
4. **Exportar los resultados** de la búsqueda en formato CSV o Excel.

---

## 2. Arquitectura general

La aplicación se compone de dos ficheros Python:

| Fichero | Responsabilidad |
| --- | --- |
| `ruct_scraper.py` | Motor de búsqueda en el RUCT: sesión HTTP, POST de búsqueda, paginación, parseo de la tabla de resultados, exportación CSV/Excel |
| `app.py` | Interfaz Streamlit: formulario de búsqueda, lista de resultados, vista de detalle con el plan de estudios, CSS / modo oscuro |

---

## 3. Flujo de búsqueda (`ruct_scraper.py`)

### 3.1 Inicialización de opciones del formulario

Al arrancar, `load_form_options()` hace un `GET` a `consultaestudios.action` y extrae los `<select>` del formulario del RUCT (lista de universidades, tipos de estudio, ramas de conocimiento, etc.). Si la petición falla, se usan valores predefinidos como fallback.

### 3.2 Búsqueda con paginación

`search_ruct()` realiza:

1. `GET consultaestudios.action` — abre sesión y obtiene cookies.
2. `POST consultaestudios.action?actual=estudios` — envía el formulario con los filtros del usuario.
3. Parseo de la tabla de resultados (`_parse_table`): extrae código, título, universidad, nivel, estado, y dos URLs por fila:
   - `url_ruct`: enlace a la ficha del título en el RUCT (`estudio.action?codigoEstudio=…`).
   - `url_plan`: enlace a la «lupa» del plan de estudios (`consultaplanestudios.action?…`).
4. Paginación automática: sigue el enlace «Siguiente» hasta agotar los resultados o alcanzar el límite de 200 páginas.

### 3.3 Normalización de acentos

El RUCT devuelve cero resultados si la consulta contiene tildes. La función `_strip_accents()` normaliza el texto usando `unicodedata.NFD` antes de enviarlo, de modo que «Ingeniería» se envía como «Ingenieria» y la búsqueda funciona correctamente.

---

## 4. Obtención del plan de estudios (`app.py`)

Éste es el proceso más complejo de la aplicación. El objetivo es mostrar el contenido real del plan de estudios (asignaturas, créditos, carácter, organización temporal) tal como aparece en el BOE.

### 4.1 Por qué el RUCT no es suficiente por sí solo

La mayoría de páginas del RUCT se renderizan mediante JavaScript en el cliente, lo que significa que un `GET` directo devuelve HTML vacío. La excepción es la página `estudio.action`, que sí devuelve HTML completo **una vez que la sesión del servidor está correctamente inicializada**.

### 4.2 Cadena de tres peticiones HTTP para obtener la URL del BOE

`_fetch_boe_url_from_ruct(url_ruct, url_plan)` ejecuta la siguiente secuencia con un único objeto `requests.Session`:

```
1. GET consultaestudios.action       ← inicializa la sesión en el servidor
2. GET url_plan  (lupa)              ← registra esta titulación en la sesión
3. GET url_ruct  (estudio.action)    ← ahora devuelve el HTML completo
```

Tras el paso 3, el HTML contiene el `div#ttwo` con todas las fechas y enlaces del BOE. Dentro de ese div, la etiqueta `<label for="f_plan">` envuelve el enlace al PDF de la «Publicación Plan Estudios en el BOE».

### 4.3 Conversión del PDF del BOE a HTML legible

Los PDFs del BOE tienen un equivalente HTML en `https://www.boe.es/diario_boe/txt.php?id=BOE-A-XXXX-XXXX`. La función `_boe_pdf_to_html()` convierte la URL del PDF a este formato extrayendo el identificador con una expresión regular.

### 4.4 Extracción del contenido del BOE

`_fetch_boe_plan(url)` descarga la página HTML del BOE y extrae únicamente el contenido relevante:

- Localiza el `div#textoxslt`, que contiene el texto del documento.
- Elimina scripts, estilos y enlaces.
- **Omite el preámbulo legal**: el documento comienza con el texto de la resolución ministerial, que no es parte del plan. La función salta todo el contenido hasta encontrar la primera tabla.
- Convierte cada tabla HTML a formato Markdown usando `_html_table_to_md()`, que genera tablas con cabecera y separador.
- Limita el resultado a 12 000 caracteres para evitar tiempos de carga excesivos.

### 4.5 Fallback: módulos del RUCT

Si no se encuentra un enlace al BOE (algunas titulaciones no tienen la publicación del plan enlazada), `_fetch_ruct_modules(url_plan)` intenta una ruta alternativa:

```
1. GET consultaestudios.action
2. GET url_plan
3. GET datosModulo?actual=menu.solicitud.planificacion.materiasSin&codModulo=0
```

El endpoint `datosModulo` es el único subpágina del RUCT que devuelve HTML estático (sin JavaScript). Contiene una tabla con los módulos y materias de la titulación. No incluye créditos ni carácter, pero proporciona al menos los nombres de las asignaturas.

### 4.6 Caché en sesión

Los planes de estudios ya consultados se almacenan en `st.session_state["study_plans"]` con una clave compuesta por título + universidad. Si el usuario vuelve a consultar la misma titulación, el resultado se sirve desde la caché sin hacer ninguna petición HTTP.

---

## 5. Interfaz de usuario (`app.py`)

### 5.1 Formulario de búsqueda

- Campo de texto libre para el nombre del título.
- Tres selectores: nivel académico, rama de conocimiento, universidad.
- Por defecto filtra titulaciones de **Grado**, **publicadas en el BOE** y **activas**.
- Botón «Buscar» como único punto de entrada (formulario Streamlit con `st.form`).

### 5.2 Lista de resultados

- Métricas rápidas: número de títulos y número de universidades distintas.
- Paginación de 25 resultados por página con control `st.number_input`.
- Una fila por resultado con nombre del título, universidad y botón «Ver».
- Mensajes de error descriptivos cuando el RUCT no responde o no hay resultados.

### 5.3 Vista de detalle

- Muestra nombre del título y universidad.
- Botón «Ver ficha en el RUCT →» con enlace directo a la ficha oficial.
- Spinner mientras se busca el plan de estudios.
- Si se encuentra la URL del BOE, botón «Ver en el BOE →».
- Contenido del plan en Markdown con tablas de asignaturas.
- Si no se puede obtener el plan, mensaje de aviso con instrucciones.
- Botón «← Volver a los resultados» para navegar de vuelta a la lista.

### 5.4 Exportación

La lista de resultados puede descargarse como CSV (con BOM UTF-8 para compatibilidad con Excel en Windows) o como archivo Excel con columnas de ancho ajustado automáticamente.

---

## 6. Compatibilidad visual (modo oscuro)

El CSS de la aplicación fuerza el modo claro en todos los sistemas operativos y navegadores mediante:

```css
html { color-scheme: light only !important; }
```

Además, hay un bloque `@media (prefers-color-scheme: dark)` que sobreescribe explícitamente los colores de fondo y texto de todos los contenedores de Streamlit, garantizando que la app se vea correctamente en macOS e iOS aunque el sistema tenga activado el modo oscuro.

---

## 7. Gestión de errores

| Situación | Comportamiento |
| --- | --- |
| RUCT no disponible al arrancar | Aviso en pantalla; filtros predefinidos como fallback |
| Búsqueda sin resultados | Mensaje descriptivo diferenciando «sin resultados» de «servidor no disponible» |
| Timeout en búsqueda | Se muestran los resultados parciales obtenidos hasta ese momento |
| RUCT devuelve página inesperada | Mensaje de error con sugerencia de reintentar |
| `url_plan` ausente | Se omite el paso de la lupa; se intenta `_fetch_ruct_modules` directamente |
| BOE inaccesible o sin tablas | Se usa el fallback de módulos del RUCT |
| Todo falla | Aviso con enlace a la ficha oficial del RUCT |

---

## 8. Dependencias

```
streamlit
requests
beautifulsoup4
lxml
pandas
openpyxl
```

No hay dependencias de modelos de inteligencia artificial ni APIs de pago. Toda la información se obtiene directamente de fuentes públicas (RUCT y BOE).

---

## 9. Despliegue

La aplicación está desplegada en **Streamlit Community Cloud** (gratuito), conectada al repositorio de GitHub rama `main`. Cualquier push a `main` actualiza la aplicación automáticamente.

---

## 10. Limitaciones conocidas

- El RUCT puede devolver cero resultados temporalmente si su servidor está bajo carga o en mantenimiento.
- Algunas titulaciones antiguas no tienen el plan de estudios enlazado en la ficha RUCT; en esos casos sólo se muestra la lista de módulos (sin créditos ni carácter).
- El contenido del BOE está limitado a 12 000 caracteres; planes de estudios muy extensos pueden aparecer truncados.
- La paginación de resultados está limitada a 200 páginas (≈ 2 000 resultados) para evitar tiempos de espera excesivos.

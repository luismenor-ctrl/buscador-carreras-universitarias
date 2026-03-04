"""
ruct_scraper.py
Scraping del RUCT (Registro de Universidades, Centros y Títulos)
https://www.educacion.gob.es/ruct/

El RUCT es la base de datos oficial del Ministerio de Educación con todos los
títulos universitarios oficiales de España (Grado, Máster, Doctorado, etc.).
"""

import io
import time
import logging
import unicodedata
import requests
from bs4 import BeautifulSoup
import pandas as pd

logger = logging.getLogger(__name__)

BASE_URL = "https://www.educacion.gob.es/ruct"
FORM_URL = f"{BASE_URL}/consultaestudios.action"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

# Mapeos de valores conocidos (evita una petición GET si la conexión es lenta)
RAMAS_CONOCIMIENTO = {
    "": "Todas",
    "431001": "Artes y Humanidades",
    "431002": "Ciencias",
    "431005": "Ciencias de la Salud",
    "431003": "Ciencias Sociales y Jurídicas",
    "431004": "Ingeniería y Arquitectura",
}

TIPOS_ESTUDIO = {
    "": "Todos",
    "G": "Grado",
    "M": "Máster",
    "D": "Doctor",
    "C": "Ciclo",
    "T": "Título Equivalente",
    "X": "Título Extranjero",
}

ESTADOS = {
    "": "Todos",
    "P": "Publicado en B.O.E.",
    "ACA": "Autorizado por Comunidad Autónoma",
    "AJ": "Afectado por Resolución Judicial",
}

SITUACIONES = {
    "": "Todos",
    "A": "Titulación Alta (activa)",
    "T": "Titulación Extinguida",
    "X": "Titulación a Extinguir",
}

COLUMNS_RESULTADOS = ["codigo", "titulo", "universidad", "nivel", "estado", "url_ruct"]


def _quitar_acentos(texto: str) -> str:
    """
    Elimina los diacríticos (acentos) de un texto.
    Ej: 'Matemáticas' → 'Matematicas', 'Ingeniería' → 'Ingenieria'
    El RUCT devuelve 0 resultados cuando la búsqueda contiene caracteres acentuados,
    pero es insensible a acentos cuando recibe texto ASCII plano.
    """
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def cargar_opciones_formulario(timeout: int = 20) -> dict:
    """
    Descarga el formulario del RUCT y extrae todas las opciones de los desplegables.
    Devuelve un dict con listas de (texto, valor) para cada campo.
    Si hay error de conexión, devuelve los valores predefinidos (sin universidades individuales).
    """
    try:
        r = requests.get(FORM_URL, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        def _opciones(name):
            sel = soup.find("select", {"name": name})
            if not sel:
                return []
            return [(o.text.strip(), o.get("value", "")) for o in sel.find_all("option")]

        return {
            "universidades": _opciones("codigoUniversidad"),
            "tipos": _opciones("codigoTipo"),
            "ramas": _opciones("codigoRama"),
            "ambitos": _opciones("ambito"),
            "estados": _opciones("codigoEstado"),
            "situaciones": _opciones("situacion"),
        }

    except Exception as e:
        logger.warning(f"No se pudieron cargar las opciones del formulario: {e}")
        # Devolver valores por defecto conocidos
        return {
            "universidades": [("Todas", "")] ,
            "tipos": list(TIPOS_ESTUDIO.items()),
            "ramas": [(v, k) for k, v in RAMAS_CONOCIMIENTO.items()],
            "ambitos": [("Todos", "")],
            "estados": list(ESTADOS.items()),
            "situaciones": list(SITUACIONES.items()),
        }


def buscar_ruct(
    descripcion: str = "",
    codigo: str = "",
    universidad: str = "",
    tipo: str = "G",
    rama: str = "",
    ambito: str = "",
    estado: str = "P",
    situacion: str = "A",
    historico: str = "N",
    timeout: int = 30,
    max_paginas: int = 200,
    progress_callback=None,
) -> tuple[pd.DataFrame, str | None]:
    """
    Busca titulaciones en el RUCT con los parámetros indicados.

    Parámetros
    ----------
    descripcion    Texto libre en el nombre del título
    codigo         Código numérico del estudio (opcional)
    universidad    Código de universidad ('' = todas)
    tipo           Tipo de estudio: 'G'=Grado, 'M'=Máster, 'D'=Doctor, ''=Todos
    rama           Código de rama: '431001'...'431004', ''=Todas
    ambito         Código de ámbito de estudio ('' = todos)
    estado         'P'=Publicado BOE, 'ACA'=Autorizado CA, ''=Todos
    situacion      'A'=Alta (activa), 'T'=Extinguida, 'X'=A extinguir, ''=Todas
    historico      'N'=No buscar histórico (default), 'S'=Incluir histórico
    timeout        Segundos de espera máxima por petición HTTP
    max_paginas    Número máximo de páginas a scrappear
    progress_callback  Función(pagina_actual: int, total_filas: int) para reportar progreso

    Devuelve
    --------
    (DataFrame, warning_str_or_None)
    El DataFrame tiene columnas: codigo, titulo, universidad, nivel, estado, url_ruct
    Si hay error o aviso, se devuelve un string descriptivo como segundo elemento.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    # Inicializar sesión (obtener JSESSIONID y cookies)
    try:
        session.get(FORM_URL, timeout=timeout)
    except requests.RequestException as e:
        df_vacio = pd.DataFrame(
            columns=COLUMNS_RESULTADOS
        )
        return df_vacio, f"No se pudo conectar al RUCT: {e}"

    payload = {
        "consulta": "1",
        "codigoEstudio": codigo.strip(),
        "descripcionEstudio": _quitar_acentos(descripcion.strip()),
        "codigoUniversidad": universidad,
        "codigoTipo": tipo,
        "codigoSubTipo": "",
        "codigoRama": rama,
        "ambito": ambito,
        "codigoEstado": estado,
        "situacion": situacion,
        "buscarHistorico": historico,
        "action:listaestudios": "Consultar",
    }

    resultados = []
    warning = None

    try:
        # Página 1 — POST
        r = session.post(
            FORM_URL,
            data=payload,
            params={"actual": "estudios"},
            timeout=timeout,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        filas = _parsear_tabla(soup)
        resultados.extend(filas)

        # Detectar si el RUCT no procesó la búsqueda (respuesta inesperada)
        if not filas:
            texto = soup.get_text()
            tiene_marcador = (
                "Ningún registro encontrado" in texto
                or "Ningun registro encontrado" in texto
                or "registros encontrados" in texto
            )
            if not tiene_marcador:
                return (
                    pd.DataFrame(columns=COLUMNS_RESULTADOS),
                    "El RUCT no ha podido procesar la búsqueda. "
                    "Es posible que el servidor esté temporalmente no disponible "
                    "o que la aplicación no tenga acceso desde este servidor. "
                    "Por favor, inténtalo de nuevo en unos minutos.",
                )

        if progress_callback:
            progress_callback(1, len(resultados))

        # Páginas 2..N — GET siguiendo el enlace "Siguiente"
        for pagina in range(2, max_paginas + 1):
            url_sig = _link_siguiente(soup)
            if not url_sig:
                break  # No hay más páginas

            time.sleep(0.4)  # Ser amable con el servidor

            r = session.get(url_sig, timeout=timeout)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")

            filas = _parsear_tabla(soup)
            if not filas:
                break

            resultados.extend(filas)

            if progress_callback:
                progress_callback(pagina, len(resultados))

        else:
            # Se llegó al límite de páginas sin agotar resultados
            warning = (
                f"Se alcanzó el límite de {max_paginas} páginas. "
                "Puede haber más resultados — reduce los filtros o aumenta el límite."
            )

    except requests.Timeout:
        warning = (
            "Tiempo de espera agotado. "
            f"Se muestran los {len(resultados)} resultados obtenidos hasta ahora."
        )
    except requests.ConnectionError as e:
        warning = f"Error de conexión con el RUCT: {e}"
    except requests.HTTPError as e:
        warning = f"El servidor del RUCT devolvió un error: {e}"

    df = (
        pd.DataFrame(resultados)
        if resultados
        else pd.DataFrame(
            columns=COLUMNS_RESULTADOS
        )
    )
    return df, warning


# ─── Funciones auxiliares internas ───────────────────────────────────────────

def _parsear_tabla(soup: BeautifulSoup) -> list[dict]:
    """Extrae todas las filas de datos de la tabla de resultados del RUCT."""
    table = soup.find("table")
    if not table:
        return []

    filas = []
    for tr in table.find_all("tr")[1:]:  # Saltar cabecera
        celdas = tr.find_all("td")
        if len(celdas) < 5:
            continue

        # El título puede tener un enlace al detalle
        link_tag = celdas[1].find("a")
        url_ruct = ""
        if link_tag and link_tag.get("href"):
            href = link_tag["href"]
            url_ruct = (
                href
                if href.startswith("http")
                else f"https://www.educacion.gob.es{href}"
            )

        filas.append(
            {
                "codigo": celdas[0].text.strip(),
                "titulo": celdas[1].text.strip(),
                "universidad": celdas[2].text.strip(),
                "nivel": celdas[3].text.strip(),
                "estado": celdas[4].text.strip(),
                "url_ruct": url_ruct,
            }
        )
    return filas


def _link_siguiente(soup: BeautifulSoup) -> str | None:
    """
    Devuelve la URL absoluta de la página siguiente en la paginación del RUCT,
    o None si no existe el enlace 'Siguiente'.
    """
    for a in soup.find_all("a"):
        texto = a.text.strip().lower()
        if texto in ("siguiente", "next", "►", ">"):
            href = a.get("href", "")
            if not href:
                continue
            if href.startswith("http"):
                return href
            # href relativo — puede ser "listaestudios?..." o "../listaestudios?..."
            if href.startswith("/"):
                return f"https://www.educacion.gob.es{href}"
            return f"{BASE_URL}/{href}"
    return None


# ─── Exportación ─────────────────────────────────────────────────────────────

def exportar_csv(df: pd.DataFrame) -> bytes:
    """
    Devuelve el DataFrame como bytes CSV con BOM UTF-8
    (compatible con Excel en Windows sin configuración adicional).
    """
    return df.to_csv(index=False).encode("utf-8-sig")


def exportar_excel(df: pd.DataFrame) -> bytes:
    """
    Devuelve el DataFrame como bytes de un fichero Excel (.xlsx).
    Requiere openpyxl instalado.
    """
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados RUCT")
        # Auto-ajustar anchos de columna
        ws = writer.sheets["Resultados RUCT"]
        for col_cells in ws.columns:
            max_len = max(
                (len(str(cell.value)) if cell.value else 0 for cell in col_cells),
                default=10,
            )
            ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 2, 60)
    return buf.getvalue()


# ─── Ejecución directa (test) ─────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    print("Cargando opciones del formulario...")
    opciones = cargar_opciones_formulario()
    print(f"  Universidades: {len(opciones['universidades'])}")
    print(f"  Ramas: {opciones['ramas']}")

    print("\nBuscando 'Medicina' (Grado, activo)...")
    df, warn = buscar_ruct(
        descripcion="Medicina",
        tipo="G",
        estado="P",
        situacion="A",
        max_paginas=5,
        progress_callback=lambda p, n: print(f"  Página {p} — {n} resultados"),
    )
    print(f"\nResultados: {len(df)}")
    if warn:
        print(f"Aviso: {warn}")
    if not df.empty:
        print(df[["codigo", "titulo", "universidad"]].head(5).to_string(index=False))

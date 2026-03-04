"""
ruct_scraper.py
Scrapes the RUCT (Registro de Universidades, Centros y Títulos),
Spain's official Ministry of Education registry of university degrees.
https://www.educacion.gob.es/ruct/
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

# Known value mappings — used as fallback when the RUCT form cannot be fetched
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

RESULT_COLUMNS = ["codigo", "titulo", "universidad", "nivel", "estado", "url_ruct"]


def _strip_accents(text: str) -> str:
    """
    Remove diacritics (accents) from a string.
    Example: 'Matemáticas' -> 'Matematicas', 'Ingeniería' -> 'Ingenieria'.

    The RUCT returns 0 results when the query contains accented characters,
    but performs accent-insensitive matching when given plain ASCII input.
    """
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def load_form_options(timeout: int = 20) -> dict:
    """
    Fetch the RUCT search form and extract all dropdown options.
    Returns a dict of lists of (label, value) tuples for each field.
    Falls back to hardcoded defaults if the connection fails.
    """
    try:
        r = requests.get(FORM_URL, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        def _options(name):
            sel = soup.find("select", {"name": name})
            if not sel:
                return []
            return [(o.text.strip(), o.get("value", "")) for o in sel.find_all("option")]

        return {
            "universidades": _options("codigoUniversidad"),
            "tipos": _options("codigoTipo"),
            "ramas": _options("codigoRama"),
            "ambitos": _options("ambito"),
            "estados": _options("codigoEstado"),
            "situaciones": _options("situacion"),
        }

    except Exception as e:
        logger.warning(f"Failed to load form options: {e}")
        # Return known hardcoded defaults
        return {
            "universidades": [("Todas", "")],
            "tipos": list(TIPOS_ESTUDIO.items()),
            "ramas": [(v, k) for k, v in RAMAS_CONOCIMIENTO.items()],
            "ambitos": [("Todos", "")],
            "estados": list(ESTADOS.items()),
            "situaciones": list(SITUACIONES.items()),
        }


def search_ruct(
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
    Search for university degrees in the RUCT.

    Parameters
    ----------
    descripcion    Free-text search on the degree name
    codigo         Numeric degree code (optional)
    universidad    University code ('' = all)
    tipo           Degree type: 'G'=Grado, 'M'=Máster, 'D'=Doctor, ''=all
    rama           Branch code: '431001'..'431005', ''=all
    ambito         Field-of-study code ('' = all)
    estado         'P'=Published in BOE, 'ACA'=Authorised by region, ''=all
    situacion      'A'=Active, 'T'=Extinct, 'X'=Being phased out, ''=all
    historico      'N'=Current only (default), 'S'=Include historical records
    timeout        Max seconds to wait per HTTP request
    max_paginas    Maximum number of result pages to scrape
    progress_callback  Optional callable(page: int, total_rows: int)

    Returns
    -------
    (DataFrame, warning_or_None)
    DataFrame columns: codigo, titulo, universidad, nivel, estado, url_ruct
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    # Initialize session to obtain cookies
    try:
        session.get(FORM_URL, timeout=timeout)
    except requests.RequestException as e:
        return pd.DataFrame(columns=RESULT_COLUMNS), f"No se pudo conectar al RUCT: {e}"

    payload = {
        "consulta": "1",
        "codigoEstudio": codigo.strip(),
        "descripcionEstudio": _strip_accents(descripcion.strip()),
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

    results = []
    warning = None

    try:
        # Page 1 — POST
        r = session.post(
            FORM_URL,
            data=payload,
            params={"actual": "estudios"},
            timeout=timeout,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        rows = _parse_table(soup)
        results.extend(rows)

        # Detect if RUCT did not process the search (unexpected response)
        if not rows:
            page_text = soup.get_text()
            has_marker = (
                "Ningún registro encontrado" in page_text
                or "Ningun registro encontrado" in page_text
                or "registros encontrados" in page_text
            )
            if not has_marker:
                return (
                    pd.DataFrame(columns=RESULT_COLUMNS),
                    "El RUCT no ha podido procesar la búsqueda. "
                    "Es posible que el servidor esté temporalmente no disponible "
                    "o que la aplicación no tenga acceso desde este servidor. "
                    "Por favor, inténtalo de nuevo en unos minutos.",
                )

        if progress_callback:
            progress_callback(1, len(results))

        # Pages 2..N — GET following the "Siguiente" (Next) link
        for page_num in range(2, max_paginas + 1):
            next_url = _next_page_url(soup)
            if not next_url:
                break  # No more pages

            time.sleep(0.4)  # Be polite to the server

            r = session.get(next_url, timeout=timeout)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")

            rows = _parse_table(soup)
            if not rows:
                break

            results.extend(rows)

            if progress_callback:
                progress_callback(page_num, len(results))

        else:
            # Page limit reached without exhausting all results
            warning = (
                f"Se alcanzó el límite de {max_paginas} páginas. "
                "Puede haber más resultados — reduce los filtros o aumenta el límite."
            )

    except requests.Timeout:
        warning = (
            "Tiempo de espera agotado. "
            f"Se muestran los {len(results)} resultados obtenidos hasta ahora."
        )
    except requests.ConnectionError as e:
        warning = f"Error de conexión con el RUCT: {e}"
    except requests.HTTPError as e:
        warning = f"El servidor del RUCT devolvió un error: {e}"

    df = (
        pd.DataFrame(results)
        if results
        else pd.DataFrame(columns=RESULT_COLUMNS)
    )
    return df, warning


# ─── Internal helpers ────────────────────────────────────────────────────────

def _parse_table(soup: BeautifulSoup) -> list[dict]:
    """Extract all data rows from the RUCT results table."""
    table = soup.find("table")
    if not table:
        return []

    rows = []
    for tr in table.find_all("tr")[1:]:  # Skip header row
        cells = tr.find_all("td")
        if len(cells) < 5:
            continue

        # The title cell may contain a link to the degree detail page
        link_tag = cells[1].find("a")
        url_ruct = ""
        if link_tag and link_tag.get("href"):
            href = link_tag["href"]
            url_ruct = (
                href
                if href.startswith("http")
                else f"https://www.educacion.gob.es{href}"
            )

        rows.append({
            "codigo": cells[0].text.strip(),
            "titulo": cells[1].text.strip(),
            "universidad": cells[2].text.strip(),
            "nivel": cells[3].text.strip(),
            "estado": cells[4].text.strip(),
            "url_ruct": url_ruct,
        })
    return rows


def _next_page_url(soup: BeautifulSoup) -> str | None:
    """
    Return the absolute URL of the next results page,
    or None if there is no 'Siguiente' (Next) link.
    """
    for a in soup.find_all("a"):
        text = a.text.strip().lower()
        if text in ("siguiente", "next", "►", ">"):
            href = a.get("href", "")
            if not href:
                continue
            if href.startswith("http"):
                return href
            if href.startswith("/"):
                return f"https://www.educacion.gob.es{href}"
            return f"{BASE_URL}/{href}"
    return None


# ─── Export ──────────────────────────────────────────────────────────────────

def export_csv(df: pd.DataFrame) -> bytes:
    """
    Return the DataFrame as UTF-8 BOM CSV bytes.
    The BOM ensures Excel on Windows opens the file without encoding issues.
    """
    return df.to_csv(index=False).encode("utf-8-sig")


def export_excel(df: pd.DataFrame) -> bytes:
    """
    Return the DataFrame as an Excel (.xlsx) file in bytes.
    Requires openpyxl to be installed.
    """
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados RUCT")
        # Auto-adjust column widths
        ws = writer.sheets["Resultados RUCT"]
        for col_cells in ws.columns:
            max_len = max(
                (len(str(cell.value)) if cell.value else 0 for cell in col_cells),
                default=10,
            )
            ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 2, 60)
    return buf.getvalue()


# ─── Direct execution (test) ─────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    print("Loading form options...")
    options = load_form_options()
    print(f"  Universities: {len(options['universidades'])}")
    print(f"  Branches: {options['ramas']}")

    print("\nSearching for 'Medicina' (Grado, active)...")
    df, warn = search_ruct(
        descripcion="Medicina",
        tipo="G",
        estado="P",
        situacion="A",
        max_paginas=5,
        progress_callback=lambda p, n: print(f"  Page {p} — {n} results"),
    )
    print(f"\nResults: {len(df)}")
    if warn:
        print(f"Warning: {warn}")
    if not df.empty:
        print(df[["codigo", "titulo", "universidad"]].head(5).to_string(index=False))

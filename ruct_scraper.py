"""
ruct_scraper.py
Scrapes the RUCT (Registro de Universidades, Centros y Títulos),
Spain's official Ministry of Education registry of university degrees.
https://www.educacion.gob.es/ruct/
"""

import io
import re
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
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
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

RESULT_COLUMNS = ["codigo", "titulo", "universidad", "nivel", "estado", "url_ruct", "url_plan"]


_INVISIBLE_CHARS = re.compile(
    r"[\u200b\u200c\u200d\u200e\u200f\u00ad\ufeff\u2060\u180e]"
)

# Windows-1252 bytes 0x80-0x9F that sometimes leak into scraped UTF-8 text
_CP1252_FIX = str.maketrans({
    "\x80": "\u20ac", "\x82": "\u201a", "\x83": "\u0192", "\x84": "\u201e",
    "\x85": "\u2026", "\x86": "\u2020", "\x87": "\u2021", "\x88": "\u02c6",
    "\x89": "\u2030", "\x8a": "\u0160", "\x8b": "\u2039", "\x8c": "\u0152",
    "\x8e": "\u017d", "\x91": "\u2018", "\x92": "\u2019", "\x93": "\u201c",
    "\x94": "\u201d", "\x95": "\u2022", "\x96": "\u2013", "\x97": "\u2014",
    "\x98": "\u02dc", "\x99": "\u2122", "\x9a": "\u0161", "\x9b": "\u203a",
    "\x9c": "\u0153", "\x9e": "\u017e", "\x9f": "\u0178",
})

def _clean_text(text: str) -> str:
    """Fix Windows-1252 encoding artifacts and remove invisible Unicode characters."""
    return _INVISIBLE_CHARS.sub("", text.translate(_CP1252_FIX)).replace("\xa0", " ").strip()


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

    # Initialize session and capture the form action URL (contains jsessionid)
    try:
        init_r = session.get(FORM_URL, timeout=timeout)
        init_soup = BeautifulSoup(init_r.text, "lxml")
        form = init_soup.find("form")
        if form and form.get("action"):
            action = form["action"]
            post_url = (
                action if action.startswith("http")
                else f"https://www.educacion.gob.es{action}"
            )
        else:
            post_url = f"{FORM_URL}?actual=estudios"
    except requests.RequestException as e:
        return pd.DataFrame(columns=RESULT_COLUMNS), f"No se pudo conectar al RUCT: {e}"

    # Extract all hidden input fields from the form (tokens, session fields, etc.)
    hidden_fields = {}
    if form:
        for inp in form.find_all("input", {"type": "hidden"}):
            name = inp.get("name")
            value = inp.get("value", "")
            if name:
                hidden_fields[name] = value

    # Find the submit button name/value dynamically
    submit_name = "action:listaestudios"
    submit_value = "Consultar"
    if form:
        for inp in form.find_all("input", {"type": "submit"}):
            name = inp.get("name")
            value = inp.get("value", "Consultar")
            if name:
                submit_name = name
                submit_value = value
                break

    # Build payload: start with hidden fields, then override with our search params
    payload = {
        **hidden_fields,
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
        submit_name: submit_value,
    }

    results = []
    warning = None

    try:
        # Page 1 — POST to the form action URL (includes jsessionid for server-side session)
        session.headers["Referer"] = FORM_URL
        session.headers["Content-Type"] = "application/x-www-form-urlencoded"
        time.sleep(0.3)
        r = session.post(
            post_url,
            data=payload,
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
            # Detect server-side validation error: requires at least one filter
            if "Por favor, introduzca" in page_text and "Denominaci" in page_text:
                return (
                    pd.DataFrame(columns=RESULT_COLUMNS),
                    "El RUCT requiere al menos un criterio de búsqueda: "
                    "escribe una denominación, introduce un código de título, "
                    "o selecciona una universidad concreta.",
                )
            if not has_marker:
                snippet = " ".join(page_text.split())[:200]
                return (
                    pd.DataFrame(columns=RESULT_COLUMNS),
                    f"El RUCT no ha podido procesar la búsqueda (HTTP {r.status_code}). "
                    "Es posible que el servidor esté temporalmente no disponible "
                    "o que la aplicación no tenga acceso desde este servidor. "
                    f"Respuesta recibida: {snippet}",
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

        # Cell 1: title link → RUCT degree detail page
        link_tag = cells[1].find("a")
        url_ruct = ""
        if link_tag and link_tag.get("href"):
            href = link_tag["href"]
            url_ruct = (
                href
                if href.startswith("http")
                else f"https://www.educacion.gob.es{href}"
            )

        # Cell 5: lupa (magnifying-glass) icon → plan details page (Memoria de verificación)
        url_plan = ""
        if len(cells) > 5:
            plan_link = cells[5].find("a")
            if plan_link and plan_link.get("href"):
                href = plan_link["href"]
                url_plan = (
                    href
                    if href.startswith("http")
                    else f"https://www.educacion.gob.es{href}"
                )

        rows.append({
            "codigo": _clean_text(cells[0].text),
            "titulo": _clean_text(cells[1].text),
            "universidad": _clean_text(cells[2].text),
            "nivel": _clean_text(cells[3].text),
            "estado": _clean_text(cells[4].text),
            "url_ruct": url_ruct,
            "url_plan": url_plan,
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

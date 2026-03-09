import streamlit as st
import pandas as pd
import logging
import re
import requests
from bs4 import BeautifulSoup
import ruct_scraper

logging.basicConfig(level=logging.WARNING)

# ─── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Buscador de Carreras Universitarias Oficiales en España",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ── Force light mode ── */
    html { color-scheme: light only !important; }
    :root {
        color-scheme: light only;
        --c-bg:       #FFFFFF;
        --c-surface:  #F8F9FA;
        --c-border:   #E8EAED;
        --c-navy:     #1B3A6B;
        --c-navy-lt:  #EBF0F8;
        --c-navy-dk:  #122954;
        --c-text:     #111827;
        --c-muted:    #6B7280;
        --c-faint:    #9CA3AF;
        --c-warn-bg:  #FFFBEB;
        --c-warn-bd:  #F59E0B;
        --c-warn-tx:  #92400E;
        --radius:     0.625rem;
    }

    @media (prefers-color-scheme: dark) {
        html, body, .stApp, [data-testid="stAppViewContainer"],
        [data-testid="stHeader"], [data-testid="stSidebar"],
        .main, .main .block-container {
            background-color: #FFFFFF !important;
            color: #111827 !important;
        }
    }

    body, p, h1, h2, h3, h4, h5, h6, div, label, button,
    input, select, textarea, li, a, td, th {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer { visibility: hidden; }
    [data-testid="stToolbar"] { background: transparent !important; box-shadow: none !important; }
    [data-testid="stToolbar"] .stAppToolbarActions,
    [data-testid="stToolbar"] [data-testid="stDecoration"] { display: none !important; }
    [data-testid="InputInstructions"] { display: none !important; }

    /* ── App shell ── */
    .stApp { background: var(--c-bg) !important; color: var(--c-text) !important; color-scheme: light only !important; }
    .main .block-container {
        padding: 0 1rem 3rem 1rem;
        max-width: 820px;
        background: var(--c-bg) !important;
        color: var(--c-text) !important;
    }

    /* ── Header ── */
    .header-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 1.75rem 0 1.25rem;
        border-bottom: 1px solid var(--c-border);
        margin-bottom: 2rem;
        gap: 0.6rem;
    }
    .header-logo {
        height: 80px;
        width: auto;
        opacity: 0.92;
    }
    .header-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--c-text) !important;
        margin: 0;
        letter-spacing: -0.01em;
        line-height: 1.3;
    }
    .header-sub {
        font-size: 0.80rem;
        color: var(--c-muted) !important;
        margin: 0;
        letter-spacing: 0.01em;
    }
    @media (max-width: 520px) {
        .header-logo { height: 60px; }
        .header-title { font-size: 0.95rem; }
        .main .block-container { padding: 0 0.75rem 2rem; }
    }

    /* ── Search form ── */
    [data-testid="stForm"] {
        background: var(--c-surface) !important;
        border: 1px solid var(--c-border) !important;
        border-radius: var(--radius) !important;
        padding: 1.25rem 1.25rem 1rem !important;
        margin-bottom: 1.75rem !important;
    }
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        border-color: var(--c-border) !important;
        border-radius: var(--radius) !important;
        background: var(--c-bg) !important;
        min-height: 42px;
    }
    .stTextInput > div > div > input {
        border-color: var(--c-border) !important;
        border-radius: var(--radius) !important;
        background: var(--c-bg) !important;
        min-height: 42px;
    }
    .form-hint {
        font-size: 0.73rem;
        color: var(--c-faint);
        margin-top: 0.4rem;
        margin-bottom: 0;
    }

    /* ── Search button ── */
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button {
        background: var(--c-navy) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        min-height: 46px !important;
        border-radius: var(--radius) !important;
        box-shadow: 0 2px 8px rgba(27,58,107,0.25) !important;
        transition: background 0.18s ease, box-shadow 0.18s ease !important;
        width: 100%;
    }
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button:hover {
        background: var(--c-navy-dk) !important;
        box-shadow: 0 4px 14px rgba(27,58,107,0.35) !important;
    }

    /* ── Metrics ── */
    div[data-testid="metric-container"] {
        background: var(--c-bg) !important;
        padding: 0.875rem 1rem;
        border-radius: var(--radius);
        border: 1px solid var(--c-border) !important;
        color: var(--c-text) !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700;
        color: var(--c-navy);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.68rem !important;
        font-weight: 600;
        color: var(--c-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* ── Results list ── */
    .result-title {
        font-size: 0.92rem;
        font-weight: 500;
        color: var(--c-text);
        line-height: 1.45;
    }
    .result-univ {
        font-size: 0.76rem;
        color: var(--c-muted);
        margin-top: 0.1rem;
    }

    /* ── Link buttons ── */
    [data-testid="stLinkButton"] > a {
        border-radius: var(--radius) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }

    /* ── Boxes ── */
    .warn-box {
        background: var(--c-warn-bg);
        border: 1px solid #FCD34D;
        border-left: 3px solid var(--c-warn-bd);
        border-radius: var(--radius);
        padding: 0.75rem 1rem;
        font-size: 0.85rem;
        color: var(--c-warn-tx);
        margin-bottom: 1rem;
    }
    .info-box {
        background: var(--c-navy-lt);
        border: 1px solid #B8C8E0;
        border-left: 3px solid var(--c-navy);
        border-radius: var(--radius);
        padding: 0.75rem 1rem;
        font-size: 0.85rem;
        color: var(--c-navy);
        margin-bottom: 1rem;
    }

    hr { margin: 1.25rem 0; border: none; height: 1px; background: var(--c-border); }
    a { color: var(--c-navy); text-decoration: none; font-weight: 500; }
    a:hover { color: var(--c-navy-dk); }
</style>
""", unsafe_allow_html=True)


# ─── Load options (cached for 1 hour) ────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Conectando con el RUCT...")
def _load_options():
    return ruct_scraper.load_form_options(timeout=20)


def _prepare_options(items: list) -> tuple:
    """Convert a list of (label, value) tuples into a display list and value dict."""
    display = [label for label, _ in items]
    values = {label: val for label, val in items}
    return display, values


# ─── Study plan scraper ───────────────────────────────────────────────────────
_WEB_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

_RUCT_INIT_URL = "https://www.educacion.gob.es/ruct/consultaestudios.action"
_RUCT_MODULES_URL = (
    "https://www.educacion.gob.es/ruct/solicitud/datosModulo"
    "?actual=menu.solicitud.planificacion.materiasSin&codModulo=0"
)


def _boe_pdf_to_html(pdf_url: str) -> str:
    """Convert a BOE PDF URL to its HTML equivalent (txt.php).
    e.g. .../pdfs/BOE-A-2013-7517.pdf -> https://www.boe.es/diario_boe/txt.php?id=BOE-A-2013-7517
    """
    m = re.search(r"(BOE-[A-Z]-\d{4}-\d+)\.pdf", pdf_url)
    return f"https://www.boe.es/diario_boe/txt.php?id={m.group(1)}" if m else ""


def _fetch_ruct_ficha(url_ruct: str, url_plan: str) -> dict:
    """
    Fetch full degree metadata from RUCT and the BOE study plan URL.

    Session flow:
      1. GET consultaestudios.action    — init session
      2. GET url_plan (detalles.action) — datos basicos: denominacion, profesion regulada,
                                         norma, menciones/especialidades
      3. GET url_ruct (estudio.action)  — nivel, MECES, rama, campo, centro, CCAA, BOE URL

    Returns a dict with all available fields (empty string/list when not found).
    """
    ficha = {
        "denominacion": "", "universidad": "", "centro": "", "ccaa": "",
        "nivel": "", "meces": "", "rama": "", "campo": "",
        "habilita": "", "profesion_regulada": "", "acuerdo": "", "norma": "",
        "menciones": [], "especialidades": [], "boe_plan_url": "",
    }
    if not url_ruct or not url_plan:
        return ficha
    try:
        session = requests.Session()
        session.headers.update(_WEB_HEADERS)
        session.get(_RUCT_INIT_URL, timeout=15)

        # Step 2: detalles.action — datos basicos
        r_det = session.get(url_plan, timeout=15)
        if r_det.status_code < 400:
            soup_det = BeautifulSoup(r_det.text, "lxml")

            def _inp(name):
                el = soup_det.find("input", {"name": name})
                return el["value"].strip() if el and el.get("value") else ""

            ficha["denominacion"] = _inp("denominacion")
            ficha["habilita"] = _inp("habilita")
            ficha["profesion_regulada"] = _inp("codigoProfesionRegulada")

            for for_val, key in [("acuerdo", "acuerdo"), ("norma", "norma")]:
                lbl = soup_det.find("label", {"for": for_val})
                if lbl:
                    a = lbl.find("a")
                    if a:
                        ficha[key] = a.get_text(strip=True)

            for fs in soup_det.find_all("fieldset"):
                leg = fs.find("legend")
                if not leg:
                    continue
                leg_text = leg.get_text(strip=True).lower()
                tbl = fs.find("table")
                if not tbl:
                    continue
                items = []
                for tr in tbl.find_all("tr")[1:]:
                    cells = tr.find_all("td")
                    if len(cells) >= 2:
                        nombre = cells[1].get_text(strip=True)
                        cred = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                        if nombre:
                            items.append({"nombre": nombre, "creditos": cred})
                if "menci" in leg_text:
                    ficha["menciones"] = items
                elif "especialidad" in leg_text:
                    ficha["especialidades"] = items

        # Step 3: estudio.action — nivel, MECES, rama, campo, centro, CCAA, BOE URL
        r_est = session.get(url_ruct, timeout=15)
        r_est.raise_for_status()
        soup_est = BeautifulSoup(r_est.text, "lxml")

        def _sid(span_id):
            el = soup_est.find(id=span_id)
            return el.get_text(strip=True) if el else ""

        nivel_raw = _sid("estudio_descripcionTipo")
        meces = _sid("estudio_nivelMeces")
        nivel_clean = nivel_raw.split(" - ")[0].strip() if " - " in nivel_raw else nivel_raw
        ficha["nivel"] = nivel_clean
        ficha["meces"] = meces
        ficha["rama"] = _sid("estudio_descripcionRama")
        ficha["campo"] = _sid("estudio_descripcionAmbito")

        tthree = soup_est.find("div", id="tthree")
        if tthree:
            tbl = tthree.find("table", id="centro")
            if tbl:
                rows = tbl.find_all("tr")[1:]
                if rows:
                    cells = rows[0].find_all("td")
                    if len(cells) >= 3:
                        ficha["universidad"] = cells[0].get_text(strip=True)
                        ficha["centro"] = cells[2].get_text(strip=True)

        ttwo = soup_est.find("div", id="ttwo")
        if ttwo:
            ccaa_tbl = ttwo.find("table", id="ccaa")
            if ccaa_tbl:
                rows = ccaa_tbl.find_all("tr")[1:]
                if rows:
                    cells = rows[0].find_all("td")
                    if len(cells) >= 3:
                        ficha["ccaa"] = cells[2].get_text(strip=True)
            plan_label = ttwo.find("label", {"for": "f_plan"})
            if plan_label:
                a = plan_label.find("a", href=True)
                if a:
                    ficha["boe_plan_url"] = _boe_pdf_to_html(a["href"])
            if not ficha["boe_plan_url"]:
                for label in ttwo.find_all("label"):
                    if "Plan Estudios" in label.get_text():
                        a = label.find("a", href=True)
                        if a and "boe.es" in a["href"] and ".pdf" in a["href"]:
                            ficha["boe_plan_url"] = _boe_pdf_to_html(a["href"])
                            break
    except Exception:
        pass
    return ficha


def _html_table_to_md(table) -> str:
    """Convert a BS4 table tag to a Markdown table string."""
    rows = []
    for i, tr in enumerate(table.find_all("tr")):
        cells = [td.get_text(separator=" ", strip=True) for td in tr.find_all(["th", "td"])]
        if not cells:
            continue
        rows.append("| " + " | ".join(cells) + " |")
        if i == 0:
            rows.append("|" + "|".join([" --- "] * len(cells)) + "|")
    return "\n".join(rows)


def _fetch_boe_plan(url: str) -> str:
    """
    Fetch a BOE txt.php page and extract the study plan content from div#textoxslt.
    Tables are converted to Markdown. For text-only documents, extracts plain text.
    """
    try:
        r = requests.get(url, headers=_WEB_HEADERS, timeout=15)
        if r.status_code >= 400:
            return ""
        soup = BeautifulSoup(r.text, "lxml")
        content = soup.find(id="textoxslt")
        if not content:
            return ""
        for el in content(["script", "style", "a"]):
            el.decompose()

        parts = []
        past_first_table = False

        for el in content.find_all(["table", "p", "h2", "h3", "h4"]):
            if el.find_parent("table"):
                continue
            if el.name == "table":
                past_first_table = True
                md = _html_table_to_md(el)
                if md:
                    parts.append(md)
            elif past_first_table:
                text = el.get_text(strip=True)
                if text:
                    parts.append(text)

        # If no tables found, fall back to full text (skip first paragraph = legal preamble)
        if not parts:
            paragraphs = [
                el.get_text(strip=True)
                for el in content.find_all(["p", "h2", "h3", "h4"])
                if not el.find_parent("table") and el.get_text(strip=True)
            ]
            if len(paragraphs) > 2:
                parts = paragraphs[2:]   # skip opening legal text

        return "\n\n".join(parts)[:14000]
    except Exception:
        return ""


def _fetch_ruct_modules(url_plan: str) -> str:
    """
    Fallback: fetch the 'Módulos o Materias' static page from RUCT.

    Session flow:
      1. GET consultaestudios.action  — init session
      2. GET url_plan (lupa link)     — register degree in server session
      3. GET datosModulo              — returns static HTML with module list

    Returns a markdown-formatted list of modules, or "" on failure.
    """
    if not url_plan:
        return ""
    try:
        session = requests.Session()
        session.headers.update(_WEB_HEADERS)
        session.get(_RUCT_INIT_URL, timeout=15)
        session.get(url_plan, timeout=15)
        r = session.get(_RUCT_MODULES_URL, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table")
        if not table:
            return ""
        items = []
        for tr in table.find_all("tr")[1:]:  # Skip header row
            cells = tr.find_all("td")
            if len(cells) >= 2:
                name = cells[1].get_text(strip=True)
                if name:
                    items.append(f"- {name}")
        if not items:
            return ""
        return "**Módulos y materias**\n\n" + "\n".join(items)
    except Exception:
        return ""


def _find_study_plan(title: str, university: str, url_ruct: str = "", url_plan: str = "") -> dict:
    """
    Fetch the RUCT degree ficha (metadata) and locate the study plan.

    Returns {"ficha": dict, "page_text": str, "source_url": str}
    """
    ficha = _fetch_ruct_ficha(url_ruct, url_plan)
    boe_url = ficha.get("boe_plan_url", "")
    if boe_url:
        plan_text = _fetch_boe_plan(boe_url)
        if plan_text:
            return {"ficha": ficha, "page_text": plan_text, "source_url": boe_url}
        # BOE URL found but extraction failed — still expose the URL so user can open it
        modules_text = _fetch_ruct_modules(url_plan) if url_plan else ""
        return {
            "ficha": ficha,
            "page_text": modules_text,
            "source_url": boe_url,          # always show BOE button
        }

    # No BOE URL — try RUCT modules page as sole source
    modules_text = _fetch_ruct_modules(url_plan) if url_plan else ""
    return {"ficha": ficha, "page_text": modules_text, "source_url": ""}


# ─── Header ───────────────────────────────────────────────────────────────────
_LOGO_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAVpA4QDAREAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD9U6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAMDxj4y8MeAPDeoeL/ABlrVrpWj6XC093d3MmyOJB/U9AO9AH5t/GT/gr7rEWsS6b8Bfh/pv8AZ0Dso1bxIskkl0o7pbxOnlL6bnb/AHVq+UDz7RP+Cuv7SFnqMU2t+F/AupWO799bpZXFvIy/7EgnO1v+AtRyl8p+jH7MP7U3w+/ah8Ft4m8JPJY6nYusGr6NcyK1xYSkccj/AFkbYJST+Idlb5agg9soAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA/Hf/gpr+1a/xW+IH/CmvBWqFvCXg+4Zb6SF/wB3qWqLwx/2kh+4P9re392qRSPh+mMKAPR/2fvjv40/Z2+JWn/EjwVPvkg/c31jK+2G/tS37yCT69m/hb5qAP3j+Dfxi8F/HT4eaV8SfAt/5+m6muHiYfvbWcf6yCVf4XQ/4/dqCDvqACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD5H/AOCh37VX/DPvwtfwt4W1Aw+N/GEUltp7xt+8sLXpNd+zfwR/7R3fwGgD8UXdnbe/3qssbQAUAFAH0Z+xV+1rrf7L/wAQxNfy3F34J16RIde09Pm2dhdRD/nqn/jy/L/d2oR+5HhvxDoni7QrDxN4b1O31LSdUt47uzvLd90c8LrlXU+9SSalABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAcv8AEXx/4W+FfgnWviB4y1AWekaFaPeXUnVto6Kg/idjhVX+JiKAPwE+P/xr8T/tB/FXW/id4pk2SahN5dna790dlZpxFAn+6Ov95t7fxVZZ51QAUAFABQAUAfcv/BOX9tb/AIU/r1v8FfiZqWPBWs3H/Etu5n+XRruRuhJ+7byN1/ut839+kxM/YEHdhgeKkkdQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAfkZ/wAFRP2qv+FgeMj8AvBOqbvDvha53a1NA/y3upjjyuPvJB0/66b/AO4tXEpHwVQMKACgAoAKACgAoA/VH/gml+2uPFVlZfs7fFXWN2s2kXl+F9SuH+a9t0X/AI85Cf8AlrGP9X/eX5fvL8ykQfovUgFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAfLv7fP7UcX7OHwlmtvD96q+NvFaSWOhoD81qu397eEf9Mwfk9ZCnbdQB+HcsstzK800kkskr7pJG+ZnY9WJqyxtABQAUAFABQAUAFAFiwv7zSr231LTbye2vLOZZ7e4gdo5IpEbKOhHKsGoA/az9gr9sjT/2kvBf/CL+ML2CD4h+HIF/tCLKr/aVuPlW8jX/AMdkUfdb/ZZagg+tKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgDn/G3jTw58PvCmq+NPFmopY6RotpLe3lwx+5Gi5P1Y9h3oA/An9pT48+I/wBo74t6v8Std8yC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AoavpGma/pl3omt6fb31hfQtb3VrcIJI5o2GGR1PBBFAHwp8RP8AgkL8HvEuuzar4B8f654Rtbh/MbTjbJqEMWe0Rd0dV/3maq5gLfhf/gkF8ANMZJvFHjfxnrki/ejjmgtIW/ARs/8A4/RzAeu+Ff8Agnh+yB4S2zW3wfs9SmHWTVL25vN3/bOSQx/+O1IHsHhT4OfCPwOqDwZ8L/Cmh7PunT9Gt7dh+KIDQB2VABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAfOv/AAUI1BdP/Y4+JVwz7d1jaQf9/L23T/2egD8IassKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPor/gnprI0L9sX4b3Jfas93d2Tf7fnWU8S/8Ajz0hH7vVJIUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQB8sf8FNbv7P8Asa+NIf8An5udKi/8n4G/9koiB+H1WWFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAHpX7NOtt4b/aJ+GWtpJtW28WaS0jf9MzcoJP8AxxnoA/oeqCAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD49/4Kq3v2b9knUIP+fvXtNh/KRn/wDZKqO4H4s0ywoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAu6Nqlxoms6frdt/rtPuI7mP/ejZWH/AKDQB/SnZXUN9Z295a/NFcRLLGf9lhkVBBYoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD4d/4K8X32b9mjQrRP8Al88ZWUbf7otLxv8A2WqiB+PNMsKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD+ij4Ba8fFPwM+HniPqdT8LaVdv/ALz2kZP61BB6BQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAHwD/wWLu9nwT8FWP8Az18U+b/3xaTj/wBnq4gfkrQWFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQB+8/7A2vL4k/ZB+Gl/v3GDTJNPP/btcywf+0qgg+gaACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA/Ob/gsve7PBfwy03/nvqmoz/wDfuGIf+1KqIH5YUywoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP2j/wCCVGvpq/7JlpYLJu/sTXtRsT/s5ZJ8f+R6UiD7FqQCgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA/MX/gs7eb7r4S2H9yLXJmX6tYgfyq4lxPzRoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD9X/8AgjhrfnfCjx/4b3/NY+IYb3b/ANd7ZV/9t6UiD9CakAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPyp/wCCyt7v+IPw303/AJ4aNez/APfy4Qf+0quIRPztoLCgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA/Rz/gjTrPk+Lfid4e8z/j807Tr3b/1xmnX/ANuKJBI/UyoICgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA/Ib/AILBaj5v7QvhXSsfLbeDoZf+BSXt1/8AEVcS4nwhQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAH2v/AMEkNbGnftP6hppk+XV/Cd7bbf7zJPbyj/x2J6JBI/ZGoICgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA/Gb/grLe/af2qoof8Anz8LWEH5yTyf+z1cS4nxhQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAH0p/wAE5tebQf2xPADmTbFfS3tlJ/t+bZThP/H9lIR+6lSSFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQB+I3/AAU/v0vP2w/FFt/z46fplt+dpFL/AO1auJcT5QoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD1D9l/Xm8MftHfDLW/M2rB4s0xZG/6ZvcpHJ/44z0Af0MVBAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAH4R/wDBQ29+3/tlfEib+7d2UH/fuwto/wD2WqKPnOmMKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgDQ0HVp9B17TNetv9dpl3Bdx/70cisP/QaAP6ULW4ivLaK7t33R3CLJG3+yRkVBBYoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPwG/bZv/wC0f2sfihc/3PEM0H/fvbH/AOyVZZ4hQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQB/RX8B/EP/AAlfwQ+H/ibfubVPC+l3bf7z2sZP6moIO9oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP53/wBpa/bVf2ifihfNJu8/xjrTL/u/bZcf+O1ZZ5vQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQB+8/wCwRryeJP2Qvhpfq+7yNLk09v8At2uJYP8A2lUEH0DQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAfzf/FK/wD7V+J3i3Vfv/bNev593+/O5qyzl6ACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP2j/AOCU+vprH7Jtpp6ybv7D17UdPI/u5ZJ8f+TFKRB9i1IBQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAEF1cLaW01y/wByBGkb6Bc0AfzR3U8t5dS3k3zSTu0kjf7RbJqyyKgAoAKAOl+Gngi8+JXxD8L/AA7068jtrrxPrNppMdxJHuWJp5Vj8wgfwru3UAfftr/wRm8Sv/x//HzTI/8Arl4fkk/nOtHMHMaMH/BF8Yzc/tHbv9mPwl/U3tHMHMaMX/BGbQP+W3x/v3/3fDca/wDtwaXMQP8A+HMvhf8A6L3qX/hPx/8Ax+jmAF/4Iy+F/wCL4+at/wCCKP8A+P0cwB/w5l8L/wDRe9S/8J+P/wCP0cwB/wAOZfC//Re9S/8ACfj/APj9HMBFN/wRj0F/9T+0Bfr/AL3huNv/AG4FHMBRl/4Ivruzb/tHYX+FW8I5/X7bT5i+Yqy/8EYdR/5Y/tE27f73hVl/9uzRzBzFG4/4I0eLY/8Aj2+PGky/9dNClX+UzUcxHMZtx/wRw+KSf8efxh8LS/8AXWyuY/5bqOYOYxr/AP4I9ftBQ/8AIN+Ifw+uf+u9zew/yt2o5i+Yw7r/AIJJftS23+p1TwJc/wDXPV7j/wBmgWjmDmOE+JH/AATr/aX+Ffg3WPHnifRNFbSNDt2u76a01eORkhHUhDgtSDmPmWmAUAFAH6v/APBHDXFuPhV8QPDe/wCax8QwXuP+u9ssf/ttSkQfoTUgFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAc38Rr4aX8PvE+p52/Y9GvZ/8AviBzQB/N3VlhQAUAFAHt/wCxDYf2l+1n8L7bO7br0Nz/AN+laT/2SgD9+aggKACgAoAKACgAoAKACgAoAKACgAoAKAPOv2ivD7eKvgH8R/DkY+fUfCmqwR/9dDaybP8Ax7FAH87lWWFABQB+jX/BGjW/J8ZfE3w35n/H7pmnX23/AK4Syp/7cUSCR+p1QQFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAea/tK6i2kfs7fFDUk4a28Hay8f+99ilx+tAH88NWWFABQAUAfSX/BOaw+3/ALZnw6TZlY5dRmY/9c9OuG/9CFIR+61SSFABQAUAFABQAUAFABQAUAFABQAUAFAFW/sotSsLjT7oZiuYXgk/3WXBoA/mr1fTbjR9UvdHvP8Aj4sbiS2k/wB5G2n/ANBqyyrQAUAfan/BJbWxpX7UV1ppcKureFr+02/3mSa3m/8AadEgkfspUEBQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAHif7al9/Zv7KPxSuv73hu5g/wC/i+X/AOz0AfgHVlhQAUAFAH11/wAEsLD7Z+13o9z/AM+Ojanc/nD5f/tWiQSP2uqCAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP53v2k9Bbwx+0P8S9BaPatn4s1ZY1/6Zm5cx/8AjjJVlnnFABQB9H/8E7dbbQf2xfh7MZNkd5cXtlIv97zbKdAP++2SkI/dmpJCgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPm3/gotqn9lfsbfEWZD800NhbD/tpf26H9CaAPwpqywoAKACgD7c/4JE2IuP2ndYufL+W08G3sgb1zd2af+z0SCR+xlQQFABQAUAFABQAUAFABQAUAFABQAUAFABQB+Ef/AAUP0RtC/bF+Itv5e2O5uLS9j/2vPsoHY/8AfTPVFHznTGFAHpX7M+vN4Y/aJ+GWtpJtW28WaT5jf9Mzcosn/jjPQB/Q9UEBQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAHyN/wVJvvsf7IOvW3/AD/atpkH5XCyf+06qO4H4oUywoAKACgD9BP+COGned8WvHuq/wDPt4bhtt3/AF0uVP8A7SokEj9ZKggKACgAoAKACgAoAKACgAoAKACgAoAKACgD8aP+CtOif2V+1Jb6ls2rq/hawu9395lmnh/9o1cS4nxdQAUAXdG1SfRNZstbs/8AXafcR3Mf+9GysP8A0GgD+lOyu4b+zt761O6K5jWWM/7LLkVBBYoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD4d/4K8ao1n+zRounx/ev/GNnE3+6tpdSf8AoSrVRA/HmmWFABQAUAfpT/wRksA+qfFjVNg/c2+iwK3++14f/ZKJBI/T+oICgAoAKACgAoAKACgAoAKACgAoAKACgAoA/K7/AILL6GkPjX4ZeJPL+a+0zUbHd/1wlib/ANuKuJcT86KACgAoA/on/Z98QHxV8Cvh34kbltT8LaVcv/10e1jLf+PZqCD0GgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPz4/4LHX+z4TeAtK/57+I5p8evl2zD/2rVRA/J6mWFABQAUAfqp/wRs00ReAPiRq/X7TrNlbZ/wCucLt/7VpSIP0UqQCgAoAKACgAoAKACgAoAKACgAoAKACgAoA/PX/gsfoS3Hwt+H/iTZzY+ILixB9PtFs0n/ttVRA/KGmWFABQB+8f7APiBfEn7IHw1v8AzNxg06bTz/273UsH/tKoIPoWgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPzO/4LOao6QfCfR0+7I+tXMn4fY1T/ANCariET8yKCwoAKACgD9ef+CPtg0X7PnivUXTb9p8Yzxr/tLHZWuP8A0OlIg+76kAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPjr/gqxoKax+ydd6k8e7+w9e07UA390lngz/5MVUQPxcplhQAUAftD/wAEpdeXV/2T7fTt+5tD8Q6jYsP7u7ZPj/yYpSIPsepAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD8qf+Cyl+H+IPw30sf8ALto17Pt/66Txj/2lVxCJ+dtBYUAFABQB+0n/AASn077F+yZZ3P8A0Edf1G5/Jki/9pUpbkH2JUgFABQAUAFABQAUAFABQAUAFABQAUAFABQB8/ft7+Hk8SfshfEuwZN3kaXHqC/9u1xFP/7SoA/BirLCgAoA/Vz/AII4a4tz8MPiF4b382OvW99j08+38v8A9tqUiD9DKkAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPyB/4LAai1z+0Z4a03/lnZ+DrZv8AgUl3eZ/RVq4lxPhWgAoAKACgD9yP+CamnGw/Y08CO8YV7t9UuW/HUbgD9AKiRB9QUAFABQAUAFABQAUAFABQAUAFABQAUAFABQBwXx38P/8ACV/BP4geGAm5tV8ManZqP9qS1kUfqaAP51KssKACgD9F/wDgjTrnk+N/ib4bMnzX2ladfbf+uEsqf+3FEgkfqjUEBQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAfiz/wAFV9R+3/taXtt/0D9B062/NWl/9q1cS4nx7QAUAFABQB+qP7LH/BQ39mf4RfAPwV8NfFOo+IYNU0PTvIvPL0lpI/OMjyPhwfm+/SaIPY4P+Con7H8/3vGmswf7+hXX9ENHKwLC/wDBTv8AY5f/AJqHqK/73h+9/wDjVHKwJv8Ah5r+xp/0VC7/APCf1H/4xU8oDv8Ah5j+xh/0Vm4/8J/U/wD4xRygPT/gpd+xc/8AzV2Rf+5e1P8A+R6OUCRP+ClH7FT9fjKV/wB7w5qv/wAi0ATQ/wDBR79i6UfJ8aU/4FoWqL/O2oAsQ/8ABRL9jWZcr8bLT/gWkaiv84KAJP8Ah4b+xv8A9Fssf/BXf/8AxigA/wCHhv7G/wD0Wyx/8Fd//wDGKAK//Dxr9jD/AKLXb/8Agl1P/wCR6AKr/wDBSj9ipOnxlLf7vhzVf/kWgCB/+CmH7GSj5PircP8A7vh/Uf6wUcoFWX/gp7+x0n3PiBqcv+74fvf6xiq5WBRuP+Cp37I0P+r8SeIZ/wDrloUw/wDQsUcrAw9T/wCCr/7KTWs1sbTxteRyo0bLFpEXzqRj+OZaOUD8cZfK81/s0kjR728tm+VtvbNMsbQAUAfan/BJbW/7N/alutO3hV1fwtf2m3+8yTQTf+06JBI/ZSoICgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA/Cz/go5qLaj+2Z8QmEm5IG062X/AGNmnWwP/j26rLPmqgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPo//AIJ2622g/ti/D2YybI7y4vbKRf73m2U6Af8AfbJSEfuzUkhQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAfgH+2xqX9q/tYfFK5xu2+Ibi2/wC/W2L/ANkqijxOmMKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD039mTXW8M/tE/DLWlk2rbeLNJ8xv+mZuUWT/AMcZ6AP6G6ggKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD+dn9oa//tT4+/ErURJuF34v1ifd/v3spqyzz2gAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKALuh6pPoOt6frdt/rtPu47uP/ejZWH/oNAH9KdrdRXlrFd27ho7hFkjP+yRkVBBYoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP5r/ABlqia34w13W0k3LqGp3Nzu/66TM3/s1WWY9ABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAH9FXwH18+Kfgf8AD3xIH3NqnhfS7tj/ALT2kZP6moIO+oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAyvFF+NK8N6tqudv2Oxnnz/uxsaAP5rKssKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP3p/YK15PEf7IXwyv0fd5Gktp//gNPLB/7SqCD3+gAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgDz/8AaB1Y6D8B/iPrfew8J6xcr9UtJSKAP516ssKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP2m/4JWa4uq/sk6fYeZu/sXW9RsT/s5kE/8A7cUpEH2FUgFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAeJ/tqal/ZX7KHxSut+3f4bu7b/AL+r5X/s9AH4B1ZYUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAfrJ/wRz1nzvhB468O7+bHxJHe4/wCu9si/+29KRB+glSAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQB8y/8ABSHVG0v9jX4gGJtsl1/Ztqv0fULff/45voA/DGrLCgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD9If8AgjPrYi8S/FDw8ZP+Pyx0u9Vf+uUlwp/9HUSCR+o9QQFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAfHf/BVjVPsH7Jd7bbsf2hr2nW35M8v/tKqiB+LdMsKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPt//gkZrbad+0vq2kmT93qvhO7i2/8ATSO4tpB/46r0SCR+xNQQFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAfBf/AAWF1EQ/ADwlpfmBftPi6Obb/eWOyuh/7UqogfkXTLCgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD6c/4Jta82iftjeBUL7Y9TTUbKT/AIHZTlP/AB9UpMTP3MqSQoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD84f+Cy2rrD4T+GGh78G71HU7sL/ANco4F/9rVcQPy1oLCgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD139kfXj4b/af+Fuqj5B/wlOnW0jf7M8ywv8ApLQB/QXUEBQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAH5Z/wDBZbUfO8W/C/R/+fbT9Tudv/XSWBf/AGlVxLifnHQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAbXgjXP+EY8aeH/ABJ93+yNTtL7d/1ymWT/ANloA/pMR1ddynioIHUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQB+Qn/BYHVnuf2h/C+jr/q7HwhBL/wBtJLu6z/46iVcS4nwlQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAH9IHwv1xfE/wANPCXiRX3rq2hWF7u/vebbo/8AWoIOooAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD8Vv+Cqmqfb/ANrbULPzP+QboenW35xtL/7Vq4lxPkCgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP3/AP2MNa/t79lP4W3+/d5Xhu0ss/8AXuvkf+0qgg9poAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD8Jv+CiWo/wBqftk/EibzNyxXFhbL/seXYW8f/oQqij5wpjCgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA/bz/gmPrP9q/sd+ErZpAzaVd6pZN/4Gyyj9JRUSIPqygAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP5+f2wtW/tv9qf4q3iPu2+Kb+0/78TND/7JVlnjtABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAfr3/wSC1p739nnxLok0m5tN8WTMi/3Y5bS2I/8eD0pEH3bUgFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQB/OT8adS/tj4yeOtY+99u8T6pc7v9+5dv/Zqss42gAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAP08/4Iza9v0v4p+GH/AOWFxpN9H/20W4R//RSUSIkfpZUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAFe8uo7S1mvJj+7gRpG/3QuaAP5p7+8l1K/uNSuf8AXXMzTyf7ztk1ZZXoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD7/AP8AgjrryW3xm8ceG/M/5CHhlb5V/wCuFzEv/txRIJH601BAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAch8XdW/sH4UeNdc37f7P8Pajd7v8ArnbO39KAP5xqssKACgAoA7r4GfCfUfjl8WPD/wAKNK1SDTLrxBLJBHdTo0kcWyF5ckDn+CgD6D8c/wDBLP8Aau8JvK+h6JoXiy3T7smk6nGrbf8Arnc+Uf8AgK7qOYOY8M8Vfs0/tCeCmZfE3wU8Z2SL96ZtFnkh/wC/qoU/8eoA86uLe4tpXtrm3kimi+Vo5U2sje4NAEVABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQB9f/APBK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9agg7+gAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD82/+CzOs+ToPwt0EH/j6u9WvG/7ZR26j/0dVxA/LugsKACgAoA/Wz/gjrpvk/A/xrrH/Pz4p+zZ/wCuVpA3/talIg+/KkAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA/Oj/gspoizeBPht4k2Zax1a/sd3/XeGNv/beqiB+V1MsKACgD97v2E9bXX/2R/hlfK+4RaN9i/wDAeWSD/wBpVBB71QAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQB+Vf/AAWT1TzvH3w30fzP+PbR7652/wDXWZF/9o1cS4n510AFABQAUAfs9/wSi0hdN/ZRivNm3+1fEeo3f+9jyoc/+QaUiD7KqQCgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgD4l/4K3aJ/an7MWn6pH10fxXZXLN6K0FxF/wChSrVRA/HGmWFABQB+2P8AwS51f+0v2QfD9n5m7+ytT1O0/wB3Ny03/taokQfW9ABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAH47f8Fd9Ue8/aY0Sw8z93p/hC0j2/7T3N0x/Rkq4lxPiCgAoAKACgD9zv+Cb+kHR/2Nfh+kg2yXg1G7b/ALaX9wU/8c2VBB9NUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAHzB/wUm0ZtY/Y38dvFHuk099OvU/4BfwB//HGeiIH4bVZYUAFAH66f8EetYa5+Afi3RXk3fYfFkk6r/dWW0t//AGaN6UiD70qQCgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPxG/wCCn2srqv7YXiezR8/2Vp2l2WPraJN/7Wq4lHyhQMKACgAoA/oB/Y20saP+yr8LLPG3zPDFldf9/o/N/wDZ6gg9noAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAPHf2w9IGt/ss/FSz2btnhW/u9v/XCJpv/AGSgD+fmrLCgAoA/Tb/gjJrbPbfFTw3IcLE+kXsS+5+1K/8A6DFRIiR+mVQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQB+Cn7eWqf2x+138TbzzN3lastp/34t4ov/ZKsuJ4FQAUAFABQB/Rt8G9HXw98IfA+gImxdN8N6ZaBf7vl20a/wBKgg7KgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA5j4m6OPEPw28V6Cybv7S0S/tNv/XSB1/8AZqAP5vqssKACgD79/wCCOuuJa/Gvxt4cMn/IQ8MfbFX/AK4XcS/+3FEgkfrXUEBQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAH8737SOrNrX7QnxN1dn3fafF+sSL/ALv2uXZ/47VlnnFABQAUAWNNs7jUr+3022+aa8lWCP8A3nbAoA/p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AUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAHE+LfjV8IPAW9fGnxS8J6GycFL/WbeGTPptZwaAPJfEH/AAUN/Y88Nkx3PxnsbyTsLDT7u63/APAooin60AcLqn/BV39lGwDfZrnxZqWP+fbRdv8A6NkSq5QOdl/4LB/s4p/qfAfxJb/e0+wX/wBuzRygNj/4LB/s6H/XfD/4jJ/uWVg3/t2KOUDf03/grJ+ytf7PtMfjPT93/PzpEbbf+/Ur1PKB2ug/8FHf2OvEEqwx/FtLGZv4dQ0m9t1/7+GHZ/49QB6v4T/aD+Bfjt1g8H/GDwbq8z9Le21m3ab/AL979/6UAegqwcblORQA6gAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA/H39rH9t39qT4dftF+PfBPgz4r3emaLo+rNbWNqul2UixR+WpxveFnb/gTVRR5R/wAPEv2yv+i23f8A4KNO/wDjFMYf8PEv2yv+i23f/go07/4xQAf8PEv2yv8Aott3/wCCjTv/AIxQAf8ADxL9sr/ott3/AOCjTv8A4xQAf8PEv2yv+i23f/go07/4xQAf8PEv2yv+i23f/go07/4xQAf8PEv2yv8Aott3/wCCjTv/AIxQ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XyFio5mB6r4W/Yt/ZU8GPE+ifAvwuzxfck1C1+3uuO+65MhqQPX9M0fSdEtEsNF0u00+2T7sNrCsUa/8BXAoAvUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAcZ41+Dvwq+I6svj74b+G/EO4ff1LTIbiRfo7qWX8KAPD/ABR/wTX/AGP/ABNM9yvw0m0WZ+r6Vq11Cv8A37LtGP8AvmjmA8z1f/gj/wDs83krzaP478fadu6RtdWk0a/TMAP/AI9VcwHO3H/BG34cu2bf4z+JYh/000+3b+RFPmAZb/8ABGv4dpzc/GvxFJ/1z0u3X+ppcwHRaX/wR9+ANvIsmseP/Ht6F+8I57SFW/8AIDGjmA9I8Nf8Ey/2QPD0qT3Pw/v9bki+6dS1m6dfxSN0RvxWp5gPbfBHwK+C/wANtr+A/hZ4X0OZf+Xiz0uGOb8Zdu8/nQB3tABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFA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BQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAf/Z"
st.markdown(f"""
<div class="header-wrap">
    <img src="data:image/jpeg;base64,{_LOGO_B64}" class="header-logo" alt="ECU — Elegir Carrera Universitaria" />
    <h1 class="header-title">Buscador de Carreras Universitarias Oficiales en España</h1>
    <p class="header-sub">Consulta en tiempo real en el registro oficial del Ministerio de Educación</p>
</div>
""", unsafe_allow_html=True)


# ─── Load form options ────────────────────────────────────────────────────────
try:
    options = _load_options()
except Exception:
    options = None
    st.warning("No se pudo conectar con el RUCT para cargar las opciones. "
               "Comprueba tu conexión e intenta de nuevo.")

# Prepare selectbox lists
if options:
    univ_display, univ_values = _prepare_options(options["universidades"])
    rama_display, rama_values = _prepare_options(options["ramas"])
    tipo_display, tipo_values = _prepare_options(options["tipos"])
else:
    univ_display = ["Todas"]
    univ_values  = {"Todas": ""}
    rama_display = ["Todas", "Artes y Humanidades", "Ciencias",
                    "Ciencias de la Salud", "Ciencias Sociales y Jurídicas",
                    "Ingeniería y Arquitectura"]
    rama_values  = {
        "Todas": "", "Artes y Humanidades": "431001", "Ciencias": "431002",
        "Ciencias de la Salud": "431005", "Ciencias Sociales y Jurídicas": "431003",
        "Ingeniería y Arquitectura": "431004",
    }
    tipo_display = ["Todos", "Grado", "Máster", "Doctor"]
    tipo_values  = {"Todos": "", "Grado": "G", "Máster": "M", "Doctor": "D"}


# ─── Search form ──────────────────────────────────────────────────────────────
with st.form("busqueda_ruct"):
    search_term = st.text_input(
        "Nombre del título",
        placeholder="Ej: Ingeniería Informática, Medicina...",
        help="Busca por palabras en el nombre oficial del título",
    )

    col1, col2 = st.columns(2)
    with col1:
        tipo_sel = st.selectbox(
            "Nivel académico",
            options=tipo_display,
            index=tipo_display.index("Grado") if "Grado" in tipo_display else 0,
        )
    with col2:
        univ_sel = st.selectbox(
            "Universidad",
            options=univ_display,
        )

    st.markdown(
        '<p class="form-hint">Pulsa <strong>Buscar</strong> para realizar la consulta. '
        'Los campos vacíos no aplican filtro.</p>',
        unsafe_allow_html=True,
    )

    submitted = st.form_submit_button(
        "Buscar", use_container_width=True, type="primary"
    )


# ─── Run search ───────────────────────────────────────────────────────────────
if submitted:
    tipo_val = tipo_values.get(tipo_sel, "")
    univ_val = univ_values.get(univ_sel, "")

    with st.spinner("Consultando el RUCT... esto puede tardar unos segundos."):
        df, warning = ruct_scraper.search_ruct(
            descripcion=search_term,
            codigo="",
            universidad=univ_val,
            tipo=tipo_val,
            rama="",
            estado="P",
            situacion="A",
            historico="N",
            timeout=30,
            max_paginas=200,
        )

    st.session_state["df_resultados"] = df
    st.session_state["warning_scraper"] = warning
    st.session_state["last_search_term"] = search_term.strip()
    # Reset selected degree when a new search is performed
    st.session_state["selected_degree"] = None


# ─── Display results ──────────────────────────────────────────────────────────
df_res = st.session_state.get("df_resultados")
warning_msg = st.session_state.get("warning_scraper")

if df_res is not None:
    if warning_msg:
        st.markdown(
            f'<div class="warn-box">⚠️ {warning_msg}</div>',
            unsafe_allow_html=True,
        )

    if df_res.empty:
        last_term = st.session_state.get("last_search_term", "")
        if last_term:
            st.markdown(
                '<div class="warn-box">⚠️ El RUCT no devolvió resultados para tu búsqueda. '
                'Si el término es habitual (p.ej. «Ingeniería», «Medicina»), '
                'es posible que el servidor del RUCT esté temporalmente no disponible. '
                'Por favor, espera unos minutos e inténtalo de nuevo.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="info-box">No se encontraron resultados con los filtros seleccionados. '
                'Prueba a ampliar la búsqueda o cambiar los parámetros.</div>',
                unsafe_allow_html=True,
            )

    else:
        n = len(df_res)
        selected = st.session_state.get("selected_degree")

        # ── Detail view: study plan for the selected degree ────────────────────
        if selected:
            if st.button("← Volver a los resultados"):
                st.session_state["selected_degree"] = None
                st.rerun()

            # Use session_state as a cache to avoid re-fetching
            if "study_plans" not in st.session_state:
                st.session_state["study_plans"] = {}
            plan_key = f"{selected['title']}|||{selected['university']}"

            if plan_key not in st.session_state["study_plans"]:
                with st.spinner("Cargando ficha y plan de estudios..."):
                    st.session_state["study_plans"][plan_key] = _find_study_plan(
                        selected["title"],
                        selected["university"],
                        selected.get("url_ruct", ""),
                        selected.get("url_plan", ""),
                    )

            plan = st.session_state["study_plans"][plan_key]
            ficha = plan.get("ficha", {})

            # ── Título y botón RUCT ─────────────────────────────────────────────────
            denom = ficha.get("denominacion") or selected["title"]
            st.markdown(f"### {denom}")
            univ = ficha.get("universidad") or selected["university"]
            st.caption(univ)
            if selected.get("url_ruct"):
                st.link_button("Ver ficha en el RUCT →", selected["url_ruct"])
            st.divider()

            # ── Ficha de la titulación ────────────────────────────────────────────────────
            def _row(label, value):
                if value:
                    st.markdown(f"**{label}:** {value}")

            _row("Centro", ficha.get("centro"))
            _row("Comunidad Autónoma", ficha.get("ccaa"))

            nivel = ficha.get("nivel", "")
            meces = ficha.get("meces", "")
            if nivel and meces:
                _row("Nivel académico", f"{nivel}, MECES {meces}")
            elif nivel:
                _row("Nivel académico", nivel)

            _row("Rama de conocimiento", ficha.get("rama"))
            _row("Campo de estudio", ficha.get("campo"))

            habilita = ficha.get("habilita", "")
            if habilita:
                _row("Habilita para profesión regulada", habilita)
            if habilita.lower() in ("sí", "si"):
                _row("Profesión regulada", ficha.get("profesion_regulada"))
                _row("Norma reguladora", ficha.get("norma"))

            menciones = ficha.get("menciones", [])
            especialidades = ficha.get("especialidades", [])
            if menciones:
                st.markdown("**Menciones:**")
                for m in menciones:
                    cred = f" ({m['creditos']} ECTS)" if m.get("creditos") else ""
                    st.markdown(f"- {m['nombre']}{cred}")
            if especialidades:
                st.markdown("**Especialidades:**")
                for e in especialidades:
                    cred = f" ({e['creditos']} ECTS)" if e.get("creditos") else ""
                    st.markdown(f"- {e['nombre']}{cred}")

            st.divider()

            # ── Plan de estudios ──────────────────────────────────────────────────────────
            if plan.get("source_url"):
                src = plan["source_url"]
                btn_label = "Ver en el BOE →" if "boe.es" in src else "Ver plan de estudios →"
                st.link_button(btn_label, src, use_container_width=True)
                st.divider()

            if plan.get("page_text"):
                st.markdown(plan["page_text"])
            elif plan.get("source_url"):
                st.markdown(
                    '<div class="info-box">El plan de estudios está disponible en el BOE. '
                    'Pulsa el botón de arriba para consultarlo directamente.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="warn-box">⚠️ No se pudo obtener el plan de estudios. '
                    'Consulta la ficha oficial usando el botón «Ver ficha en el RUCT →» de arriba.</div>',
                    unsafe_allow_html=True,
                )

        # ── Results list ───────────────────────────────────────────────────────
        else:
            # Quick metrics
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Títulos encontrados", f"{n:,}")
            with col_m2:
                st.metric("Universidades", f"{df_res['universidad'].nunique():,}")

            st.divider()

            # Pagination
            page_size = 25
            total_pages = max(1, (n - 1) // page_size + 1)
            detail_page = st.number_input(
                f"Página (de {total_pages})",
                min_value=1,
                max_value=total_pages,
                value=st.session_state.get("result_page", 1),
                step=1,
            )
            st.session_state["result_page"] = detail_page
            start = (detail_page - 1) * page_size
            end = min(start + page_size, n)
            st.caption(f"Mostrando {start + 1}–{end} de {n} resultados · pulsa un título para ver su plan de estudios")

            # One row per result: title+university on the left, "Ver" button on the right
            for i, (_, row) in enumerate(df_res.iloc[start:end].iterrows()):
                col_info, col_btn = st.columns([6, 1])
                with col_info:
                    st.markdown(
                        f'<span class="result-title">{row["titulo"]}</span>'
                        f'<br><span class="result-univ">{row["universidad"]}</span>',
                        unsafe_allow_html=True,
                    )
                with col_btn:
                    if st.button("Ver", key=f"view_{start + i}", use_container_width=True):
                        st.session_state["selected_degree"] = {
                            "title": row["titulo"],
                            "university": row["universidad"],
                            "url_ruct": row.get("url_ruct", ""),
                            "url_plan": row.get("url_plan", ""),
                        }
                        st.rerun()

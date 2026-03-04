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
    page_title="Buscador RUCT — Carreras Universitarias España",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        color-scheme: light;
        --color-bg: #FFFFFF;
        --color-surface: #FAFAFA;
        --color-border: #E5E5E5;
        --color-text-primary: #171717;
        --color-text-secondary: #737373;
        --color-text-tertiary: #A3A3A3;
        --color-accent: #3B82F6;
        --color-accent-light: #DBEAFE;
        --color-accent-dark: #1D4ED8;
        --color-success: #10B981;
        --color-success-light: #D1FAE5;
        --color-warning: #F59E0B;
        --radius-lg: 0.75rem;
    }

    body, p, h1, h2, h3, h4, h5, h6, div, label, button,
    input, select, textarea, li, a, td, th {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    [data-testid="stToolbar"] {
        background: transparent !important;
        box-shadow: none !important;
    }
    [data-testid="stToolbar"] .stAppToolbarActions,
    [data-testid="stToolbar"] [data-testid="stDecoration"] { display: none !important; }

    [data-testid="stExpandSidebarButton"] button {
        min-width: 44px !important;
        min-height: 44px !important;
    }

    .stApp { background: #FFFFFF; }

    .main .block-container {
        padding: 3.5rem 1rem 2rem 1rem;
        max-width: 800px;
        background: #FFFFFF;
    }

    /* Metrics */
    div[data-testid="metric-container"] {
        background: #FFFFFF;
        padding: 0.875rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--color-border);
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700;
        color: #171717;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        font-weight: 600;
        color: var(--color-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Search form submit button — prominent blue */
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button {
        background: var(--color-accent) !important;
        color: white !important;
        border: none !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        min-height: 54px !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35) !important;
        transition: box-shadow 0.2s ease, background 0.2s ease !important;
        width: 100%;
    }
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button:hover {
        background: var(--color-accent-dark) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.45) !important;
    }

    /* Selectbox and text input */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        border-color: var(--color-border) !important;
        border-radius: var(--radius-lg) !important;
        background: #FFFFFF !important;
        min-height: 44px;
    }
    .stTextInput > div > div > input {
        border-color: var(--color-border) !important;
        border-radius: var(--radius-lg) !important;
        min-height: 44px;
    }

    /* Header */
    .header-container {
        padding: 1.25rem 0 1rem;
        border-bottom: 1px solid var(--color-border);
        margin-bottom: 1.5rem;
        background-color: #FFFFFF;
    }
    .header-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #171717 !important;
        margin: 0;
        letter-spacing: -0.02em;
        text-align: center;
    }
    .header-subtitle {
        text-align: center;
        font-size: 0.875rem;
        color: #737373 !important;
        margin: 0.375rem 0 0.75rem;
    }
    .header-badges {
        display: flex;
        justify-content: center;
        gap: 0.375rem;
        flex-wrap: wrap;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.3rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
        border: 1px solid var(--color-border);
        background: var(--color-surface);
        color: #171717;
    }
    .badge-country {
        background: var(--color-accent-light);
        color: var(--color-accent-dark);
        border-color: #93C5FD;
    }
    .badge-source {
        background: var(--color-success-light);
        color: #065F46;
        border-color: #6EE7B7;
    }

    /* Form section */
    [data-testid="stForm"] {
        background: var(--color-surface);
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-lg);
        padding: 1.25rem;
        margin-bottom: 1.5rem;
    }
    .form-hint {
        font-size: 0.75rem;
        color: var(--color-text-tertiary);
        margin-top: 0.5rem;
    }

    /* Results list */
    .result-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .result-list li {
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--color-border);
        display: flex;
        flex-direction: column;
    }
    .result-list li:last-child { border-bottom: none; }
    .result-title {
        font-size: 0.95rem;
        font-weight: 500;
        color: #171717;
        line-height: 1.4;
    }
    .result-univ {
        font-size: 0.78rem;
        color: var(--color-text-secondary);
        margin-top: 0.15rem;
    }

    /* Warning / info boxes */
    .warn-box {
        background: #FFFBEB;
        border: 1px solid #FCD34D;
        border-left: 3px solid var(--color-warning);
        border-radius: var(--radius-lg);
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
        color: #92400E;
        margin-bottom: 1rem;
    }
    .info-box {
        background: var(--color-accent-light);
        border: 1px solid #93C5FD;
        border-left: 3px solid var(--color-accent);
        border-radius: var(--radius-lg);
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
        color: var(--color-accent-dark);
        margin-bottom: 1rem;
    }

    hr {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: var(--color-border);
    }

    a { color: var(--color-accent); text-decoration: none; font-weight: 500; }
    a:hover { color: var(--color-accent-dark); }

    /* Hide English "Press Enter to submit form" notification */
    [data-testid="InputInstructions"] { display: none !important; }

    @media (max-width: 640px) {
        .main .block-container {
            padding: 0.5rem 0.75rem 2rem 0.75rem;
        }
        .header-title { font-size: 1.25rem; }
    }
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


def _fetch_boe_url_from_ruct(url_ruct: str, url_plan: str) -> str:
    """
    Get the BOE study plan HTML URL from the RUCT degree page.

    Session flow:
      1. GET consultaestudios.action    — init session
      2. GET url_plan (lupa link)       — register this degree in server session
      3. GET url_ruct (estudio.action)  — now returns full page including div#ttwo

    div#ttwo contains the label 'Publicación Plan Estudios en el BOE' with the PDF link.
    Returns the BOE HTML URL (txt.php), or "" on failure.
    """
    if not url_ruct or not url_plan:
        return ""
    try:
        session = requests.Session()
        session.headers.update(_WEB_HEADERS)
        session.get(_RUCT_INIT_URL, timeout=15)
        session.get(url_plan, timeout=15)
        r = session.get(url_ruct, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        ttwo = soup.find("div", id="ttwo")
        if not ttwo:
            return ""
        # The label for="f_plan" wraps the 'Publicación Plan Estudios en el BOE' link
        plan_label = ttwo.find("label", {"for": "f_plan"})
        if plan_label:
            a = plan_label.find("a", href=True)
            if a:
                return _boe_pdf_to_html(a["href"])
        # Fallback: scan labels in div#ttwo for 'Plan Estudios'
        for label in ttwo.find_all("label"):
            if "Plan Estudios" in label.get_text():
                a = label.find("a", href=True)
                if a and "boe.es" in a["href"] and ".pdf" in a["href"]:
                    return _boe_pdf_to_html(a["href"])
        return ""
    except Exception:
        return ""


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
    Tables are converted to Markdown format for clean display.
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
        seen_tables: set = set()

        def _process(node) -> None:
            for child in node.children:
                if not hasattr(child, "name") or not child.name:
                    continue
                if child.name == "table":
                    tid = id(child)
                    if tid not in seen_tables:
                        seen_tables.add(tid)
                        md = _html_table_to_md(child)
                        if md:
                            parts.append(md)
                elif child.name in ("p", "h2", "h3", "h4"):
                    text = child.get_text(strip=True)
                    if text:
                        parts.append(text)
                else:
                    _process(child)

        _process(content)
        return "\n\n".join(parts)[:12000]
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
    Locate the study plan for a RUCT degree.

    Source chain:
      1. Primary: BOE 'Publicación Plan Estudios' from RUCT div#ttwo (via session)
         Complete plan: subjects, credits, type, temporal organisation.
      2. Fallback: RUCT datosModulo page — list of module/subject names.

    Returns {"page_text": str, "source_url": str}
    """
    # Step 1: RUCT degree page → BOE plan PDF → BOE HTML → extract div#textoxslt
    boe_url = _fetch_boe_url_from_ruct(url_ruct, url_plan)
    if boe_url:
        plan_text = _fetch_boe_plan(boe_url)
        if plan_text:
            return {"page_text": plan_text, "source_url": boe_url}

    # Step 2: RUCT modules page (fallback — subject names only, no credits)
    modules_text = _fetch_ruct_modules(url_plan) if url_plan else ""
    if modules_text:
        return {"page_text": modules_text, "source_url": ""}

    return {"page_text": "", "source_url": ""}


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <h1 class="header-title">Buscador de Carreras Universitarias</h1>
    <p class="header-subtitle">
        Consulta en tiempo real el RUCT — Registro oficial del Ministerio de Educación
    </p>
    <div class="header-badges">
        <span class="badge badge-country">España</span>
        <span class="badge badge-source">Fuente: RUCT oficial</span>
    </div>
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

    col1, col2, col3 = st.columns(3)
    with col1:
        tipo_sel = st.selectbox(
            "Nivel académico",
            options=tipo_display,
            index=tipo_display.index("Grado") if "Grado" in tipo_display else 0,
        )
    with col2:
        rama_sel = st.selectbox(
            "Rama de conocimiento",
            options=rama_display,
        )
    with col3:
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
    rama_val = rama_values.get(rama_sel, "")
    univ_val = univ_values.get(univ_sel, "")

    with st.spinner("Consultando el RUCT... esto puede tardar unos segundos."):
        df, warning = ruct_scraper.search_ruct(
            descripcion=search_term,
            codigo="",
            universidad=univ_val,
            tipo=tipo_val,
            rama=rama_val,
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

            st.markdown(f"### {selected['title']}")
            st.caption(selected["university"])
            if selected.get("url_ruct"):
                st.link_button("Ver ficha en el RUCT →", selected["url_ruct"])
            st.divider()

            # Use session_state as a cache to avoid re-fetching
            if "study_plans" not in st.session_state:
                st.session_state["study_plans"] = {}
            plan_key = f"{selected['title']}|||{selected['university']}"

            if plan_key not in st.session_state["study_plans"]:
                with st.spinner("Buscando el plan de estudios..."):
                    st.session_state["study_plans"][plan_key] = _find_study_plan(
                        selected["title"],
                        selected["university"],
                        selected.get("url_ruct", ""),
                        selected.get("url_plan", ""),
                    )

            plan = st.session_state["study_plans"][plan_key]

            if plan.get("source_url"):
                src = plan["source_url"]
                btn_label = "Ver en el BOE →" if "boe.es" in src else "Ver plan de estudios →"
                st.link_button(btn_label, src, use_container_width=True)
                st.divider()

            if plan.get("page_text"):
                st.markdown(plan["page_text"])
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

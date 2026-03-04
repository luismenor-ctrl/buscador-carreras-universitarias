import streamlit as st
import pandas as pd
import logging
import urllib.parse
import ruct_scraper

logging.basicConfig(level=logging.INFO)

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
        --shadow-sm: 0 1px 2px 0 rgba(0,0,0,0.05);
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

    /* Expanders */
    [data-testid="stExpander"] {
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-lg) !important;
        overflow: hidden;
        margin-bottom: 0.5rem;
    }
    [data-testid="stExpander"] summary,
    .streamlit-expanderHeader {
        background: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: #171717 !important;
        padding: 0.875rem 1rem !important;
        border: none !important;
    }
    [data-testid="stExpanderDetails"] {
        padding: 0.75rem 1rem 1rem 1rem !important;
        border-top: 1px solid var(--color-border) !important;
    }

    /* Buttons */
    .stButton > button {
        background: var(--color-accent) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-lg) !important;
        padding: 0.625rem 1.25rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        width: 100%;
        min-height: 44px;
    }
    .stButton > button:hover { background: var(--color-accent-dark) !important; }

    /* Search button — more prominent */
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button {
        background: var(--color-accent) !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        min-height: 54px !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35) !important;
        transition: box-shadow 0.2s ease, background 0.2s ease !important;
    }
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button:hover {
        background: var(--color-accent-dark) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.45) !important;
    }

    /* Selectbox and multiselect */
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

    /* Radio buttons */
    .stRadio label { min-height: 36px; display: flex; align-items: center; }

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

    /* Form section — applied to st.form's native container */
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
    .result-list li a {
        font-size: 0.95rem;
        font-weight: 500;
        color: var(--color-accent);
        text-decoration: none;
        line-height: 1.4;
    }
    .result-list li a:hover { color: var(--color-accent-dark); }
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

    /* Separator */
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

        # Quick metrics
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Títulos encontrados", f"{n:,}")
        with col_m2:
            st.metric("Universidades", f"{df_res['universidad'].nunique():,}")

        st.divider()

        # Pagination controls
        page_size = 25
        total_pages = max(1, (n - 1) // page_size + 1)
        detail_page = st.number_input(
            f"Página (de {total_pages})",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
        )
        start = (detail_page - 1) * page_size
        end = min(start + page_size, n)
        st.caption(f"Mostrando {start + 1}–{end} de {n} resultados")

        # Results list — each title links to a Google search for its study plan
        items_html = ""
        for _, row in df_res.iloc[start:end].iterrows():
            title = row["titulo"]
            univ = row["universidad"]
            query = urllib.parse.quote(f'"{title}" plan de estudios {univ}')
            url = f"https://www.google.com/search?q={query}"
            items_html += (
                f'<li><a href="{url}" target="_blank" rel="noopener">{title}</a>'
                f'<span class="result-univ">{univ}</span></li>'
            )

        st.markdown(f'<ul class="result-list">{items_html}</ul>', unsafe_allow_html=True)

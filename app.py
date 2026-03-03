import streamlit as st
import pandas as pd
import logging
import ruct_scraper

logging.basicConfig(level=logging.INFO)

# ─── Configuración de página ──────────────────────────────────────────────────
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

    .stApp { background: var(--color-bg); }

    .main .block-container {
        padding: 3.5rem 1rem 2rem 1rem;
        max-width: 800px;
        background: var(--color-bg);
    }

    /* Sidebar (no se usa en este flujo, pero por si acaso) */
    [data-testid="stSidebar"] {
        background: var(--color-surface);
        border-right: 1px solid var(--color-border);
    }

    /* Métricas */
    div[data-testid="metric-container"] {
        background: var(--color-bg);
        padding: 0.875rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--color-border);
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700;
        color: var(--color-text-primary);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        font-weight: 600;
        color: var(--color-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 1px solid var(--color-border);
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        flex-wrap: nowrap;
    }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        border-radius: 0;
        color: var(--color-text-secondary);
        font-weight: 500;
        font-size: 0.875rem;
        padding: 0.75rem 0.875rem;
        white-space: nowrap;
    }
    .stTabs [aria-selected="true"] {
        color: var(--color-accent) !important;
        background: transparent !important;
        border-bottom-color: var(--color-accent) !important;
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
        background: var(--color-bg) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: var(--color-text-primary) !important;
        padding: 0.875rem 1rem !important;
        border: none !important;
    }
    [data-testid="stExpanderDetails"] {
        padding: 0.75rem 1rem 1rem 1rem !important;
        border-top: 1px solid var(--color-border) !important;
    }

    /* Botones */
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

    /* Selectbox y multiselect */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        border-color: var(--color-border) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--color-bg) !important;
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
    }
    .header-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--color-text-primary);
        margin: 0;
        letter-spacing: -0.02em;
        text-align: center;
    }
    .header-subtitle {
        text-align: center;
        font-size: 0.875rem;
        color: var(--color-text-secondary);
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
        color: var(--color-text-primary);
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

    /* Sección de formulario */
    .form-section {
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: 1.25rem;
        margin-bottom: 1.5rem;
    }
    .form-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--color-text-primary);
        margin: 0 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--color-border);
    }
    .form-hint {
        font-size: 0.75rem;
        color: var(--color-text-tertiary);
        margin-top: 0.5rem;
    }

    /* Tabla de resultados */
    .stDataFrame {
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        overflow: hidden;
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

    /* Separador */
    hr {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: var(--color-border);
    }

    a { color: var(--color-accent); text-decoration: none; font-weight: 500; }
    a:hover { color: var(--color-accent-dark); }

    @media (max-width: 640px) {
        .main .block-container {
            padding: 0.5rem 0.75rem 2rem 0.75rem;
        }
        .header-title { font-size: 1.25rem; }
        .form-section { padding: 1rem; }
    }
</style>
""", unsafe_allow_html=True)


# ─── Carga de opciones (con caché 1 hora) ─────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Conectando con el RUCT...")
def _cargar_opciones():
    return ruct_scraper.cargar_opciones_formulario(timeout=20)


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


# ─── Cargar opciones del formulario ───────────────────────────────────────────
try:
    opciones = _cargar_opciones()
except Exception:
    opciones = None
    st.warning("No se pudo conectar con el RUCT para cargar las opciones. "
               "Comprueba tu conexión e intenta de nuevo.")

# Preparar listas para los selectbox
if opciones:
    univ_lista = [(texto, val) for texto, val in opciones["universidades"]]
    univ_display = [texto for texto, val in univ_lista]
    univ_values  = {texto: val for texto, val in univ_lista}

    rama_lista = [(texto, val) for texto, val in opciones["ramas"]]
    rama_display = [texto for texto, val in rama_lista]
    rama_values  = {texto: val for texto, val in rama_lista}

    tipo_lista = [(texto, val) for texto, val in opciones["tipos"]]
    tipo_display = [texto for texto, val in tipo_lista]
    tipo_values  = {texto: val for texto, val in tipo_lista}
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


# ─── Formulario de búsqueda ───────────────────────────────────────────────────
st.markdown('<div class="form-section">', unsafe_allow_html=True)
st.markdown('<p class="form-title">Parámetros de búsqueda</p>', unsafe_allow_html=True)

with st.form("busqueda_ruct"):
    col1, col2 = st.columns([3, 2])
    with col1:
        descripcion = st.text_input(
            "Nombre del título",
            placeholder="Ej: Ingeniería Informática, Medicina...",
            help="Busca por palabras en el nombre oficial del título",
        )
    with col2:
        codigo = st.text_input(
            "Código del título",
            placeholder="Ej: 2500798",
            help="Código numérico exacto del título en el RUCT",
        )

    col3, col4, col5 = st.columns(3)
    with col3:
        tipo_sel = st.selectbox(
            "Nivel académico",
            options=tipo_display,
            index=tipo_display.index("Grado") if "Grado" in tipo_display else 0,
        )
    with col4:
        rama_sel = st.selectbox(
            "Rama de conocimiento",
            options=rama_display,
        )
    with col5:
        univ_sel = st.selectbox(
            "Universidad",
            options=univ_display,
        )

    st.markdown("---")

    col6, col7, col8 = st.columns(3)
    with col6:
        situacion_opts = {
            "Solo activas": "A",
            "Extinguidas": "T",
            "A extinguir": "X",
            "Todas": "",
        }
        situacion_sel = st.selectbox("Situación", options=list(situacion_opts.keys()))
    with col7:
        max_pag = st.number_input(
            "Máx. páginas",
            min_value=1,
            max_value=500,
            value=100,
            step=10,
            help="Cada página contiene ~25 resultados. 100 páginas ≈ 2.500 títulos.",
        )
    with col8:
        timeout_seg = st.number_input(
            "Timeout (s)",
            min_value=5,
            max_value=120,
            value=30,
            step=5,
            help="Segundos de espera máxima por cada petición al servidor del RUCT.",
        )

    st.markdown(
        '<p class="form-hint">Los campos vacíos no aplican filtro. '
        'La búsqueda por nombre no distingue mayúsculas/minúsculas.</p>',
        unsafe_allow_html=True,
    )

    submitted = st.form_submit_button("Buscar en el RUCT", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# ─── Ejecución de la búsqueda ─────────────────────────────────────────────────
if submitted:
    tipo_val = tipo_values.get(tipo_sel, "")
    rama_val = rama_values.get(rama_sel, "")
    univ_val = univ_values.get(univ_sel, "")
    situ_val = situacion_opts.get(situacion_sel, "A")

    with st.spinner("Consultando el RUCT... esto puede tardar unos segundos."):
        df, warning = ruct_scraper.buscar_ruct(
            descripcion=descripcion,
            codigo=codigo,
            universidad=univ_val,
            tipo=tipo_val,
            rama=rama_val,
            estado="P",
            situacion=situ_val,
            historico="N",
            timeout=int(timeout_seg),
            max_paginas=int(max_pag),
        )

    st.session_state["df_resultados"] = df
    st.session_state["warning_scraper"] = warning


# ─── Mostrar resultados ───────────────────────────────────────────────────────
df_res = st.session_state.get("df_resultados")
warning_msg = st.session_state.get("warning_scraper")

if df_res is not None:
    if warning_msg:
        st.markdown(
            f'<div class="warn-box">⚠️ {warning_msg}</div>',
            unsafe_allow_html=True,
        )

    if df_res.empty:
        st.markdown(
            '<div class="info-box">No se encontraron resultados con los filtros seleccionados. '
            'Prueba a ampliar la búsqueda o cambiar los parámetros.</div>',
            unsafe_allow_html=True,
        )
    else:
        n = len(df_res)

        # Métricas rápidas
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Títulos encontrados", f"{n:,}")
        with col_m2:
            n_univ = df_res["universidad"].nunique()
            st.metric("Universidades", f"{n_univ:,}")

        st.markdown("<hr>", unsafe_allow_html=True)

        # Botones de descarga
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_bytes = ruct_scraper.exportar_csv(df_res)
            st.download_button(
                label="Descargar CSV",
                data=csv_bytes,
                file_name="resultados_ruct.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_dl2:
            try:
                excel_bytes = ruct_scraper.exportar_excel(df_res)
                st.download_button(
                    label="Descargar Excel",
                    data=excel_bytes,
                    file_name="resultados_ruct.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except ImportError:
                st.info("Instala openpyxl para exportar a Excel: `pip install openpyxl`")

        st.markdown("<hr>", unsafe_allow_html=True)

        # Tabla de resultados
        # Renombrar columnas para visualización
        df_display = df_res.rename(columns={
            "codigo": "Código",
            "titulo": "Título",
            "universidad": "Universidad",
            "nivel": "Nivel",
            "estado": "Estado",
            "url_ruct": "URL RUCT",
        })

        # Mostrar tabla con la columna URL como enlace (HTML)
        st.dataframe(
            df_display.drop(columns=["URL RUCT"]),
            use_container_width=True,
            hide_index=True,
        )

        # Detalle expandible por cada resultado (muestra el enlace al RUCT)
        st.markdown("---")
        st.markdown("**Ver detalle en el RUCT**")
        pagina_detalle = st.number_input(
            "Página (25 resultados por página)",
            min_value=1,
            max_value=max(1, (n - 1) // 25 + 1),
            value=1,
            step=1,
        )
        inicio = (pagina_detalle - 1) * 25
        fin = min(inicio + 25, n)

        for _, row in df_res.iloc[inicio:fin].iterrows():
            label = f"{row['titulo']} — {row['universidad']}"
            with st.expander(label):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Código:** `{row['codigo']}`")
                    st.markdown(f"**Nivel:** {row['nivel']}")
                    st.markdown(f"**Estado:** {row['estado']}")
                with col_b:
                    if row.get("url_ruct"):
                        st.markdown(
                            f"[Ver en el RUCT]({row['url_ruct']})",
                            unsafe_allow_html=False,
                        )

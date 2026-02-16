import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from data_updater import get_updater, check_and_update_if_needed
import logging

# Configuración de la página
st.set_page_config(
    page_title="Buscador de Carreras Universitarias España",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS minimalista profesional - Mobile-First
st.markdown("""
<script src="https://unpkg.com/lucide@latest"></script>
<style>
    /* ============================================
       DISEÑO MINIMALISTA - MOBILE FIRST
       ============================================ */

    /* Importar fuente Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Variables CSS - Sistema de diseño */
    :root {
        --color-bg: #FFFFFF;
        --color-surface: #FAFAFA;
        --color-border: #E5E5E5;
        --color-border-strong: #D4D4D4;
        --color-text-primary: #171717;
        --color-text-secondary: #737373;
        --color-text-tertiary: #A3A3A3;
        --color-accent: #3B82F6;
        --color-accent-light: #DBEAFE;
        --color-accent-dark: #1D4ED8;
        --color-success: #10B981;
        --color-success-light: #D1FAE5;
        --color-warning: #F59E0B;
        --color-warning-light: #FEF3C7;
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
    }

    /* Reset y base */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fondo limpio */
    .stApp {
        background: var(--color-bg);
    }

    .main .block-container {
        padding: 1rem;
        max-width: 1200px;
        background: var(--color-bg);
    }

    @media (min-width: 1025px) {
        .main .block-container {
            padding: 2rem;
        }
    }

    /* ============================================
       SIDEBAR MINIMALISTA
       ============================================ */
    [data-testid="stSidebar"] {
        background: var(--color-surface);
        border-right: 1px solid var(--color-border);
        padding: 1.5rem 1rem;
    }

    [data-testid="stSidebar"] * {
        color: var(--color-text-primary) !important;
    }

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stSlider label {
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }

    @media (max-width: 1024px) {
        [data-testid="stSidebar"] {
            display: none;
        }
    }

    /* ============================================
       MÉTRICAS MINIMALISTAS
       ============================================ */
    [data-testid="stMetricValue"] {
        font-size: 1.875rem;
        font-weight: 700;
        color: var(--color-text-primary);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--color-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    div[data-testid="metric-container"] {
        background: var(--color-bg);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--color-border);
        transition: border-color 0.2s ease;
    }

    div[data-testid="metric-container"]:hover {
        border-color: var(--color-accent);
    }

    @media (max-width: 640px) {
        div[data-testid="metric-container"] {
            padding: 1rem;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
    }

    /* ============================================
       TABS MINIMALISTAS
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid var(--color-border);
        padding: 0;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
    }

    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        border-radius: 0;
        color: var(--color-text-secondary);
        font-weight: 500;
        padding: 0.75rem 1rem;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--color-text-primary);
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        color: var(--color-accent) !important;
        background: transparent !important;
        border-bottom-color: var(--color-accent);
    }

    @media (max-width: 640px) {
        .stTabs [data-baseweb="tab"] {
            min-width: 100px;
            font-size: 0.875rem;
        }
    }

    /* ============================================
       EXPANDERS MINIMALISTAS
       ============================================ */
    .streamlit-expanderHeader {
        background: var(--color-bg);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        font-weight: 600;
        font-size: 0.9375rem;
        color: var(--color-text-primary);
        padding: 1rem 1.25rem;
        transition: all 0.2s ease;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--color-accent);
        background: var(--color-surface);
    }

    .streamlit-expanderContent {
        background: var(--color-bg);
        border: 1px solid var(--color-border);
        border-top: none;
        border-radius: 0 0 var(--radius-lg) var(--radius-lg);
        padding: 1.5rem;
        margin-top: -1px;
    }

    @media (max-width: 640px) {
        .streamlit-expanderHeader {
            font-size: 0.875rem;
            padding: 0.875rem 1rem;
        }
    }

    /* ============================================
       BOTONES MINIMALISTAS
       ============================================ */
    .stButton > button {
        background: var(--color-accent);
        color: white;
        border: none;
        border-radius: var(--radius-lg);
        padding: 0.625rem 1.25rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: background-color 0.2s ease;
        box-shadow: none;
    }

    .stButton > button:hover {
        background: var(--color-accent-dark);
    }

    /* ============================================
       FORMS MINIMALISTAS
       ============================================ */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        border-color: var(--color-border);
        border-radius: var(--radius-lg);
        background: var(--color-bg);
    }

    /* ============================================
       COMPONENTES CUSTOM
       ============================================ */

    /* Header */
    .header-container {
        padding: 1.5rem 0 1rem;
        border-bottom: 1px solid var(--color-border);
    }

    .header-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
    }

    .header-icon {
        width: 2rem;
        height: 2rem;
        color: var(--color-accent);
        stroke-width: 2;
    }

    .header-title {
        font-size: 1.875rem;
        font-weight: 700;
        color: var(--color-text-primary);
        margin: 0;
        letter-spacing: -0.025em;
    }

    .header-subtitle {
        text-align: center;
        font-size: 1rem;
        color: var(--color-text-secondary);
        font-weight: 400;
        margin: 0.5rem 0 1rem;
        line-height: 1.5;
    }

    .header-badges {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
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

    .badge-updated {
        background: var(--color-success-light);
        color: #065F46;
        border-color: #6EE7B7;
    }

    /* Info boxes */
    .info-box {
        background: var(--color-surface);
        padding: 1rem;
        border-radius: var(--radius-lg);
        border-left: 3px solid var(--color-accent);
        margin: 1rem 0;
    }

    .info-box.success {
        border-left-color: var(--color-success);
        background: #ECFDF5;
    }

    .info-box.warning {
        border-left-color: var(--color-warning);
        background: #FFFBEB;
    }

    /* Footer */
    .footer-section {
        background: var(--color-surface);
        border-top: 1px solid var(--color-border);
        padding: 2rem;
        margin-top: 3rem;
        border-radius: var(--radius-lg);
    }

    /* Enlaces */
    a {
        color: var(--color-accent);
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s ease;
    }

    a:hover {
        color: var(--color-accent-dark);
    }

    /* Dataframes */
    .stDataFrame {
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        overflow: hidden;
    }

    /* Alerts */
    .stAlert {
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: 1rem;
    }

    /* Divisores */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: var(--color-border);
    }

    /* Scrollbar minimalista */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--color-surface);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--color-border);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--color-text-tertiary);
    }

    /* ============================================
       MEDIA QUERIES RESPONSIVE
       ============================================ */
    @media (max-width: 640px) {
        .header-title {
            font-size: 1.5rem;
        }
        .header-subtitle {
            font-size: 0.875rem;
        }
        .header-icon {
            width: 1.5rem;
            height: 1.5rem;
        }
        .footer-section {
            padding: 1rem;
        }
    }
</style>

<script>
// Inicializar iconos Lucide
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
});

// Re-inicializar en cambios de Streamlit
window.addEventListener('streamlit:render', () => {
    lucide.createIcons();
});
</script>
""", unsafe_allow_html=True)

# Función helper para iconos Lucide
def icon_inline(name, size=16):
    """Genera un icono Lucide inline con tamaño personalizado"""
    return f'<i data-lucide="{name}" style="width:{size}px;height:{size}px;vertical-align:middle;margin-right:6px;"></i>'

# Configuración minimalista para gráficos Plotly
CHART_CONFIG = {
    'plot_bgcolor': '#FAFAFA',
    'paper_bgcolor': '#FFFFFF',
    'font': {
        'family': "Inter, sans-serif",
        'size': 12,
        'color': '#171717'
    },
    'xaxis': {
        'showgrid': False,
        'linecolor': '#E5E5E5',
        'tickcolor': '#E5E5E5',
        'tickfont': {'color': '#737373'}
    },
    'yaxis': {
        'showgrid': True,
        'gridcolor': '#F5F5F5',
        'linecolor': '#E5E5E5',
        'tickcolor': '#E5E5E5',
        'tickfont': {'color': '#737373'}
    },
    'margin': {'t': 20, 'b': 40, 'l': 40, 'r': 20},
    'showlegend': True,
    'legend': {
        'bgcolor': 'rgba(255,255,255,0.9)',
        'bordercolor': '#E5E5E5',
        'borderwidth': 1
    }
}

# Sistema de actualización automática de datos
def verificar_y_actualizar_datos():
    """
    Verifica si los datos necesitan actualización y la ejecuta si es necesario
    """
    try:
        # Verificar y actualizar datos si es necesario (max 7 días)
        check_and_update_if_needed('carreras_universidades.csv', max_age_days=7)
        return True
    except Exception as e:
        logging.error(f"Error en actualización automática: {e}")
        return False

@st.cache_data
def obtener_estado_actualizacion():
    """Obtiene información sobre el estado de actualización de los datos"""
    try:
        updater = get_updater('carreras_universidades.csv')
        return updater.get_update_status()
    except Exception as e:
        logging.error(f"Error obteniendo estado: {e}")
        return {
            'last_update': 'Desconocido',
            'status': 'No disponible',
            'records_count': 0
        }

# Cargar datos
@st.cache_data(ttl=3600)  # Cache por 1 hora
def cargar_datos():
    """Carga el CSV de carreras universitarias con actualización automática"""
    try:
        # Verificar y actualizar datos en background
        verificar_y_actualizar_datos()

        # Cargar datos
        df = pd.read_csv('carreras_universidades.csv')
        return df
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo de datos. Por favor, verifica que 'carreras_universidades.csv' esté en el directorio correcto.")
        return pd.DataFrame()

# Función para generar enlace compartible
def generar_enlace_compartible(carrera, universidad):
    """Genera un enlace corto para compartir en Instagram"""
    carrera_encode = carrera.replace(" ", "-").lower()
    universidad_encode = universidad.replace(" ", "-").lower()
    return f"tu-dominio.com/carrera/{carrera_encode}/{universidad_encode}"

# HEADER minimalista con estado de actualización
update_status = obtener_estado_actualizacion()

# Determinar icono y color según estado
status_icon = "check-circle" if update_status['status'] == 'Actualizado' else "clock"
status_color = "#10B981" if update_status['status'] == 'Actualizado' else "#F59E0B"

st.markdown(f"""
    <div class="header-container">
        <div class="header-content">
            <i data-lucide="graduation-cap" class="header-icon"></i>
            <h1 class="header-title">Buscador de Carreras Universitarias</h1>
        </div>
        <p class="header-subtitle">
            Encuentra la carrera y universidad perfecta para tu futuro
        </p>
        <div class="header-badges">
            <span class="badge badge-country">España</span>
            <span class="badge badge-updated" title="Última actualización: {update_status['last_update']}">
                <i data-lucide="{status_icon}" style="width:14px;height:14px;color:{status_color};"></i>
                {update_status['records_count']} carreras | {update_status['status']}
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Cargar datos
df = cargar_datos()

if df.empty:
    st.stop()

# SIDEBAR - Filtros minimalistas
st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
        <i data-lucide="sliders-horizontal" style="width:24px;height:24px;color:#3B82F6;"></i>
        <h2 style="margin: 0.5rem 0 0.25rem; font-size: 1.125rem; font-weight: 600; color: #171717;">
            Filtros
        </h2>
        <p style="font-size: 0.75rem; color: #737373; margin: 0;">
            Personaliza tu búsqueda
        </p>
    </div>
""", unsafe_allow_html=True)

# Filtro por nombre de carrera
carreras_unicas = sorted(df['nombre_carrera'].unique())
carrera_seleccionada = st.sidebar.selectbox(
    "Carrera",
    options=['Todas'] + carreras_unicas,
    index=0
)

# Filtro por comunidad autónoma
comunidades = sorted(df['comunidad_autonoma'].unique())
comunidad_seleccionada = st.sidebar.multiselect(
    "Comunidad Autónoma",
    options=comunidades,
    default=[],
    placeholder="Selecciona opciones"
)

# Filtro por tipo de universidad
tipo_universidad = st.sidebar.radio(
    "Tipo de universidad",
    options=['Todas', 'Pública', 'Privada'],
    index=0
)

# Filtro por modalidad
modalidad = st.sidebar.radio(
    "Modalidad",
    options=['Todas', 'Presencial', 'A distancia', 'Semipresencial'],
    index=0
)

# Filtro por nota de corte
st.sidebar.subheader("Nota de corte")
min_nota, max_nota = st.sidebar.slider(
    "Rango de nota",
    min_value=float(df['nota_corte'].min()),
    max_value=float(df['nota_corte'].max()),
    value=(float(df['nota_corte'].min()), float(df['nota_corte'].max())),
    step=0.1
)

# Sección de actualización de datos
st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0 0.5rem 0;">
        <i data-lucide="database" style="width:20px;height:20px;color:#3B82F6;"></i>
        <h3 style="margin: 0.5rem 0 0; font-size: 0.875rem; font-weight: 600; color: #171717;">
            Estado de Datos
        </h3>
    </div>
""", unsafe_allow_html=True)

# Mostrar información de actualización
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Registros", update_status['records_count'])
with col2:
    st.metric("Estado", update_status['status'])

st.sidebar.caption(f"📅 Última actualización: {update_status['last_update']}")

# Botón de actualización manual
if st.sidebar.button("🔄 Actualizar Datos", width='stretch'):
    with st.spinner("Actualizando datos..."):
        try:
            updater = get_updater('carreras_universidades.csv')
            success = updater.update_csv(force=True)
            if success:
                st.sidebar.success("✓ Datos actualizados correctamente")
                st.cache_data.clear()
                st.rerun()
            else:
                st.sidebar.warning("⚠ No se pudieron obtener datos frescos. Usando caché.")
        except Exception as e:
            st.sidebar.error(f"❌ Error: {str(e)}")
            logging.error(f"Error en actualización manual: {e}")

# Aplicar filtros
df_filtrado = df.copy()

if carrera_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['nombre_carrera'] == carrera_seleccionada]

if comunidad_seleccionada:
    df_filtrado = df_filtrado[df_filtrado['comunidad_autonoma'].isin(comunidad_seleccionada)]

if tipo_universidad != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['tipo_universidad'] == tipo_universidad]

if modalidad != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['modalidad'] == modalidad]

df_filtrado = df_filtrado[
    (df_filtrado['nota_corte'] >= min_nota) & 
    (df_filtrado['nota_corte'] <= max_nota)
]

# CONTENIDO PRINCIPAL
# Mostrar estadísticas resumidas
st.markdown(f"""
    <div style='text-align: center; margin: 2rem 0 1rem 0;'>
        <h3 style='color: #171717; font-weight: 600; font-size: 1.25rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem;'>
            {icon_inline('bar-chart-4', 24)}Resumen de Resultados
        </h3>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(icon_inline('book-open', 20), unsafe_allow_html=True)
    st.metric("Carreras encontradas", len(df_filtrado))

with col2:
    universidades_unicas = df_filtrado['universidad'].nunique()
    st.markdown(icon_inline('building-2', 20), unsafe_allow_html=True)
    st.metric("Universidades", universidades_unicas)

with col3:
    nota_media = df_filtrado['nota_corte'].mean()
    st.markdown(icon_inline('bar-chart-2', 20), unsafe_allow_html=True)
    st.metric("Nota de corte media", f"{nota_media:.2f}")

with col4:
    plazas_totales = df_filtrado['plazas'].sum()
    st.markdown(icon_inline('users', 20), unsafe_allow_html=True)
    st.metric("Total de plazas", f"{plazas_totales:,}")

st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

# Tabs para diferentes vistas
tab1, tab2, tab3, tab4 = st.tabs(["Listado", "Comparar", "Análisis", "Información"])

with tab1:
    st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0 1.5rem 0;'>
            <h2 style='color: #171717; font-weight: 700;'>
                {icon_inline('clipboard-list', 24)}Resultados de Búsqueda
            </h2>
            <p style='color: #737373; font-size: 0.875rem;'>Explora todas las opciones disponibles</p>
        </div>
    """, unsafe_allow_html=True)

    if len(df_filtrado) == 0:
        st.warning("⚠️ No se encontraron resultados con los filtros seleccionados. Intenta ajustar los criterios.")
    else:
        # Selector de ordenamiento
        orden_col1, orden_col2 = st.columns([1, 3])
        with orden_col1:
            ordenar_por = st.selectbox(
                "Ordenar por:",
                options=['Universidad', 'Nota de corte', 'Plazas', 'Ciudad'],
                help="Selecciona el criterio de ordenamiento"
            )
        
        # Ordenar dataframe
        orden_map = {
            'Universidad': 'universidad',
            'Nota de corte': 'nota_corte',
            'Plazas': 'plazas',
            'Ciudad': 'ciudad'
        }
        df_ordenado = df_filtrado.sort_values(by=orden_map[ordenar_por], ascending=False)
        
        # Mostrar resultados como tarjetas minimalistas
        for idx, row in df_ordenado.iterrows():
            # Estilo de badge según tipo
            tipo_class = 'public' if row['tipo_universidad'] == 'Pública' else 'private'
            tipo_bg = '#D1FAE5' if row['tipo_universidad'] == 'Pública' else '#FEF3C7'
            tipo_border = '#6EE7B7' if row['tipo_universidad'] == 'Pública' else '#FCD34D'
            tipo_color = '#065F46' if row['tipo_universidad'] == 'Pública' else '#92400E'

            with st.expander(
                f"🎓 {row['nombre_carrera']} — {row['universidad']}",
                expanded=False
            ):
                # Badges limpios
                st.markdown(f"""
                    <div style="display: flex; gap: 0.5rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
                        <span style="display: inline-flex; align-items: center; gap: 0.25rem;
                                     padding: 0.375rem 0.75rem; border-radius: 9999px;
                                     font-size: 0.75rem; font-weight: 600;
                                     background: {tipo_bg}; border: 1px solid {tipo_border}; color: {tipo_color};">
                            🏛️ {row['tipo_universidad']}
                        </span>
                        <span style="display: inline-flex; align-items: center; gap: 0.25rem;
                                     padding: 0.375rem 0.75rem; border-radius: 9999px;
                                     font-size: 0.75rem; font-weight: 600;
                                     background: #FAFAFA; border: 1px solid #E5E5E5; color: #171717;">
                            💻 {row['modalidad']}
                        </span>
                    </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"""
                        <h3 style="font-size: 1.25rem; font-weight: 600; color: #171717; margin: 0 0 1rem 0;">
                            {row['universidad']}
                        </h3>
                    """, unsafe_allow_html=True)

                    st.markdown(f"📍 **Ubicación:** {row['ciudad']}, {row['comunidad_autonoma']}")
                    st.markdown(f"🌐 **Idioma:** {row['idioma']}")
                    st.markdown(f"🔗 **Web:** [{row['url_info']}]({row['url_info']})")

                with col2:
                    st.markdown("""
                        <div style='background: #FAFAFA; border: 1px solid #E5E5E5;
                                    border-radius: 0.75rem; padding: 1rem;'>
                            <div style='text-align: center; padding-bottom: 1rem; margin-bottom: 1rem;
                                        border-bottom: 1px solid #E5E5E5;'>
                                <div style='font-size: 0.75rem; font-weight: 600; color: #737373;
                                            text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;'>
                                    Nota de corte
                                </div>
                                <div style='font-size: 2rem; font-weight: 700; color: #3B82F6;'>
                    """, unsafe_allow_html=True)
                    st.markdown(f"{row['nota_corte']}")
                    st.markdown("</div></div>", unsafe_allow_html=True)

                    st.markdown(f"⏱️ {row['duracion_años']} años")
                    st.markdown(f"📖 {row['creditos_ects']} ECTS")
                    st.markdown(f"🪑 {row['plazas']} plazas")
                    st.markdown(f"🎯 {row['rama_conocimiento']}")
                    st.markdown("</div>", unsafe_allow_html=True)

                # Sección de compartir
                st.markdown("---")
                st.markdown(f"#### {icon_inline('share-2', 18)}Compartir", unsafe_allow_html=True)
                enlace = generar_enlace_compartible(row['nombre_carrera'], row['universidad'])
                st.code(enlace, language=None)
                st.caption("Copia este enlace para compartir")

with tab2:
    st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0 2rem 0;'>
            <h2 style='color: #171717; font-weight: 700;'>
                {icon_inline('bar-chart', 24)}Comparador de Universidades
            </h2>
            <p style='color: #737373; font-size: 0.875rem;'>Compara hasta 5 universidades lado a lado</p>
        </div>
    """, unsafe_allow_html=True)

    if len(df_filtrado) < 2:
        st.info("ℹ️ Necesitas al menos 2 opciones para comparar. Ajusta tus filtros.")
    else:
        # Selector de universidades a comparar
        universidades_disponibles = df_filtrado['universidad'].unique().tolist()
        universidades_comparar = st.multiselect(
            "Selecciona universidades para comparar:",
            options=universidades_disponibles,
            max_selections=5,
            help="Puedes seleccionar hasta 5 universidades para comparar",
            placeholder="Elige hasta 5 universidades"
        )

        if universidades_comparar:
            df_comparacion = df_filtrado[df_filtrado['universidad'].isin(universidades_comparar)]

            # Tabla comparativa
            st.markdown(f"### {icon_inline('table', 20)}Tabla Comparativa", unsafe_allow_html=True)
            columnas_mostrar = ['universidad', 'ciudad', 'tipo_universidad', 'nota_corte',
                               'plazas', 'duracion_años', 'modalidad']
            st.dataframe(
                df_comparacion[columnas_mostrar].set_index('universidad'),
                width='stretch',
                height=250
            )

            # Gráficos con diseño mejorado
            col_graf1, col_graf2 = st.columns(2)

            with col_graf1:
                st.markdown(f"### {icon_inline('bar-chart-2', 20)}Notas de Corte", unsafe_allow_html=True)
                fig_notas = px.bar(
                    df_comparacion,
                    x='universidad',
                    y='nota_corte',
                    color='tipo_universidad',
                    title='',
                    labels={'nota_corte': 'Nota de corte', 'universidad': 'Universidad'},
                    color_discrete_map={'Pública': '#10B981', 'Privada': '#F59E0B'},
                    height=400
                )
                fig_notas.update_layout(**CHART_CONFIG)
                fig_notas.update_layout(xaxis_title="", yaxis_title="Nota de corte")
                fig_notas.update_traces(marker_line_width=0)
                st.plotly_chart(fig_notas, width='stretch')

            with col_graf2:
                st.markdown(f"### {icon_inline('users', 20)}Plazas Disponibles", unsafe_allow_html=True)
                fig_plazas = px.bar(
                    df_comparacion,
                    x='universidad',
                    y='plazas',
                    color='tipo_universidad',
                    title='',
                    labels={'plazas': 'Número de plazas', 'universidad': 'Universidad'},
                    color_discrete_map={'Pública': '#10B981', 'Privada': '#F59E0B'},
                    height=400
                )
                fig_plazas.update_layout(**CHART_CONFIG)
                fig_plazas.update_layout(xaxis_title="", yaxis_title="Número de plazas")
                fig_plazas.update_traces(marker_line_width=0)
                st.plotly_chart(fig_plazas, width='stretch')

with tab3:
    st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0 2rem 0;'>
            <h2 style='color: #171717; font-weight: 700;'>
                {icon_inline('trending-up', 24)}Análisis de Datos
            </h2>
            <p style='color: #737373; font-size: 0.875rem;'>Visualiza tendencias y patrones en las carreras</p>
        </div>
    """, unsafe_allow_html=True)

    # Layout en dos columnas para los primeros gráficos
    col_ana1, col_ana2 = st.columns(2)

    with col_ana1:
        # Distribución por rama de conocimiento
        st.markdown(f"### {icon_inline('target', 20)}Por Rama de Conocimiento", unsafe_allow_html=True)
        rama_counts = df_filtrado['rama_conocimiento'].value_counts()
        fig_rama = px.pie(
            values=rama_counts.values,
            names=rama_counts.index,
            title='',
            hole=0.4,
            color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
        )
        fig_rama.update_layout(**CHART_CONFIG)
        fig_rama.update_layout(height=400)
        fig_rama.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_rama, width='stretch')

    with col_ana2:
        # Distribución geográfica
        st.markdown(f"### {icon_inline('map-pin', 20)}Por Comunidad Autónoma", unsafe_allow_html=True)
        comunidad_counts = df_filtrado['comunidad_autonoma'].value_counts().head(10).reset_index()
        comunidad_counts.columns = ['Comunidad Autónoma', 'Número de opciones']
        fig_comunidad = px.bar(
            comunidad_counts,
            x='Comunidad Autónoma',
            y='Número de opciones',
            title='',
            color_discrete_sequence=['#3B82F6']
        )
        fig_comunidad.update_layout(**CHART_CONFIG)
        fig_comunidad.update_layout(
            xaxis_title="",
            yaxis_title="Opciones disponibles",
            showlegend=False,
            height=400
        )
        fig_comunidad.update_traces(marker_line_width=0)
        st.plotly_chart(fig_comunidad, width='stretch')

    # Gráfico de dispersión a ancho completo
    st.markdown(f"### {icon_inline('git-branch', 20)}Relación Nota de Corte vs Plazas", unsafe_allow_html=True)
    fig_scatter = px.scatter(
        df_filtrado,
        x='plazas',
        y='nota_corte',
        color='rama_conocimiento',
        size='duracion_años',
        hover_data=['universidad', 'nombre_carrera'],
        title='',
        labels={'plazas': 'Número de plazas', 'nota_corte': 'Nota de corte'},
        color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'],
        height=500
    )
    fig_scatter.update_layout(**CHART_CONFIG)
    fig_scatter.update_layout(
        xaxis_title="Número de plazas",
        yaxis_title="Nota de corte"
    )
    st.plotly_chart(fig_scatter, width='stretch')

with tab4:
    st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0 2rem 0;'>
            <h2 style='color: #171717; font-weight: 700;'>
                {icon_inline('info', 24)}Información del Buscador
            </h2>
            <p style='color: #737373; font-size: 0.875rem;'>Todo lo que necesitas saber sobre esta herramienta</p>
        </div>
    """, unsafe_allow_html=True)

    # Sección objetivo
    st.markdown(f"""
        <div class='info-box'>
            <h3 style='color: #3B82F6; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;'>
                {icon_inline('target', 20)}Objetivo
            </h3>
            <p style='color: #171717; line-height: 1.8; font-size: 0.9375rem;'>
                Esta herramienta está diseñada para ayudar a <strong>padres y estudiantes</strong>
                a explorar las opciones de carreras universitarias en España de manera sencilla,
                visual e intuitiva. Facilitamos la toma de decisiones con datos actualizados
                y comparativas útiles.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Datos incluidos en dos columnas
    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.markdown(f"""
            <div style='background: #FAFAFA;
                        padding: 1.5rem; border-radius: 0.75rem; border: 1px solid #E5E5E5;
                        height: 100%;'>
                <h3 style='color: #171717; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;'>
                    {icon_inline('database', 20)}Datos Incluidos
                </h3>
                <ul style='color: #171717; line-height: 2; font-size: 0.9375rem; padding-left: 1.25rem;'>
                    <li>Nombre de la carrera</li>
                    <li>Universidad (pública o privada)</li>
                    <li>Ubicación completa</li>
                    <li>Modalidad de estudio</li>
                    <li>Nota de corte</li>
                    <li>Duración y créditos</li>
                    <li>Plazas disponibles</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with col_info2:
        st.markdown(f"""
            <div style='background: #FAFAFA;
                        padding: 1.5rem; border-radius: 0.75rem; border: 1px solid #E5E5E5;
                        height: 100%;'>
                <h3 style='color: #171717; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;'>
                    {icon_inline('compass', 20)}Cómo Usar
                </h3>
                <ol style='color: #171717; line-height: 2; font-size: 0.9375rem; padding-left: 1.25rem;'>
                    <li>Usa los <strong>filtros</strong> de la barra lateral</li>
                    <li>Explora el <strong>listado</strong> de resultados</li>
                    <li><strong>Compara</strong> universidades</li>
                    <li><strong>Analiza</strong> tendencias</li>
                    <li><strong>Comparte</strong> los enlaces</li>
                </ol>
            </div>
        """, unsafe_allow_html=True)

    # Compartir en Instagram
    st.markdown(f"""
        <div style='background: #FEF3C7;
                    padding: 1.5rem; border-radius: 0.75rem; border-left: 3px solid #F59E0B;
                    margin: 1.5rem 0;'>
            <h3 style='color: #171717; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;'>
                {icon_inline('smartphone', 20)}Compartir en Instagram
            </h3>
            <p style='color: #171717; font-size: 0.9375rem;'>
                Cada resultado incluye un enlace corto que puedes copiar y compartir
                en tus stories o mensajes directos de Instagram. ¡Ayuda a otros a encontrar
                su carrera ideal!
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Nota importante
    st.markdown(f"""
        <div style='background: #FEE2E2;
                    padding: 1.5rem; border-radius: 0.75rem; border-left: 3px solid #EF4444;
                    margin: 1.5rem 0;'>
            <h3 style='color: #171717; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;'>
                {icon_inline('alert-triangle', 20)}Nota Importante
            </h3>
            <p style='color: #171717; margin-bottom: 1rem; font-size: 0.9375rem;'>
                Esta es una <strong>herramienta informativa</strong>. Para información
                oficial y actualizada, consulta siempre las fuentes oficiales:
            </p>
            <p style='margin: 0.5rem 0;'>
                <a href='https://www.educacion.gob.es/ruct/home' target='_blank'
                   style='color: #3B82F6; font-weight: 500;'>
                    RUCT - Registro de Universidades, Centros y Títulos
                </a>
            </p>
            <p style='margin: 0.5rem 0;'>
                <a href='https://www.ciencia.gob.es/qedu.html' target='_blank'
                   style='color: #3B82F6; font-weight: 500;'>
                    QEDU - Qué estudiar y dónde en la universidad
                </a>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Próximas mejoras
    st.markdown(f"""
        <div style='background: #F5F3FF;
                    padding: 1.5rem; border-radius: 0.75rem; border-left: 3px solid #8B5CF6;
                    margin: 1.5rem 0;'>
            <h3 style='color: #171717; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;'>
                {icon_inline('lightbulb', 20)}Próximas Mejoras
            </h3>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 1rem; color: #171717; font-size: 0.9375rem;'>
                <div>{icon_inline('briefcase', 16)}Datos de inserción laboral</div>
                <div>{icon_inline('dollar-sign', 16)}Calculadora de becas</div>
                <div>{icon_inline('user', 16)}Testimonios de estudiantes</div>
                <div>{icon_inline('calendar', 16)}Jornadas de puertas abiertas</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
        <div style='text-align: center; padding: 1rem; color: #A3A3A3;'>
            <p style='margin: 0.5rem 0; font-size: 0.875rem;'>
                Última actualización: <strong>{datetime.now().strftime('%d/%m/%Y')}</strong>
            </p>
            <p style='margin: 0.5rem 0; color: #737373; font-size: 0.9375rem;'>
                Desarrollado para ayudar a las familias en la elección universitaria
            </p>
        </div>
    """, unsafe_allow_html=True)

# FOOTER minimalista
st.markdown("---")
st.markdown(f"""
    <div class='footer-section'>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 2rem;'>
            <div>
                <h3 style='font-size: 0.875rem; font-weight: 600; color: #171717;
                           display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;'>
                    {icon_inline('mail', 16)}
                    Contacto
                </h3>
                <p style='font-size: 0.875rem; color: #737373; margin: 0;'>
                    Para sugerencias o reportar datos incorrectos
                </p>
            </div>
            <div>
                <h3 style='font-size: 0.875rem; font-weight: 600; color: #171717;
                           display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;'>
                    {icon_inline('link', 16)}
                    Enlaces Oficiales
                </h3>
                <p style='margin: 0.5rem 0;'>
                    <a href='https://www.educacion.gob.es/ruct/home' target='_blank'
                       style='font-size: 0.875rem; color: #3B82F6; text-decoration: none; font-weight: 500;'>
                        RUCT
                    </a>
                </p>
                <p style='margin: 0.5rem 0;'>
                    <a href='https://www.ciencia.gob.es/qedu.html' target='_blank'
                       style='font-size: 0.875rem; color: #3B82F6; text-decoration: none; font-weight: 500;'>
                        QEDU
                    </a>
                </p>
            </div>
            <div>
                <h3 style='font-size: 0.875rem; font-weight: 600; color: #171717;
                           display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;'>
                    {icon_inline('instagram', 16)}
                    Redes Sociales
                </h3>
                <p style='font-size: 0.875rem; color: #737373; margin: 0;'>
                    Instagram: <strong>@tu_usuario</strong>
                </p>
            </div>
        </div>
        <div style='text-align: center; margin-top: 2rem; padding-top: 2rem;
                    border-top: 1px solid #E5E5E5;'>
            <p style='color: #A3A3A3; font-size: 0.75rem; margin: 0.5rem 0;'>
                Última actualización: {datetime.now().strftime('%d/%m/%Y')}</p>
            <p style='color: #737373; font-size: 0.875rem; margin: 0.5rem 0;'>
                Desarrollado para ayudar a las familias en la elección universitaria
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

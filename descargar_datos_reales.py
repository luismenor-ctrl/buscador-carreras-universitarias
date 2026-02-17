"""
Descarga y combina datos reales de fuentes oficiales españolas con datos sintéticos.

Fuentes reales:
1. Generalitat de Catalunya — notas de corte + plazas (13 universidades, 2023-2024)
   analisi.transparenciacatalunya.cat — Licencia CC BY 4.0
2. Universidad de Murcia — notas de corte por grado (2024-2025)
   datos.um.es — Licencia CC BY-SA 4.0
3. Universidad de Zaragoza — notas de corte cupo general (2024-2025)
   zaguan.unizar.es — Licencia CC BY-NC-SA 4.0

Para las universidades no cubiertas por datos reales, se mantienen los
datos sintéticos generados por generar_datos.py.
"""

import io
import logging
import sys

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 30


# ─────────────────────────────────────────────────────────────────────────────
# MAPAS DE NORMALIZACIÓN
# ─────────────────────────────────────────────────────────────────────────────

# Siglas universidad → datos completos
CATALUÑA_UNIVERSIDADES = {
    "UAB": {
        "nombre": "Universidad Autónoma de Barcelona",
        "tipo": "Pública",
        "ciudad": "Bellaterra",
        "idioma": "Catalán/Español",
        "url": "https://www.uab.cat",
    },
    "UB": {
        "nombre": "Universidad de Barcelona",
        "tipo": "Pública",
        "ciudad": "Barcelona",
        "idioma": "Catalán/Español",
        "url": "https://www.ub.edu",
    },
    "UPC": {
        "nombre": "Universidad Politécnica de Cataluña",
        "tipo": "Pública",
        "ciudad": "Barcelona",
        "idioma": "Catalán/Español",
        "url": "https://www.upc.edu",
    },
    "UPF": {
        "nombre": "Universidad Pompeu Fabra",
        "tipo": "Pública",
        "ciudad": "Barcelona",
        "idioma": "Catalán/Español/Inglés",
        "url": "https://www.upf.edu",
    },
    "UdG": {
        "nombre": "Universidad de Girona",
        "tipo": "Pública",
        "ciudad": "Girona",
        "idioma": "Catalán/Español",
        "url": "https://www.udg.edu",
    },
    "UdL": {
        "nombre": "Universidad de Lleida",
        "tipo": "Pública",
        "ciudad": "Lleida",
        "idioma": "Catalán/Español",
        "url": "https://www.udl.es",
    },
    "URV": {
        "nombre": "Universidad Rovira i Virgili",
        "tipo": "Pública",
        "ciudad": "Tarragona",
        "idioma": "Catalán/Español",
        "url": "https://www.urv.cat",
    },
    "UVic": {
        "nombre": "Universidad de Vic",
        "tipo": "Privada",
        "ciudad": "Vic",
        "idioma": "Catalán/Español",
        "url": "https://www.uvic.cat",
    },
    "UVic-UCC": {
        "nombre": "Universidad de Vic",
        "tipo": "Privada",
        "ciudad": "Vic",
        "idioma": "Catalán/Español",
        "url": "https://www.uvic.cat",
    },
    "UIC": {
        "nombre": "Universidad Internacional de Cataluña",
        "tipo": "Privada",
        "ciudad": "Barcelona",
        "idioma": "Español/Inglés",
        "url": "https://www.uic.es",
    },
    "UOC": {
        "nombre": "Universitat Oberta de Catalunya",
        "tipo": "Pública",
        "ciudad": "Barcelona",
        "idioma": "Catalán/Español",
        "url": "https://www.uoc.edu",
    },
    "URL": {
        "nombre": "Universidad Ramon Llull",
        "tipo": "Privada",
        "ciudad": "Barcelona",
        "idioma": "Catalán/Español/Inglés",
        "url": "https://www.url.edu",
    },
    "UAO": {
        "nombre": "Universidad Abat Oliba CEU",
        "tipo": "Privada",
        "ciudad": "Barcelona",
        "idioma": "Español/Catalán",
        "url": "https://www.uao.es",
    },
}

# Traducciones de nombres en catalán → español
TRADUCCIONES_CAT = {
    "Administració i Direcció d'Empreses": "Grado en Administración y Dirección de Empresas",
    "Arquitectura": "Grado en Arquitectura",
    "Arquitectura Tècnica": "Grado en Arquitectura Técnica",
    "Biologia": "Grado en Biología",
    "Biologia Humana": "Grado en Biología Humana",
    "Bioquímica": "Grado en Bioquímica",
    "Biotecnologia": "Grado en Biotecnología",
    "Ciència i Enginyeria de Dades": "Grado en Ciencia e Ingeniería de Datos",
    "Ciències Ambientals": "Grado en Ciencias Ambientales",
    "Ciències Polítiques i de l'Administració": "Grado en Ciencias Políticas y de la Administración",
    "Cinema": "Grado en Cine",
    "Comunicació Audiovisual": "Grado en Comunicación Audiovisual",
    "Criminologia": "Grado en Criminología",
    "Dret": "Grado en Derecho",
    "Disseny": "Grado en Diseño",
    "Economia": "Grado en Economía",
    "Educació Primària": "Grado en Educación Primaria",
    "Educació Social": "Grado en Educación Social",
    "Enginyeria Agroalimentària i del Medi Rural": "Grado en Ingeniería Agroalimentaria",
    "Enginyeria Biomèdica": "Grado en Ingeniería Biomédica",
    "Enginyeria Civil": "Grado en Ingeniería Civil",
    "Enginyeria de Sistemes de Telecomunicació": "Grado en Ingeniería de Telecomunicaciones",
    "Enginyeria de Tecnologia i Disseny Tèxtil": "Grado en Ingeniería de Diseño Textil",
    "Enginyeria Elèctrica": "Grado en Ingeniería Eléctrica",
    "Enginyeria Electrònica Industrial i Automàtica": "Grado en Ingeniería Electrónica Industrial",
    "Enginyeria en Tecnologies Industrials": "Grado en Ingeniería en Tecnologías Industriales",
    "Enginyeria Física": "Grado en Ingeniería Física",
    "Enginyeria Informàtica": "Grado en Ingeniería Informática",
    "Enginyeria Mecànica": "Grado en Ingeniería Mecánica",
    "Enginyeria Química": "Grado en Ingeniería Química",
    "Estudis d'Anglès i Català": "Grado en Estudios Ingleses y Catalán",
    "Estudis d'Anglès i Espanyol": "Grado en Estudios Ingleses y Español",
    "Farmàcia": "Grado en Farmacia",
    "Filologia Catalana": "Grado en Filología Catalana",
    "Filologia Hispànica": "Grado en Filología Hispánica",
    "Filosofia": "Grado en Filosofía",
    "Física": "Grado en Física",
    "Fisioteràpia": "Grado en Fisioterapia",
    "Gastronomia": "Grado en Gastronomía",
    "Geografia i Medi Ambient": "Grado en Geografía y Medio Ambiente",
    "Gestió i Administració Pública": "Grado en Gestión y Administración Pública",
    "Història": "Grado en Historia",
    "Història de l'Art": "Grado en Historia del Arte",
    "Humanitats": "Grado en Humanidades",
    "Infermeria": "Grado en Enfermería",
    "Informació i Documentació": "Grado en Información y Documentación",
    "Logopèdia": "Grado en Logopedia",
    "Matemàtiques": "Grado en Matemáticas",
    "Medicina": "Grado en Medicina",
    "Mestre d'Educació Infantil": "Grado en Magisterio de Educación Infantil",
    "Mestre d'Educació Primària": "Grado en Magisterio de Educación Primaria",
    "Nanociència i Nanotecnologia": "Grado en Nanociencia y Nanotecnología",
    "Nutrició Humana i Dietètica": "Grado en Nutrición y Dietética",
    "Odontologia": "Grado en Odontología",
    "Pedagogia": "Grado en Pedagogía",
    "Periodisme": "Grado en Periodismo",
    "Psicologia": "Grado en Psicología",
    "Publicitat i Relacions Públiques": "Grado en Publicidad y Relaciones Públicas",
    "Química": "Grado en Química",
    "Relacions Internacionals": "Grado en Relaciones Internacionales",
    "Relacions Laborals": "Grado en Relaciones Laborales y Recursos Humanos",
    "Sociologia": "Grado en Sociología",
    "Teologia": "Grado en Teología",
    "Terapia Ocupacional": "Grado en Terapia Ocupacional",
    "Traducció i Interpretació": "Grado en Traducción e Interpretación",
    "Treball Social": "Grado en Trabajo Social",
    "Turisme": "Grado en Turismo",
    "Veterinària": "Grado en Veterinaria",
}

# Rama de conocimiento por titulación (nombre normalizado en español)
RAMAS = {
    "Grado en Administración y Dirección de Empresas": "Ciencias Sociales y Jurídicas",
    "Grado en Arquitectura": "Ingeniería y Arquitectura",
    "Grado en Arquitectura Técnica": "Ingeniería y Arquitectura",
    "Grado en Biología": "Ciencias",
    "Grado en Biología Humana": "Ciencias de la Salud",
    "Grado en Bioquímica": "Ciencias",
    "Grado en Biotecnología": "Ciencias",
    "Grado en Ciencia e Ingeniería de Datos": "Ingeniería y Arquitectura",
    "Grado en Ciencias Ambientales": "Ciencias",
    "Grado en Ciencias Políticas y de la Administración": "Ciencias Sociales y Jurídicas",
    "Grado en Cine": "Artes y Humanidades",
    "Grado en Comunicación Audiovisual": "Ciencias Sociales y Jurídicas",
    "Grado en Criminología": "Ciencias Sociales y Jurídicas",
    "Grado en Derecho": "Ciencias Sociales y Jurídicas",
    "Grado en Diseño": "Artes y Humanidades",
    "Grado en Economía": "Ciencias Sociales y Jurídicas",
    "Grado en Educación Primaria": "Ciencias Sociales y Jurídicas",
    "Grado en Educación Social": "Ciencias Sociales y Jurídicas",
    "Grado en Enfermería": "Ciencias de la Salud",
    "Grado en Farmacia": "Ciencias de la Salud",
    "Grado en Filología Hispánica": "Artes y Humanidades",
    "Grado en Filosofía": "Artes y Humanidades",
    "Grado en Física": "Ciencias",
    "Grado en Fisioterapia": "Ciencias de la Salud",
    "Grado en Gastronomía": "Ciencias Sociales y Jurídicas",
    "Grado en Geografía y Medio Ambiente": "Ciencias",
    "Grado en Gestión y Administración Pública": "Ciencias Sociales y Jurídicas",
    "Grado en Historia": "Artes y Humanidades",
    "Grado en Historia del Arte": "Artes y Humanidades",
    "Grado en Humanidades": "Artes y Humanidades",
    "Grado en Información y Documentación": "Ciencias Sociales y Jurídicas",
    "Grado en Ingeniería Agroalimentaria": "Ingeniería y Arquitectura",
    "Grado en Ingeniería Biomédica": "Ingeniería y Arquitectura",
    "Grado en Ingeniería Civil": "Ingeniería y Arquitectura",
    "Grado en Ingeniería de Diseño Textil": "Ingeniería y Arquitectura",
    "Grado en Ingeniería de Telecomunicaciones": "Ingeniería y Arquitectura",
    "Grado en Ingeniería Eléctrica": "Ingeniería y Arquitectura",
    "Grado en Ingeniería Electrónica Industrial": "Ingeniería y Arquitectura",
    "Grado en Ingeniería en Tecnologías Industriales": "Ingeniería y Arquitectura",
    "Grado en Ingeniería Física": "Ingeniería y Arquitectura",
    "Grado en Ingeniería Informática": "Ingeniería y Arquitectura",
    "Grado en Ingeniería Mecánica": "Ingeniería y Arquitectura",
    "Grado en Ingeniería Química": "Ingeniería y Arquitectura",
    "Grado en Logopedia": "Ciencias de la Salud",
    "Grado en Magisterio de Educación Infantil": "Ciencias Sociales y Jurídicas",
    "Grado en Magisterio de Educación Primaria": "Ciencias Sociales y Jurídicas",
    "Grado en Matemáticas": "Ciencias",
    "Grado en Medicina": "Ciencias de la Salud",
    "Grado en Nanociencia y Nanotecnología": "Ciencias",
    "Grado en Nutrición y Dietética": "Ciencias de la Salud",
    "Grado en Odontología": "Ciencias de la Salud",
    "Grado en Pedagogía": "Ciencias Sociales y Jurídicas",
    "Grado en Periodismo": "Ciencias Sociales y Jurídicas",
    "Grado en Psicología": "Ciencias de la Salud",
    "Grado en Publicidad y Relaciones Públicas": "Ciencias Sociales y Jurídicas",
    "Grado en Química": "Ciencias",
    "Grado en Relaciones Internacionales": "Ciencias Sociales y Jurídicas",
    "Grado en Relaciones Laborales y Recursos Humanos": "Ciencias Sociales y Jurídicas",
    "Grado en Sociología": "Ciencias Sociales y Jurídicas",
    "Grado en Terapia Ocupacional": "Ciencias de la Salud",
    "Grado en Traducción e Interpretación": "Artes y Humanidades",
    "Grado en Trabajo Social": "Ciencias Sociales y Jurídicas",
    "Grado en Turismo": "Ciencias Sociales y Jurídicas",
    "Grado en Veterinaria": "Ciencias de la Salud",
}

# Duración (años) y ECTS por titulación
DURACION_ECTS = {
    "Grado en Arquitectura": (5, 300),
    "Grado en Farmacia": (5, 300),
    "Grado en Medicina": (6, 360),
    "Grado en Odontología": (5, 300),
    "Grado en Veterinaria": (5, 300),
}
DURACION_DEFAULT = (4, 240)

# Municipio catalán → nombre en español
MUNICIPIOS_CAT = {
    "Cerdanyola del Vallès": "Cerdanyola del Vallès",
    "Bellaterra": "Bellaterra",
    "Barcelona": "Barcelona",
    "Girona": "Girona",
    "Lleida": "Lleida",
    "Tarragona": "Tarragona",
    "Vic": "Vic",
    "Manresa": "Manresa",
    "Igualada": "Igualada",
    "Mataró": "Mataró",
    "Terrassa": "Terrassa",
    "Reus": "Reus",
    "Vilanova i la Geltrú": "Vilanova i la Geltrú",
    "Sabadell": "Sabadell",
}


# ─────────────────────────────────────────────────────────────────────────────
# DESCARGADORES
# ─────────────────────────────────────────────────────────────────────────────

def descargar_cataluna() -> pd.DataFrame:
    """
    Generalitat de Catalunya: notas de corte y plazas por titulación y universidad.
    Cubre: UAB, UB, UPC, UPF, UdG, UdL, URV, UVic, UOC, UIC, URL, UAO.
    """
    url = "https://analisi.transparenciacatalunya.cat/api/views/usyn-hngc/rows.csv?accessType=DOWNLOAD"
    logger.info("Descargando Cataluña...")
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.content.decode("utf-8-sig")))

    # Renombrar columnas para evitar problemas con apóstrofes especiales (U+2019)
    df.columns = [
        "curs", "any", "codi", "nom_oferta",
        "tipus_estudi", "sigles_univ", "via_acces",
        "nota_tall", "municipi", "num_places"
    ]

    # Filtrar solo el año más reciente y solo Graus
    df = df[df["tipus_estudi"] == "Grau"].copy()
    anyo_max = df["any"].max()
    df = df[df["any"] == anyo_max].copy()

    # Filtrar solo vía PAU (acceso desde bachillerato)
    df = df[df["via_acces"].str.contains("Pau|pau|PAU", na=False)].copy()

    rows = []
    for _, row in df.iterrows():
        sigles = row["sigles_univ"]
        if sigles not in CATALUÑA_UNIVERSIDADES:
            continue
        univ_data = CATALUÑA_UNIVERSIDADES[sigles]

        # Nombre en catalán → español
        nom_cat = str(row["nom_oferta"]).strip()
        nom_es = TRADUCCIONES_CAT.get(nom_cat)
        if nom_es is None:
            # Intento genérico: añadir "Grado en" si no está traducido
            nom_es = f"Grado en {nom_cat.capitalize()}"

        nota = float(row["nota_tall"]) if pd.notna(row["nota_tall"]) else None
        plazas = int(row["num_places"]) if pd.notna(row["num_places"]) else None
        if nota is None or nota < 5.0:
            continue

        duracion, ects = DURACION_ECTS.get(nom_es, DURACION_DEFAULT)
        rama = RAMAS.get(nom_es, "Ciencias Sociales y Jurídicas")

        rows.append({
            "nombre_carrera": nom_es,
            "universidad": univ_data["nombre"],
            "tipo_universidad": univ_data["tipo"],
            "ciudad": row["municipi"],
            "comunidad_autonoma": "Cataluña",
            "modalidad": "Presencial",
            "duracion_años": duracion,
            "creditos_ects": ects,
            "rama_conocimiento": rama,
            "nota_corte": round(nota, 3),
            "plazas": plazas or 80,
            "idioma": univ_data["idioma"],
            "url_info": univ_data["url"],
            "fuente": "Generalitat de Catalunya (analisi.transparenciacatalunya.cat)",
            "curso": f"{anyo_max}-{anyo_max + 1}",
        })

    result = pd.DataFrame(rows)
    logger.info(f"  Cataluña: {len(result)} filas, {result['universidad'].nunique()} universidades")
    return result


def descargar_murcia() -> pd.DataFrame:
    """
    Universidad de Murcia: notas de corte por grado 2024-2025.
    """
    url = "https://datos.um.es/public/nota-corte-grado-2024-2025/csv"
    logger.info("Descargando Murcia...")
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.content.decode("utf-8-sig")), sep=",")

    univ_data = {
        "nombre": "Universidad de Murcia",
        "tipo": "Pública",
        "ciudad": "Murcia",
        "comunidad": "Región de Murcia",
        "idioma": "Español",
        "url": "https://www.um.es",
    }

    rows = []
    for _, row in df.iterrows():
        titulacion = str(row["titulacion"]).strip()
        if not titulacion.lower().startswith("grado"):
            titulacion = f"Grado en {titulacion.capitalize()}"

        nota = float(str(row["nota_corte"]).replace(",", ".")) if pd.notna(row["nota_corte"]) else None
        if nota is None or nota < 5.0:
            continue

        duracion, ects = DURACION_ECTS.get(titulacion, DURACION_DEFAULT)
        rama = RAMAS.get(titulacion, "Ciencias Sociales y Jurídicas")

        rows.append({
            "nombre_carrera": titulacion,
            "universidad": univ_data["nombre"],
            "tipo_universidad": univ_data["tipo"],
            "ciudad": univ_data["ciudad"],
            "comunidad_autonoma": univ_data["comunidad"],
            "modalidad": "Presencial",
            "duracion_años": duracion,
            "creditos_ects": ects,
            "rama_conocimiento": rama,
            "nota_corte": round(nota, 3),
            "plazas": 80,
            "idioma": univ_data["idioma"],
            "url_info": univ_data["url"],
            "fuente": "Universidad de Murcia (datos.um.es)",
            "curso": "2024-2025",
        })

    result = pd.DataFrame(rows).drop_duplicates("nombre_carrera")
    logger.info(f"  Murcia: {len(result)} filas")
    return result


def descargar_zaragoza() -> pd.DataFrame:
    """
    Universidad de Zaragoza: notas de corte cupo general 2024-2025.
    """
    url = "https://zaguan.unizar.es/record/148071/files/CSV.csv"
    logger.info("Descargando Zaragoza...")
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()

    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            df = pd.read_csv(io.StringIO(r.content.decode(enc)), sep=None, engine="python")
            break
        except Exception:
            continue

    rows = []
    for _, row in df.iterrows():
        raw = str(row["ESTUDIO"]).strip()
        # Normalizar: "Grado: Medicina" → "Grado en Medicina"
        if raw.lower().startswith("grado:"):
            titulacion = "Grado en " + raw[6:].strip().capitalize()
        elif raw.lower().startswith("grado en"):
            titulacion = raw.capitalize()
        else:
            titulacion = f"Grado en {raw.capitalize()}"

        nota = row["NOTA_CORTE_DEFINITIVA_JULIO"]
        if pd.isna(nota):
            nota = row.get("NOTA_CORTE_DEFINITIVA_SEPTIEMBRE", None)
        if pd.isna(nota) or float(nota) < 5.0:
            continue

        ciudad = str(row.get("LOCALIDAD", "Zaragoza")).strip()
        if pd.isna(ciudad) or ciudad == "nan":
            ciudad = "Zaragoza"

        duracion, ects = DURACION_ECTS.get(titulacion, DURACION_DEFAULT)
        rama = RAMAS.get(titulacion, "Ciencias Sociales y Jurídicas")

        rows.append({
            "nombre_carrera": titulacion,
            "universidad": "Universidad de Zaragoza",
            "tipo_universidad": "Pública",
            "ciudad": ciudad,
            "comunidad_autonoma": "Aragón",
            "modalidad": "Presencial",
            "duracion_años": duracion,
            "creditos_ects": ects,
            "rama_conocimiento": rama,
            "nota_corte": round(float(nota), 3),
            "plazas": 80,
            "idioma": "Español",
            "url_info": "https://www.unizar.es",
            "fuente": "Universidad de Zaragoza (zaguan.unizar.es)",
            "curso": "2024-2025",
        })

    result = pd.DataFrame(rows).drop_duplicates("nombre_carrera")
    logger.info(f"  Zaragoza: {len(result)} filas")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# COMBINACIÓN CON DATOS SINTÉTICOS
# ─────────────────────────────────────────────────────────────────────────────

def combinar_con_sinteticos(df_real: pd.DataFrame) -> pd.DataFrame:
    """
    Carga los datos sintéticos y los combina con los datos reales.
    Los datos reales tienen prioridad (sustituyen al sintético si coincide
    nombre_carrera + universidad).
    """
    logger.info("Cargando datos sintéticos base...")
    try:
        df_sint = pd.read_csv("carreras_universidades.csv", encoding="utf-8")
    except FileNotFoundError:
        logger.warning("No se encontró carreras_universidades.csv, generando sintéticos...")
        import subprocess
        subprocess.run([sys.executable, "generar_datos.py"], check=True)
        df_sint = pd.read_csv("carreras_universidades.csv", encoding="utf-8")

    # Universidades cubiertas por datos reales → excluir del sintético
    universidades_reales = set(df_real["universidad"].unique())
    df_sint_filtered = df_sint[~df_sint["universidad"].isin(universidades_reales)].copy()
    df_sint_filtered["fuente"] = "Sintético (generar_datos.py)"
    df_sint_filtered["curso"] = "2024-2025"

    logger.info(
        f"  Sintéticos restantes: {len(df_sint_filtered)} filas "
        f"({df_sint_filtered['universidad'].nunique()} universidades no cubiertas)"
    )

    combined = pd.concat([df_real, df_sint_filtered], ignore_index=True)
    combined = combined.drop_duplicates(subset=["nombre_carrera", "universidad"])
    combined = combined.sort_values(
        ["rama_conocimiento", "nombre_carrera", "universidad"]
    ).reset_index(drop=True)

    return combined


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    logger.info("=" * 60)
    logger.info("DESCARGA DE DATOS REALES DE UNIVERSIDADES ESPAÑOLAS")
    logger.info("=" * 60)

    dfs_reales = []

    # Cataluña
    try:
        dfs_reales.append(descargar_cataluna())
    except Exception as e:
        logger.error(f"Error descargando Cataluña: {e}")

    # Murcia
    try:
        dfs_reales.append(descargar_murcia())
    except Exception as e:
        logger.error(f"Error descargando Murcia: {e}")

    # Zaragoza
    try:
        dfs_reales.append(descargar_zaragoza())
    except Exception as e:
        logger.error(f"Error descargando Zaragoza: {e}")

    if not dfs_reales:
        logger.error("No se pudieron descargar datos reales. Abortando.")
        return

    df_real = pd.concat(dfs_reales, ignore_index=True)
    df_real = df_real.drop_duplicates(subset=["nombre_carrera", "universidad"])
    logger.info(
        f"\nDatos reales combinados: {len(df_real)} filas, "
        f"{df_real['universidad'].nunique()} universidades"
    )

    # Combinar con sintéticos
    df_final = combinar_con_sinteticos(df_real)

    # Guardar
    output = "carreras_universidades.csv"
    df_final.to_csv(output, index=False, encoding="utf-8")
    logger.info(f"\n{'=' * 60}")
    logger.info(f"RESULTADO FINAL: {output}")
    logger.info(f"  Total filas:       {len(df_final)}")
    logger.info(f"  Carreras únicas:   {df_final['nombre_carrera'].nunique()}")
    logger.info(f"  Universidades:     {df_final['universidad'].nunique()}")
    logger.info(f"\n  Por fuente:")
    for fuente, cnt in df_final["fuente"].value_counts().items():
        logger.info(f"    {fuente[:60]:60} {cnt:5} filas")
    logger.info(f"\n  Por comunidad autónoma:")
    for ccaa, cnt in df_final["comunidad_autonoma"].value_counts().head(10).items():
        logger.info(f"    {ccaa:30} {cnt:5}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

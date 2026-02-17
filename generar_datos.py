"""
Genera dataset completo de carreras universitarias en España.
Basado en datos reales de universidades y titulaciones españolas.
Objetivo: ~900-1000 entradas cubriendo las 17 comunidades autónomas.
"""
import pandas as pd
import random

random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSIDADES
# ─────────────────────────────────────────────────────────────────────────────

UNIVERSIDADES = {
    # Andalucía
    "Universidad de Sevilla": {
        "tipo": "Pública", "ciudad": "Sevilla", "comunidad": "Andalucía",
        "url": "https://www.us.es", "idioma": "Español"
    },
    "Universidad de Granada": {
        "tipo": "Pública", "ciudad": "Granada", "comunidad": "Andalucía",
        "url": "https://www.ugr.es", "idioma": "Español"
    },
    "Universidad de Málaga": {
        "tipo": "Pública", "ciudad": "Málaga", "comunidad": "Andalucía",
        "url": "https://www.uma.es", "idioma": "Español"
    },
    "Universidad de Córdoba": {
        "tipo": "Pública", "ciudad": "Córdoba", "comunidad": "Andalucía",
        "url": "https://www.uco.es", "idioma": "Español"
    },
    "Universidad de Jaén": {
        "tipo": "Pública", "ciudad": "Jaén", "comunidad": "Andalucía",
        "url": "https://www.ujaen.es", "idioma": "Español"
    },
    "Universidad de Almería": {
        "tipo": "Pública", "ciudad": "Almería", "comunidad": "Andalucía",
        "url": "https://www.ual.es", "idioma": "Español"
    },
    "Universidad de Cádiz": {
        "tipo": "Pública", "ciudad": "Cádiz", "comunidad": "Andalucía",
        "url": "https://www.uca.es", "idioma": "Español"
    },
    "Universidad de Huelva": {
        "tipo": "Pública", "ciudad": "Huelva", "comunidad": "Andalucía",
        "url": "https://www.uhu.es", "idioma": "Español"
    },
    "Universidad Pablo de Olavide": {
        "tipo": "Pública", "ciudad": "Sevilla", "comunidad": "Andalucía",
        "url": "https://www.upo.es", "idioma": "Español"
    },
    "Universidad Loyola Andalucía": {
        "tipo": "Privada", "ciudad": "Sevilla", "comunidad": "Andalucía",
        "url": "https://www.uloyola.es", "idioma": "Español/Inglés"
    },
    # Aragón
    "Universidad de Zaragoza": {
        "tipo": "Pública", "ciudad": "Zaragoza", "comunidad": "Aragón",
        "url": "https://www.unizar.es", "idioma": "Español"
    },
    "Universidad San Jorge": {
        "tipo": "Privada", "ciudad": "Zaragoza", "comunidad": "Aragón",
        "url": "https://www.usj.es", "idioma": "Español/Inglés"
    },
    # Asturias
    "Universidad de Oviedo": {
        "tipo": "Pública", "ciudad": "Oviedo", "comunidad": "Asturias",
        "url": "https://www.uniovi.es", "idioma": "Español"
    },
    # Islas Baleares
    "Universidad de las Islas Baleares": {
        "tipo": "Pública", "ciudad": "Palma de Mallorca", "comunidad": "Islas Baleares",
        "url": "https://www.uib.es", "idioma": "Catalán/Español"
    },
    # Islas Canarias
    "Universidad de Las Palmas de Gran Canaria": {
        "tipo": "Pública", "ciudad": "Las Palmas de G.C.", "comunidad": "Islas Canarias",
        "url": "https://www.ulpgc.es", "idioma": "Español"
    },
    "Universidad de La Laguna": {
        "tipo": "Pública", "ciudad": "San Cristóbal de La Laguna", "comunidad": "Islas Canarias",
        "url": "https://www.ull.es", "idioma": "Español"
    },
    # Cantabria
    "Universidad de Cantabria": {
        "tipo": "Pública", "ciudad": "Santander", "comunidad": "Cantabria",
        "url": "https://www.unican.es", "idioma": "Español"
    },
    # Castilla-La Mancha
    "Universidad de Castilla-La Mancha": {
        "tipo": "Pública", "ciudad": "Ciudad Real", "comunidad": "Castilla-La Mancha",
        "url": "https://www.uclm.es", "idioma": "Español"
    },
    # Castilla y León
    "Universidad de Salamanca": {
        "tipo": "Pública", "ciudad": "Salamanca", "comunidad": "Castilla y León",
        "url": "https://www.usal.es", "idioma": "Español"
    },
    "Universidad de Valladolid": {
        "tipo": "Pública", "ciudad": "Valladolid", "comunidad": "Castilla y León",
        "url": "https://www.uva.es", "idioma": "Español"
    },
    "Universidad de Burgos": {
        "tipo": "Pública", "ciudad": "Burgos", "comunidad": "Castilla y León",
        "url": "https://www.ubu.es", "idioma": "Español"
    },
    "Universidad de León": {
        "tipo": "Pública", "ciudad": "León", "comunidad": "Castilla y León",
        "url": "https://www.unileon.es", "idioma": "Español"
    },
    "IE University": {
        "tipo": "Privada", "ciudad": "Segovia", "comunidad": "Castilla y León",
        "url": "https://www.ie.edu", "idioma": "Español/Inglés"
    },
    # Cataluña
    "Universidad de Barcelona": {
        "tipo": "Pública", "ciudad": "Barcelona", "comunidad": "Cataluña",
        "url": "https://www.ub.edu", "idioma": "Catalán/Español"
    },
    "Universidad Autónoma de Barcelona": {
        "tipo": "Pública", "ciudad": "Bellaterra", "comunidad": "Cataluña",
        "url": "https://www.uab.cat", "idioma": "Catalán/Español"
    },
    "Universidad Politécnica de Cataluña": {
        "tipo": "Pública", "ciudad": "Barcelona", "comunidad": "Cataluña",
        "url": "https://www.upc.edu", "idioma": "Catalán/Español"
    },
    "Universidad Pompeu Fabra": {
        "tipo": "Pública", "ciudad": "Barcelona", "comunidad": "Cataluña",
        "url": "https://www.upf.edu", "idioma": "Catalán/Español/Inglés"
    },
    "Universidad de Girona": {
        "tipo": "Pública", "ciudad": "Girona", "comunidad": "Cataluña",
        "url": "https://www.udg.edu", "idioma": "Catalán/Español"
    },
    "Universidad de Lleida": {
        "tipo": "Pública", "ciudad": "Lleida", "comunidad": "Cataluña",
        "url": "https://www.udl.es", "idioma": "Catalán/Español"
    },
    "Universidad Rovira i Virgili": {
        "tipo": "Pública", "ciudad": "Tarragona", "comunidad": "Cataluña",
        "url": "https://www.urv.cat", "idioma": "Catalán/Español"
    },
    "Universidad Internacional de Cataluña": {
        "tipo": "Privada", "ciudad": "Barcelona", "comunidad": "Cataluña",
        "url": "https://www.uic.es", "idioma": "Español/Inglés"
    },
    # Extremadura
    "Universidad de Extremadura": {
        "tipo": "Pública", "ciudad": "Badajoz", "comunidad": "Extremadura",
        "url": "https://www.unex.es", "idioma": "Español"
    },
    # Galicia
    "Universidad de Santiago de Compostela": {
        "tipo": "Pública", "ciudad": "Santiago de Compostela", "comunidad": "Galicia",
        "url": "https://www.usc.gal", "idioma": "Gallego/Español"
    },
    "Universidad de Vigo": {
        "tipo": "Pública", "ciudad": "Vigo", "comunidad": "Galicia",
        "url": "https://www.uvigo.gal", "idioma": "Gallego/Español"
    },
    "Universidad de A Coruña": {
        "tipo": "Pública", "ciudad": "A Coruña", "comunidad": "Galicia",
        "url": "https://www.udc.es", "idioma": "Gallego/Español"
    },
    # La Rioja
    "Universidad de La Rioja": {
        "tipo": "Pública", "ciudad": "Logroño", "comunidad": "La Rioja",
        "url": "https://www.unirioja.es", "idioma": "Español"
    },
    # Madrid
    "Universidad Complutense de Madrid": {
        "tipo": "Pública", "ciudad": "Madrid", "comunidad": "Comunidad de Madrid",
        "url": "https://www.ucm.es", "idioma": "Español"
    },
    "Universidad Autónoma de Madrid": {
        "tipo": "Pública", "ciudad": "Madrid", "comunidad": "Comunidad de Madrid",
        "url": "https://www.uam.es", "idioma": "Español"
    },
    "Universidad Politécnica de Madrid": {
        "tipo": "Pública", "ciudad": "Madrid", "comunidad": "Comunidad de Madrid",
        "url": "https://www.upm.es", "idioma": "Español/Inglés"
    },
    "Universidad Carlos III de Madrid": {
        "tipo": "Pública", "ciudad": "Getafe", "comunidad": "Comunidad de Madrid",
        "url": "https://www.uc3m.es", "idioma": "Español/Inglés"
    },
    "Universidad Rey Juan Carlos": {
        "tipo": "Pública", "ciudad": "Móstoles", "comunidad": "Comunidad de Madrid",
        "url": "https://www.urjc.es", "idioma": "Español"
    },
    "Universidad de Alcalá": {
        "tipo": "Pública", "ciudad": "Alcalá de Henares", "comunidad": "Comunidad de Madrid",
        "url": "https://www.uah.es", "idioma": "Español"
    },
    "Universidad Pontificia Comillas": {
        "tipo": "Privada", "ciudad": "Madrid", "comunidad": "Comunidad de Madrid",
        "url": "https://www.comillas.edu", "idioma": "Español/Inglés"
    },
    "Universidad CEU San Pablo": {
        "tipo": "Privada", "ciudad": "Madrid", "comunidad": "Comunidad de Madrid",
        "url": "https://www.uspceu.com", "idioma": "Español/Inglés"
    },
    "Universidad Francisco de Vitoria": {
        "tipo": "Privada", "ciudad": "Madrid", "comunidad": "Comunidad de Madrid",
        "url": "https://www.ufv.es", "idioma": "Español/Inglés"
    },
    "Universidad Nebrija": {
        "tipo": "Privada", "ciudad": "Madrid", "comunidad": "Comunidad de Madrid",
        "url": "https://www.nebrija.es", "idioma": "Español/Inglés"
    },
    "Universidad Alfonso X el Sabio": {
        "tipo": "Privada", "ciudad": "Villanueva de la Cañada", "comunidad": "Comunidad de Madrid",
        "url": "https://www.uax.es", "idioma": "Español"
    },
    # Murcia
    "Universidad de Murcia": {
        "tipo": "Pública", "ciudad": "Murcia", "comunidad": "Región de Murcia",
        "url": "https://www.um.es", "idioma": "Español"
    },
    "Universidad Politécnica de Cartagena": {
        "tipo": "Pública", "ciudad": "Cartagena", "comunidad": "Región de Murcia",
        "url": "https://www.upct.es", "idioma": "Español"
    },
    "Universidad Católica de Murcia (UCAM)": {
        "tipo": "Privada", "ciudad": "Murcia", "comunidad": "Región de Murcia",
        "url": "https://www.ucam.edu", "idioma": "Español/Inglés"
    },
    # Navarra
    "Universidad de Navarra": {
        "tipo": "Privada", "ciudad": "Pamplona", "comunidad": "Navarra",
        "url": "https://www.unav.edu", "idioma": "Español/Inglés"
    },
    "Universidad Pública de Navarra": {
        "tipo": "Pública", "ciudad": "Pamplona", "comunidad": "Navarra",
        "url": "https://www.unavarra.es", "idioma": "Español/Vasco"
    },
    # País Vasco
    "Universidad del País Vasco": {
        "tipo": "Pública", "ciudad": "Bilbao", "comunidad": "País Vasco",
        "url": "https://www.ehu.eus", "idioma": "Vasco/Español"
    },
    "Universidad de Deusto": {
        "tipo": "Privada", "ciudad": "Bilbao", "comunidad": "País Vasco",
        "url": "https://www.deusto.es", "idioma": "Español/Inglés"
    },
    "Universidad de Mondragón": {
        "tipo": "Privada", "ciudad": "Mondragón", "comunidad": "País Vasco",
        "url": "https://www.mondragon.edu", "idioma": "Vasco/Español"
    },
    # Comunidad Valenciana
    "Universidad de Valencia": {
        "tipo": "Pública", "ciudad": "Valencia", "comunidad": "Comunidad Valenciana",
        "url": "https://www.uv.es", "idioma": "Valenciano/Español"
    },
    "Universidad Politécnica de Valencia": {
        "tipo": "Pública", "ciudad": "Valencia", "comunidad": "Comunidad Valenciana",
        "url": "https://www.upv.es", "idioma": "Valenciano/Español"
    },
    "Universidad de Alicante": {
        "tipo": "Pública", "ciudad": "Alicante", "comunidad": "Comunidad Valenciana",
        "url": "https://www.ua.es", "idioma": "Valenciano/Español"
    },
    "Universidad Jaume I": {
        "tipo": "Pública", "ciudad": "Castellón de la Plana", "comunidad": "Comunidad Valenciana",
        "url": "https://www.uji.es", "idioma": "Valenciano/Español"
    },
    "Universidad Miguel Hernández": {
        "tipo": "Pública", "ciudad": "Elche", "comunidad": "Comunidad Valenciana",
        "url": "https://www.umh.es", "idioma": "Valenciano/Español"
    },
    "Universidad CEU Cardenal Herrera": {
        "tipo": "Privada", "ciudad": "Valencia", "comunidad": "Comunidad Valenciana",
        "url": "https://www.uchceu.es", "idioma": "Español"
    },
    "Universidad Católica de Valencia": {
        "tipo": "Privada", "ciudad": "Valencia", "comunidad": "Comunidad Valenciana",
        "url": "https://www.ucv.es", "idioma": "Español"
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# TITULACIONES POR RAMA
# Formato: (nombre, duración_años, créditos_ects, nota_base, nota_max, plazas_base, plazas_max, modalidades)
# ─────────────────────────────────────────────────────────────────────────────

TITULACIONES = {
    "Artes y Humanidades": [
        ("Grado en Historia", 4, 240, 7.5, 10.5, 80, 200, ["Presencial"]),
        ("Grado en Historia del Arte", 4, 240, 8.0, 11.0, 60, 180, ["Presencial"]),
        ("Grado en Filosofía", 4, 240, 7.5, 10.5, 50, 120, ["Presencial"]),
        ("Grado en Filología Hispánica", 4, 240, 7.5, 10.5, 60, 150, ["Presencial"]),
        ("Grado en Filología Inglesa", 4, 240, 8.0, 11.5, 60, 160, ["Presencial"]),
        ("Grado en Lengua y Literatura Españolas", 4, 240, 7.5, 10.0, 50, 130, ["Presencial"]),
        ("Grado en Estudios Ingleses", 4, 240, 8.0, 11.5, 60, 160, ["Presencial"]),
        ("Grado en Traducción e Interpretación", 4, 240, 9.0, 12.0, 60, 120, ["Presencial"]),
        ("Grado en Bellas Artes", 4, 240, 8.5, 12.0, 50, 120, ["Presencial"]),
        ("Grado en Arqueología", 4, 240, 7.5, 10.5, 40, 100, ["Presencial"]),
        ("Grado en Musicología", 4, 240, 7.5, 11.0, 30, 80, ["Presencial"]),
        ("Grado en Humanidades", 4, 240, 7.0, 10.0, 50, 150, ["Presencial", "Online"]),
        ("Grado en Estudios Árabes e Islámicos", 4, 240, 7.5, 10.5, 30, 80, ["Presencial"]),
        ("Grado en Comunicación Cultural", 4, 240, 7.5, 10.5, 40, 100, ["Presencial"]),
        ("Grado en Lenguas Modernas", 4, 240, 8.0, 11.5, 50, 130, ["Presencial"]),
        ("Grado en Gestión del Patrimonio Cultural", 4, 240, 7.5, 10.5, 40, 100, ["Presencial"]),
    ],
    "Ciencias": [
        ("Grado en Matemáticas", 4, 240, 9.0, 12.5, 80, 200, ["Presencial"]),
        ("Grado en Física", 4, 240, 9.5, 12.5, 60, 150, ["Presencial"]),
        ("Grado en Química", 4, 240, 9.0, 12.0, 80, 180, ["Presencial"]),
        ("Grado en Biología", 4, 240, 9.0, 12.0, 80, 200, ["Presencial"]),
        ("Grado en Geología", 4, 240, 8.5, 11.5, 50, 120, ["Presencial"]),
        ("Grado en Bioquímica", 4, 240, 10.0, 13.0, 60, 120, ["Presencial"]),
        ("Grado en Biotecnología", 4, 240, 10.5, 13.5, 60, 120, ["Presencial"]),
        ("Grado en Estadística", 4, 240, 9.0, 12.0, 50, 100, ["Presencial"]),
        ("Grado en Ciencias Ambientales", 4, 240, 8.5, 11.5, 60, 150, ["Presencial"]),
        ("Grado en Ciencias del Mar", 4, 240, 9.0, 12.0, 50, 100, ["Presencial"]),
        ("Grado en Ciencias de la Computación", 4, 240, 10.0, 13.0, 60, 150, ["Presencial"]),
        ("Grado en Matemáticas y Estadística", 4, 240, 9.5, 12.5, 50, 100, ["Presencial"]),
        ("Grado en Nanociencia y Nanotecnología", 4, 240, 9.5, 13.0, 40, 80, ["Presencial"]),
        ("Grado en Óptica y Optometría", 4, 240, 8.5, 11.5, 40, 80, ["Presencial"]),
    ],
    "Ciencias de la Salud": [
        ("Grado en Medicina", 6, 360, 12.5, 13.9, 120, 250, ["Presencial"]),
        ("Grado en Enfermería", 4, 240, 8.0, 11.5, 80, 250, ["Presencial"]),
        ("Grado en Farmacia", 5, 300, 10.5, 13.0, 80, 180, ["Presencial"]),
        ("Grado en Odontología", 5, 300, 11.5, 13.5, 60, 120, ["Presencial"]),
        ("Grado en Fisioterapia", 4, 240, 10.0, 12.5, 60, 120, ["Presencial"]),
        ("Grado en Veterinaria", 5, 300, 10.5, 13.0, 80, 150, ["Presencial"]),
        ("Grado en Psicología", 4, 240, 9.0, 12.0, 100, 300, ["Presencial", "Online"]),
        ("Grado en Nutrición y Dietética", 4, 240, 9.0, 12.0, 50, 120, ["Presencial"]),
        ("Grado en Terapia Ocupacional", 4, 240, 8.0, 11.0, 40, 80, ["Presencial"]),
        ("Grado en Logopedia", 4, 240, 9.0, 12.0, 40, 80, ["Presencial"]),
        ("Grado en Podología", 4, 240, 7.5, 10.5, 30, 60, ["Presencial"]),
        ("Grado en Trabajo Social", 4, 240, 7.5, 10.0, 60, 150, ["Presencial", "Online"]),
        ("Grado en Ciencias de la Actividad Física y del Deporte", 4, 240, 9.0, 12.0, 60, 150, ["Presencial"]),
        ("Grado en Radiología e Imagen Médica", 4, 240, 9.0, 11.5, 40, 80, ["Presencial"]),
        ("Grado en Biología Sanitaria", 4, 240, 9.5, 12.5, 40, 80, ["Presencial"]),
    ],
    "Ciencias Sociales y Jurídicas": [
        ("Grado en Derecho", 4, 240, 9.0, 12.0, 150, 400, ["Presencial", "Online"]),
        ("Grado en Administración y Dirección de Empresas", 4, 240, 9.5, 12.5, 150, 400, ["Presencial", "Online"]),
        ("Grado en Economía", 4, 240, 9.5, 12.5, 100, 300, ["Presencial"]),
        ("Grado en Contabilidad y Finanzas", 4, 240, 8.5, 11.5, 80, 200, ["Presencial"]),
        ("Grado en Marketing", 4, 240, 9.0, 12.0, 80, 200, ["Presencial"]),
        ("Grado en Relaciones Laborales y Recursos Humanos", 4, 240, 8.0, 11.0, 80, 200, ["Presencial", "Online"]),
        ("Grado en Educación Primaria", 4, 240, 8.5, 11.5, 80, 250, ["Presencial"]),
        ("Grado en Educación Infantil", 4, 240, 8.5, 11.5, 80, 200, ["Presencial"]),
        ("Grado en Pedagogía", 4, 240, 8.0, 11.0, 60, 150, ["Presencial"]),
        ("Grado en Periodismo", 4, 240, 9.0, 12.0, 80, 200, ["Presencial"]),
        ("Grado en Comunicación Audiovisual", 4, 240, 9.0, 12.0, 60, 150, ["Presencial"]),
        ("Grado en Publicidad y Relaciones Públicas", 4, 240, 8.5, 11.5, 60, 150, ["Presencial"]),
        ("Grado en Turismo", 4, 240, 7.5, 10.5, 60, 150, ["Presencial"]),
        ("Grado en Ciencias Políticas y de la Administración", 4, 240, 9.0, 12.0, 60, 150, ["Presencial"]),
        ("Grado en Sociología", 4, 240, 8.0, 11.0, 60, 150, ["Presencial"]),
        ("Grado en Criminología", 4, 240, 8.5, 12.0, 60, 150, ["Presencial"]),
        ("Grado en Relaciones Internacionales", 4, 240, 10.0, 13.0, 60, 150, ["Presencial"]),
        ("Grado en Doble Grado en Derecho y ADE", 4, 300, 11.0, 13.5, 50, 120, ["Presencial"]),
        ("Grado en Finanzas y Contabilidad", 4, 240, 9.0, 12.0, 60, 150, ["Presencial"]),
        ("Grado en Gestión y Administración Pública", 4, 240, 8.0, 11.0, 50, 120, ["Presencial", "Online"]),
        ("Grado en Educación Social", 4, 240, 7.5, 10.5, 60, 150, ["Presencial"]),
        ("Grado en Magisterio de Educación Primaria", 4, 240, 8.5, 11.5, 80, 200, ["Presencial"]),
        ("Grado en Magisterio de Educación Infantil", 4, 240, 8.5, 11.5, 80, 200, ["Presencial"]),
        ("Grado en Información y Documentación", 4, 240, 7.5, 10.5, 40, 100, ["Presencial", "Online"]),
    ],
    "Ingeniería y Arquitectura": [
        ("Grado en Ingeniería Informática", 4, 240, 10.5, 13.5, 150, 350, ["Presencial", "Online"]),
        ("Grado en Ingeniería Civil", 4, 240, 9.0, 12.0, 100, 250, ["Presencial"]),
        ("Grado en Ingeniería Mecánica", 4, 240, 9.5, 12.5, 100, 250, ["Presencial"]),
        ("Grado en Ingeniería Eléctrica", 4, 240, 8.5, 11.5, 80, 200, ["Presencial"]),
        ("Grado en Ingeniería Electrónica Industrial", 4, 240, 9.0, 12.0, 80, 200, ["Presencial"]),
        ("Grado en Ingeniería Química", 4, 240, 9.0, 12.0, 80, 200, ["Presencial"]),
        ("Grado en Ingeniería Aeroespacial", 4, 240, 12.0, 13.9, 60, 120, ["Presencial"]),
        ("Grado en Ingeniería de Telecomunicaciones", 4, 240, 10.0, 13.0, 100, 250, ["Presencial"]),
        ("Grado en Ingeniería Biomédica", 4, 240, 11.0, 13.5, 50, 100, ["Presencial"]),
        ("Grado en Ingeniería de Materiales", 4, 240, 9.0, 12.0, 50, 100, ["Presencial"]),
        ("Grado en Arquitectura", 5, 300, 11.0, 13.5, 80, 180, ["Presencial"]),
        ("Grado en Ingeniería Industrial", 4, 240, 10.0, 13.0, 100, 250, ["Presencial"]),
        ("Grado en Ingeniería Agrónoma", 4, 240, 8.5, 11.5, 60, 150, ["Presencial"]),
        ("Grado en Ingeniería Naval y Oceánica", 4, 240, 9.0, 12.0, 40, 100, ["Presencial"]),
        ("Grado en Ingeniería de Sistemas de Información", 4, 240, 10.0, 12.5, 80, 200, ["Presencial"]),
        ("Grado en Ingeniería Ambiental", 4, 240, 9.0, 12.0, 60, 150, ["Presencial"]),
        ("Grado en Ingeniería de Minas y Energía", 4, 240, 8.5, 11.5, 50, 120, ["Presencial"]),
        ("Grado en Ingeniería Electrónica de Telecomunicaciones", 4, 240, 9.5, 12.5, 80, 200, ["Presencial"]),
        ("Grado en Ingeniería Robótica", 4, 240, 10.5, 13.0, 50, 100, ["Presencial"]),
        ("Grado en Diseño Industrial y Desarrollo del Producto", 4, 240, 9.0, 12.0, 50, 100, ["Presencial"]),
        ("Grado en Ingeniería de Organización Industrial", 4, 240, 9.0, 12.0, 80, 200, ["Presencial"]),
        ("Grado en Ciencias e Ingeniería de Datos", 4, 240, 11.0, 13.5, 60, 150, ["Presencial"]),
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# MAPEO UNIVERSIDAD → TITULACIONES OFERTADAS
# Para evitar duplicados irreales (p.ej. ingeniería aeroespacial en universidades pequeñas)
# ─────────────────────────────────────────────────────────────────────────────

# Universidades politécnicas y técnicas
POLITECNICAS = {
    "Universidad Politécnica de Madrid",
    "Universidad Politécnica de Cataluña",
    "Universidad Politécnica de Valencia",
    "Universidad Politécnica de Cartagena",
}

# Universidades con medicina
CON_MEDICINA = {
    "Universidad Complutense de Madrid", "Universidad Autónoma de Madrid",
    "Universidad de Barcelona", "Universidad Autónoma de Barcelona",
    "Universidad de Valencia", "Universidad de Granada", "Universidad de Sevilla",
    "Universidad de Santiago de Compostela", "Universidad del País Vasco",
    "Universidad de Salamanca", "Universidad de Valladolid", "Universidad de Oviedo",
    "Universidad de Zaragoza", "Universidad de La Laguna", "Universidad de Murcia",
    "Universidad de Málaga", "Universidad de Córdoba", "Universidad de Cádiz",
    "Universidad de Extremadura", "Universidad de Alicante", "Universidad Jaume I",
    "Universidad Miguel Hernández", "Universidad de Navarra", "Universidad de Deusto",
    "Universidad CEU San Pablo", "Universidad de Castilla-La Mancha",
    "Universidad Francisco de Vitoria", "Universidad Loyola Andalucía",
    "Universidad CEU Cardenal Herrera", "Universidad Católica de Valencia",
    "Universidad de Cantabria", "Universidad Rey Juan Carlos",
    "Universidad de Las Palmas de Gran Canaria",
}

# Titulaciones NO ofrecidas por politécnicas
NO_EN_POLITECNICAS = {
    "Grado en Historia", "Grado en Historia del Arte", "Grado en Filosofía",
    "Grado en Filología Hispánica", "Grado en Filología Inglesa",
    "Grado en Traducción e Interpretación", "Grado en Arqueología",
    "Grado en Musicología", "Grado en Humanidades",
    "Grado en Derecho", "Grado en Sociología", "Grado en Pedagogía",
    "Grado en Periodismo", "Grado en Comunicación Audiovisual",
    "Grado en Publicidad y Relaciones Públicas",
    "Grado en Ciencias Políticas y de la Administración",
    "Grado en Relaciones Internacionales",
    "Grado en Medicina", "Grado en Farmacia", "Grado en Odontología",
    "Grado en Veterinaria", "Grado en Logopedia", "Grado en Terapia Ocupacional",
    "Grado en Podología",
    "Grado en Biología", "Grado en Física", "Grado en Química", "Grado en Matemáticas",
    "Grado en Geología", "Grado en Biotecnología", "Grado en Bioquímica",
}

# Titulaciones SOLO en politécnicas o técnicas
SOLO_EN_POLITECNICAS = {
    "Grado en Arquitectura",
    "Grado en Ingeniería Aeroespacial",
    "Grado en Ingeniería Naval y Oceánica",
    "Grado en Ingeniería de Minas y Energía",
}

# Titulaciones raras (sólo en algunas universidades grandes)
TITULACIONES_RARAS = {
    "Grado en Musicología": 0.3,
    "Grado en Arqueología": 0.4,
    "Grado en Estudios Árabes e Islámicos": 0.25,
    "Grado en Nanociencia y Nanotecnología": 0.3,
    "Grado en Ciencias del Mar": 0.35,
    "Grado en Ingeniería Biomédica": 0.35,
    "Grado en Ingeniería Robótica": 0.3,
    "Grado en Ingeniería Naval y Oceánica": 0.2,
    "Grado en Ingeniería de Minas y Energía": 0.25,
    "Grado en Doble Grado en Derecho y ADE": 0.4,
    "Grado en Biología Sanitaria": 0.3,
    "Grado en Radiología e Imagen Médica": 0.35,
    "Grado en Gestión del Patrimonio Cultural": 0.3,
    "Grado en Comunicación Cultural": 0.3,
}


def nota_corte_para(tit_nombre, nota_base, nota_max, univ_nombre):
    """Calcula nota de corte realista según universidad y titulación."""
    nota = round(random.uniform(nota_base, nota_max), 1)
    # Prestigio extra para ciertas universidades
    universidades_top = {
        "Universidad Complutense de Madrid", "Universidad Autónoma de Madrid",
        "Universidad de Barcelona", "Universidad Pompeu Fabra",
        "Universidad Politécnica de Madrid", "Universidad Politécnica de Cataluña",
        "Universidad Carlos III de Madrid", "Universidad de Navarra",
        "Universidad de Salamanca", "Universidad del País Vasco",
        "IE University",
    }
    if univ_nombre in universidades_top:
        nota = min(13.9, nota + random.uniform(0.3, 0.8))
        nota = round(nota, 1)
    return nota


def puede_ofertarse(tit_nombre, univ_nombre, univ_data):
    """Determina si una universidad puede ofertar esta titulación."""
    es_politecnica = univ_nombre in POLITECNICAS

    if es_politecnica and tit_nombre in NO_EN_POLITECNICAS:
        return False
    if not es_politecnica and tit_nombre in SOLO_EN_POLITECNICAS:
        return False
    if tit_nombre in {"Grado en Medicina", "Grado en Odontología", "Grado en Veterinaria"}:
        return univ_nombre in CON_MEDICINA
    if tit_nombre in TITULACIONES_RARAS:
        prob = TITULACIONES_RARAS[tit_nombre]
        return random.random() < prob
    return True


def generar_dataset():
    filas = []

    for univ_nombre, univ_data in UNIVERSIDADES.items():
        for rama, titulaciones in TITULACIONES.items():
            for tit in titulaciones:
                nombre, duracion, ects, nota_min, nota_max, plazas_min, plazas_max, modalidades = tit

                if not puede_ofertarse(nombre, univ_nombre, univ_data):
                    continue

                # Algunas universidades no ofrecen todas las modalidades
                modalidad = random.choice(modalidades)

                # Calcular nota de corte
                nota = nota_corte_para(nombre, nota_min, nota_max, univ_nombre)

                # Plazas
                plazas = random.randint(plazas_min, plazas_max)
                # Ajustar plazas: universidades privadas tienen menos plazas
                if univ_data["tipo"] == "Privada":
                    plazas = max(20, int(plazas * 0.6))
                # Redondear a múltiplos de 5
                plazas = round(plazas / 5) * 5

                filas.append({
                    "nombre_carrera": nombre,
                    "universidad": univ_nombre,
                    "tipo_universidad": univ_data["tipo"],
                    "ciudad": univ_data["ciudad"],
                    "comunidad_autonoma": univ_data["comunidad"],
                    "modalidad": modalidad,
                    "duracion_años": duracion,
                    "creditos_ects": ects,
                    "rama_conocimiento": rama,
                    "nota_corte": nota,
                    "plazas": plazas,
                    "idioma": univ_data["idioma"],
                    "url_info": univ_data["url"],
                })

    df = pd.DataFrame(filas)

    # Eliminar duplicados exactos
    df = df.drop_duplicates(subset=["nombre_carrera", "universidad"])

    # Ordenar
    df = df.sort_values(["rama_conocimiento", "nombre_carrera", "universidad"]).reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = generar_dataset()
    df.to_csv("carreras_universidades.csv", index=False, encoding="utf-8")

    print(f"Total filas: {len(df)}")
    print(f"Carreras únicas: {df['nombre_carrera'].nunique()}")
    print(f"Universidades únicas: {df['universidad'].nunique()}")
    print(f"\nPor rama:")
    print(df["rama_conocimiento"].value_counts().to_string())
    print(f"\nPor comunidad autónoma:")
    print(df["comunidad_autonoma"].value_counts().to_string())
    print(f"\nPor tipo:")
    print(df["tipo_universidad"].value_counts().to_string())
    print(f"\nPor modalidad:")
    print(df["modalidad"].value_counts().to_string())

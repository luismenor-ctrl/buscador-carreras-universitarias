"""
Sistema de actualización automática de datos universitarios
Fuentes: QEDU, RUCT, páginas oficiales de universidades
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional
import hashlib
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataUpdater:
    """
    Gestor de actualización automática de datos universitarios
    """

    def __init__(self, csv_path: str, cache_dir: str = '.cache'):
        self.csv_path = Path(csv_path)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # TTL (Time To Live) para diferentes tipos de datos
        self.ttl = {
            'metadata': timedelta(hours=6),      # Info general actualizada cada 6h
            'nota_corte': timedelta(days=1),     # Notas de corte diarias
            'plazas': timedelta(days=7),         # Plazas semanales
            'full_data': timedelta(days=30)      # Datos completos mensuales
        }

        # Headers para requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
        }

        # URLs oficiales
        self.sources = {
            'qedu': 'https://www.ciencia.gob.es/qedu.html',
            'ruct': 'https://www.educacion.gob.es/ruct/home',
            'universidades_publicas': [
                'https://www.upm.es',
                'https://www.ucm.es',
                'https://www.upc.edu',
                'https://www.ub.edu',
                'https://www.uam.es'
            ]
        }

    def _get_cache_path(self, key: str) -> Path:
        """Genera ruta de caché para una clave"""
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.pkl"

    def _is_cache_valid(self, cache_path: Path, ttl: timedelta) -> bool:
        """Verifica si la caché es válida según el TTL"""
        if not cache_path.exists():
            return False

        mod_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - mod_time < ttl

    def _save_cache(self, key: str, data: any):
        """Guarda datos en caché"""
        cache_path = self._get_cache_path(key)
        with open(cache_path, 'wb') as f:
            pickle.dump({
                'timestamp': datetime.now(),
                'data': data
            }, f)
        logger.info(f"Caché guardada: {key}")

    def _load_cache(self, key: str) -> Optional[any]:
        """Carga datos desde caché"""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'rb') as f:
                cached = pickle.load(f)
                return cached['data']
        except Exception as e:
            logger.error(f"Error cargando caché {key}: {e}")
            return None

    def fetch_qedu_data(self) -> Optional[pd.DataFrame]:
        """
        Obtiene datos del sistema QEDU (Qué Estudiar y Dónde en la Universidad)
        Fuente oficial del Ministerio de Ciencia e Innovación
        """
        cache_key = 'qedu_data'
        cache_path = self._get_cache_path(cache_key)

        # Verificar caché
        if self._is_cache_valid(cache_path, self.ttl['full_data']):
            logger.info("Usando datos QEDU desde caché")
            return self._load_cache(cache_key)

        try:
            logger.info("Obteniendo datos frescos de QEDU...")

            # QEDU tiene una API interna que podemos usar
            api_url = "https://www.educacion.gob.es/notasdecorte/busquedaSimple.action"

            # Parámetros para buscar todas las titulaciones
            params = {
                'codTipoEstudio': '',  # Vacío para obtener todos
                'tipoEstudioDesc': 'GRADO',
                'curso': '2025'  # Año actual
            }

            response = requests.post(api_url, data=params, headers=self.headers, timeout=30)

            if response.status_code == 200:
                # Parsear respuesta (depende del formato real de QEDU)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Aquí iría el parsing específico basado en la estructura real
                # Por ahora, retornamos None para implementar fallback
                logger.warning("Parsing de QEDU pendiente de implementación completa")
                return None

        except Exception as e:
            logger.error(f"Error obteniendo datos de QEDU: {e}")
            return None

    def fetch_university_data(self, university_url: str) -> Dict:
        """
        Obtiene datos actualizados de la página oficial de una universidad
        """
        cache_key = f'univ_{university_url}'
        cache_path = self._get_cache_path(cache_key)

        if self._is_cache_valid(cache_path, self.ttl['metadata']):
            return self._load_cache(cache_key)

        try:
            response = requests.get(university_url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extraer información relevante
                data = {
                    'url': university_url,
                    'timestamp': datetime.now().isoformat(),
                    'accessible': True
                }

                self._save_cache(cache_key, data)
                return data

        except Exception as e:
            logger.error(f"Error accediendo a {university_url}: {e}")
            return {'url': university_url, 'accessible': False}

    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida y limpia los datos obtenidos
        """
        logger.info("Validando datos...")

        # Copiar dataframe para no modificar el original
        df_clean = df.copy()

        # Validaciones básicas
        validations = {
            'nota_corte': lambda x: 5.0 <= x <= 14.0,  # Rango válido en España
            'duracion_años': lambda x: 1 <= x <= 6,    # Grados de 3-4 años, algunos 5-6
            'creditos_ects': lambda x: 60 <= x <= 480, # Min 60 ECTS/año, max 8 años
            'plazas': lambda x: x > 0                   # Debe haber al menos 1 plaza
        }

        # Aplicar validaciones
        for col, validation_fn in validations.items():
            if col in df_clean.columns:
                invalid_mask = ~df_clean[col].apply(validation_fn)
                invalid_count = invalid_mask.sum()

                if invalid_count > 0:
                    logger.warning(f"Encontradas {invalid_count} filas con {col} inválido")
                    # Marcar como NaN valores inválidos
                    df_clean.loc[invalid_mask, col] = pd.NA

        # Eliminar duplicados
        before_dedup = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['nombre_carrera', 'universidad'])
        after_dedup = len(df_clean)

        if before_dedup != after_dedup:
            logger.info(f"Eliminados {before_dedup - after_dedup} duplicados")

        # Validar URLs
        if 'url_info' in df_clean.columns:
            url_pattern = r'^https?://'
            invalid_urls = ~df_clean['url_info'].str.match(url_pattern, na=False)
            if invalid_urls.any():
                logger.warning(f"Encontradas {invalid_urls.sum()} URLs inválidas")

        logger.info(f"Validación completada: {len(df_clean)} registros válidos")
        return df_clean

    def enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriquece los datos existentes con información adicional
        """
        logger.info("Enriqueciendo datos...")

        df_enriched = df.copy()

        # Agregar timestamp de última actualización
        df_enriched['ultima_actualizacion'] = datetime.now().strftime('%Y-%m-%d')

        # Agregar campo de validación de URL
        df_enriched['url_verificada'] = False

        # Verificar URLs en paralelo (más rápido)
        urls = df_enriched['url_info'].unique()
        logger.info(f"Verificando {len(urls)} URLs únicas...")

        verified_urls = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {
                executor.submit(self._verify_url, url): url
                for url in urls
            }

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    verified_urls[url] = future.result()
                except Exception as e:
                    logger.error(f"Error verificando {url}: {e}")
                    verified_urls[url] = False

        # Aplicar verificaciones
        df_enriched['url_verificada'] = df_enriched['url_info'].map(verified_urls)

        logger.info(f"Enriquecimiento completado")
        return df_enriched

    def _verify_url(self, url: str, timeout: int = 5) -> bool:
        """Verifica si una URL es accesible"""
        try:
            response = requests.head(url, headers=self.headers, timeout=timeout, allow_redirects=True)
            return response.status_code < 400
        except:
            return False

    def update_csv(self, force: bool = False) -> bool:
        """
        Actualiza el CSV principal con datos frescos

        Args:
            force: Si True, ignora la caché y fuerza actualización

        Returns:
            True si la actualización fue exitosa
        """
        logger.info("="*60)
        logger.info("INICIANDO ACTUALIZACIÓN DE DATOS")
        logger.info("="*60)

        try:
            # 1. Cargar datos actuales
            if not self.csv_path.exists():
                logger.error(f"CSV no encontrado: {self.csv_path}")
                return False

            df_current = pd.read_csv(self.csv_path)
            logger.info(f"Datos actuales: {len(df_current)} registros")

            # Crear backup
            backup_path = self.csv_path.with_suffix('.backup.csv')
            df_current.to_csv(backup_path, index=False)
            logger.info(f"Backup creado: {backup_path}")

            # 2. Intentar obtener datos frescos de QEDU
            df_fresh = None
            if force or not self._is_cache_valid(
                self._get_cache_path('qedu_data'),
                self.ttl['full_data']
            ):
                df_fresh = self.fetch_qedu_data()

            # 3. Si no hay datos frescos, enriquecer los actuales
            if df_fresh is None:
                logger.info("No hay datos frescos disponibles, enriqueciendo datos actuales...")
                df_updated = self.enrich_data(df_current)
            else:
                logger.info(f"Datos frescos obtenidos: {len(df_fresh)} registros")
                # Combinar datos frescos con actuales
                df_updated = pd.concat([df_current, df_fresh]).drop_duplicates(
                    subset=['nombre_carrera', 'universidad'],
                    keep='last'
                )

            # 4. Validar datos
            df_validated = self.validate_data(df_updated)

            # 5. Guardar datos actualizados
            df_validated.to_csv(self.csv_path, index=False)
            logger.info(f"CSV actualizado: {len(df_validated)} registros")

            # 6. Guardar metadata de actualización
            metadata = {
                'last_update': datetime.now().isoformat(),
                'records_count': len(df_validated),
                'source': 'qedu' if df_fresh is not None else 'enrichment',
                'success': True
            }
            self._save_cache('last_update_metadata', metadata)

            logger.info("="*60)
            logger.info("ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
            logger.info("="*60)

            return True

        except Exception as e:
            logger.error(f"Error durante la actualización: {e}", exc_info=True)

            # Restaurar backup en caso de error
            if backup_path.exists():
                logger.info("Restaurando backup...")
                df_current.to_csv(self.csv_path, index=False)

            return False

    def get_update_status(self) -> Dict:
        """
        Obtiene información sobre el estado de las actualizaciones
        """
        metadata = self._load_cache('last_update_metadata')

        if metadata is None:
            return {
                'last_update': 'Nunca',
                'records_count': 0,
                'status': 'No disponible'
            }

        last_update = datetime.fromisoformat(metadata['last_update'])
        time_since = datetime.now() - last_update

        return {
            'last_update': last_update.strftime('%Y-%m-%d %H:%M:%S'),
            'time_since': str(time_since).split('.')[0],  # Remover microsegundos
            'records_count': metadata['records_count'],
            'source': metadata.get('source', 'unknown'),
            'status': 'Actualizado' if time_since < timedelta(days=7) else 'Desactualizado'
        }

    def schedule_updates(self, interval_hours: int = 24):
        """
        Configura actualizaciones automáticas periódicas

        Args:
            interval_hours: Intervalo entre actualizaciones en horas
        """
        import threading

        def update_loop():
            while True:
                logger.info(f"Ejecutando actualización programada...")
                self.update_csv()
                logger.info(f"Próxima actualización en {interval_hours} horas")
                time.sleep(interval_hours * 3600)

        # Iniciar hilo en background
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        logger.info(f"Actualizaciones automáticas iniciadas (cada {interval_hours}h)")

        return thread


# Funciones de conveniencia para usar en Streamlit
def get_updater(csv_path: str = 'carreras_universidades.csv') -> DataUpdater:
    """Factory function para obtener instancia del updater"""
    return DataUpdater(csv_path)

def check_and_update_if_needed(csv_path: str = 'carreras_universidades.csv',
                                max_age_days: int = 7) -> bool:
    """
    Verifica si los datos están desactualizados y actualiza si es necesario

    Args:
        csv_path: Ruta al CSV
        max_age_days: Edad máxima de los datos en días

    Returns:
        True si los datos están actualizados
    """
    updater = get_updater(csv_path)
    status = updater.get_update_status()

    if status['status'] == 'Desactualizado':
        logger.info("Datos desactualizados, iniciando actualización...")
        return updater.update_csv()

    logger.info("Datos actualizados, no es necesaria actualización")
    return True


if __name__ == "__main__":
    # Script de prueba
    updater = DataUpdater('carreras_universidades.csv')

    print("\n" + "="*60)
    print("SISTEMA DE ACTUALIZACIÓN DE DATOS UNIVERSITARIOS")
    print("="*60 + "\n")

    # Mostrar estado actual
    status = updater.get_update_status()
    print("Estado actual:")
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n¿Desea ejecutar una actualización? (s/n): ", end='')
    if input().lower() == 's':
        success = updater.update_csv()
        if success:
            print("\n✓ Actualización completada exitosamente")
        else:
            print("\n✗ Error durante la actualización")

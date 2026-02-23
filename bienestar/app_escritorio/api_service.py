import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class APIClient:
    BASE_URL = "http://127.0.0.1:8000"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.access_token  = None
        self.refresh_token = None

    # ── Helpers ───────────────────────────────────
    def _get(self, endpoint: str) -> list | dict:
        """Hace GET y maneja errores de red de forma centralizada."""
        url = f"{self.BASE_URL}{endpoint}"
        try:
            r = self.session.get(url, timeout=10)
            logger.debug(f"GET {endpoint} → {r.status_code}")
            r.raise_for_status()
            return r.json()
        except requests.exceptions.ConnectionError:
            raise Exception("No se pudo conectar al servidor.")
        except requests.exceptions.Timeout:
            raise Exception("El servidor tardó demasiado en responder.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Sesión expirada. Por favor inicia sesión nuevamente.")
            raise Exception(f"Error del servidor: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error de red: {str(e)}")

    # ── Autenticación ─────────────────────────────
    def login(self, email: str, password: str) -> bool:
        url  = f"{self.BASE_URL}/api/token/"
        data = {"email": email, "password": password}
        try:
            r = self.session.post(url, json=data, timeout=10)
            logger.debug(f"Login STATUS: {r.status_code}")

            if r.status_code == 200:
                tokens = r.json()
                self.access_token  = tokens["access"]
                self.refresh_token = tokens["refresh"]
                self.session.headers["Authorization"] = f"Bearer {self.access_token}"
                logger.debug("Login exitoso, token guardado en sesión")
                return True
            elif r.status_code == 401:
                return False
            else:
                logger.error(f"Error inesperado en login: {r.status_code}")
                return False

        except requests.exceptions.ConnectionError:
            raise Exception("No se pudo conectar al servidor. ¿Está Django corriendo?")
        except requests.exceptions.Timeout:
            raise Exception("El servidor tardó demasiado en responder.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error de red: {str(e)}")

    def logout(self):
        self.access_token  = None
        self.refresh_token = None
        self.session.headers.pop("Authorization", None)
        logger.debug("Sesión cerrada")

    # ── Emociones (catálogo) ──────────────────────
    def get_emociones(self) -> list:
        return self._get("/api/emociones/")

    # ── Alumnos ───────────────────────────────────
    def get_alumnos(self) -> list:
        """Lista resumida de todos los alumnos."""
        return self._get("/api/alumnos/")

    def get_alumno_perfil(self, alumno_id: int) -> dict:
        """Perfil completo de un alumno."""
        return self._get(f"/api/alumnos/{alumno_id}/perfil/")

    def get_alumno_emociones(self, alumno_id: int) -> list:
        """Historial de emociones de un alumno."""
        return self._get(f"/api/alumnos/{alumno_id}/emociones/")

    def get_alumno_habitos(self, alumno_id: int) -> list:
        """Historial de hábitos de un alumno."""
        return self._get(f"/api/alumnos/{alumno_id}/habitos/")

    def get_alumno_diario(self, alumno_id: int) -> list:
        """Entradas del diario de un alumno."""
        return self._get(f"/api/alumnos/{alumno_id}/diario/")

    def get_alumno_notas(self, alumno_id: int) -> list:
        """Notas del psicólogo sobre un alumno."""
        return self._get(f"/api/alumnos/{alumno_id}/notas/")

    def crear_nota(self, alumno_id: int, contenido: str) -> dict:
        """Crea una nueva nota del psicólogo sobre un alumno."""
        url  = f"{self.BASE_URL}/api/alumnos/{alumno_id}/notas/"
        try:
            r = self.session.post(url, json={"contenido": contenido}, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.ConnectionError:
            raise Exception("No se pudo conectar al servidor.")
        except requests.exceptions.Timeout:
            raise Exception("El servidor tardó demasiado en responder.")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Error del servidor: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error de red: {str(e)}")


# Instancia única — importa esto en todos los archivos
api_client = APIClient()
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class APIClient:
    FASTAPI_URL = "http://127.0.0.1:8001"
    DJANGO_URL  = "http://127.0.0.1:8000"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.access_token = None
        self.rol          = None
        self.nombre       = None

    def _headers_auth(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

    def _get(self, endpoint: str, base: str = "fastapi") -> list | dict:
        base_url = self.FASTAPI_URL if base == "fastapi" else self.DJANGO_URL
        url = f"{base_url}{endpoint}"
        try:
            r = self.session.get(url, headers=self._headers_auth(), timeout=10)
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
            if e.response.status_code == 403:
                raise Exception("No tienes permisos para realizar esta acción.")
            raise Exception(f"Error del servidor: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error de red: {str(e)}")

    def _post(self, endpoint: str, data: dict, base: str = "fastapi") -> dict:
        base_url = self.FASTAPI_URL if base == "fastapi" else self.DJANGO_URL
        url = f"{base_url}{endpoint}"
        try:
            r = self.session.post(url, json=data, headers=self._headers_auth(), timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            detail = ""
            try:
                detail = e.response.json().get("detail", "")
            except Exception:
                pass
            raise Exception(detail or f"Error del servidor: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error de red: {str(e)}")

    def _put(self, endpoint: str, data: dict, base: str = "fastapi") -> dict:
        base_url = self.FASTAPI_URL if base == "fastapi" else self.DJANGO_URL
        url = f"{base_url}{endpoint}"
        try:
            r = self.session.put(url, json=data, headers=self._headers_auth(), timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            detail = ""
            try:
                detail = e.response.json().get("detail", "")
            except Exception:
                pass
            raise Exception(detail or f"Error del servidor: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error de red: {str(e)}")

    def _delete(self, endpoint: str, base: str = "fastapi") -> dict:
        base_url = self.FASTAPI_URL if base == "fastapi" else self.DJANGO_URL
        url = f"{base_url}{endpoint}"
        try:
            r = self.session.delete(url, headers=self._headers_auth(), timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            detail = ""
            try:
                detail = e.response.json().get("detail", "")
            except Exception:
                pass
            raise Exception(detail or f"Error del servidor: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error de red: {str(e)}")

    # ── Auth ──────────────────────────────────────
    def login(self, email: str, password: str) -> dict:
        url = f"{self.FASTAPI_URL}/admin/login"
        try:
            r = requests.post(
                url,
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            logger.debug(f"Login STATUS: {r.status_code} | {r.text}")

            if r.status_code == 200:
                data = r.json()
                self.access_token = data["access_token"]
                self.rol          = data["rol"]
                self.nombre       = data["nombre"]
                self.session.headers["Authorization"] = f"Bearer {self.access_token}"
                return {"ok": True, "rol": self.rol, "nombre": self.nombre}
            elif r.status_code == 401:
                raise Exception("Credenciales incorrectas.")
            else:
                raise Exception(f"Error inesperado: {r.status_code}")
        except requests.exceptions.ConnectionError:
            raise Exception("No se pudo conectar al servidor FastAPI.")
        except requests.exceptions.Timeout:
            raise Exception("El servidor tardó demasiado. Intenta nuevamente.")

    def logout(self):
        self.access_token = None
        self.rol          = None
        self.nombre       = None
        self.session.headers.pop("Authorization", None)

    def esta_autenticado(self) -> bool:
        return self.access_token is not None

    def es_admin(self) -> bool:
        return self.rol == "admin"

    def es_psicologa(self) -> bool:
        return self.rol == "psicologa"

    # ── Estudiantes (FastAPI) ─────────────────────
    def get_estudiantes(self) -> list:
        return self._get("/students/")

    def get_estudiante(self, student_id: int) -> dict:
        return self._get(f"/students/{student_id}")

    def crear_estudiante(self, datos: dict) -> dict:
        return self._post("/students/", datos)

    def actualizar_estudiante(self, student_id: int, datos: dict) -> dict:
        return self._put(f"/students/{student_id}", datos)

    def eliminar_estudiante(self, student_id: int) -> dict:
        return self._delete(f"/students/{student_id}")

    # ── Frases (FastAPI) ──────────────────────────
    def get_frases(self) -> list:
        return self._get("/phrases/")

    def get_frase(self, phrase_id: int) -> dict:
        return self._get(f"/phrases/{phrase_id}")

    def crear_frase(self, contenido: str, autor: str = None) -> dict:
        data = {"contenido": contenido}
        if autor:
            data["autor"] = autor
        return self._post("/phrases/", data)

    def actualizar_frase(self, phrase_id: int, datos: dict) -> dict:
        return self._put(f"/phrases/{phrase_id}", datos)

    def eliminar_frase(self, phrase_id: int) -> dict:
        return self._delete(f"/phrases/{phrase_id}")

    # ── Datos de alumnos ──────────────────────────
    # Lista y perfil vienen de FastAPI
    def get_alumnos(self) -> list:
        return self._get("/students/")

    def get_alumno_perfil(self, alumno_id: int) -> dict:
        return self._get(f"/students/{alumno_id}")

    # Emociones, hábitos, diario y notas vienen de Django
    # (se activarán cuando Django esté corriendo)
    def get_alumno_emociones(self, alumno_id: int) -> list:
        try:
            return self._get(f"/api/students/{alumno_id}/emociones/", base="django")
        except Exception:
            return []   # 👈 retorna vacío si Django no está disponible

    def get_alumno_habitos(self, alumno_id: int) -> list:
        try:
            return self._get(f"/api/students/{alumno_id}/habitos/", base="django")
        except Exception:
            return []

    def get_alumno_diario(self, alumno_id: int) -> list:
        try:
            return self._get(f"/api/students/{alumno_id}/diario/", base="django")
        except Exception:
            return []

    def get_alumno_notas(self, alumno_id: int) -> list:
        try:
            return self._get(f"/api/students/{alumno_id}/notas/", base="django")
        except Exception:
            return []

    def crear_nota(self, alumno_id: int, contenido: str) -> dict:
        return self._post(
            f"/api/students/{alumno_id}/notas/",
            {"contenido": contenido},
            base="django"
        )


api_client = APIClient()
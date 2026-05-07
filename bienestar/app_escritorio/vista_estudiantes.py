from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QFrame, QLineEdit, QComboBox,
    QDateEdit, QFormLayout, QDialog, QDialogButtonBox,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QDate
from PySide6.QtGui import QFont

from api_service import api_client
from styles import STYLE_GLOBAL


# ══════════════════════════════════════════════════
# WORKERS
# ══════════════════════════════════════════════════

class WorkerGetEstudiantes(QThread):
    finished = Signal(list)
    error    = Signal(str)
    def run(self):
        try:
            self.finished.emit(api_client.get_estudiantes())
        except Exception as e:
            self.error.emit(str(e))


class WorkerCrearEstudiante(QThread):
    finished = Signal(dict)
    error    = Signal(str)
    def __init__(self, datos):
        super().__init__()
        self.datos = datos
    def run(self):
        try:
            self.finished.emit(api_client.crear_estudiante(self.datos))
        except Exception as e:
            self.error.emit(str(e))


class WorkerActualizarEstudiante(QThread):
    finished = Signal(dict)
    error    = Signal(str)
    def __init__(self, student_id, datos):
        super().__init__()
        self.student_id = student_id
        self.datos      = datos
    def run(self):
        try:
            self.finished.emit(api_client.actualizar_estudiante(self.student_id, self.datos))
        except Exception as e:
            self.error.emit(str(e))


class WorkerEliminarEstudiante(QThread):
    finished = Signal(dict)
    error    = Signal(str)
    def __init__(self, student_id):
        super().__init__()
        self.student_id = student_id
    def run(self):
        try:
            self.finished.emit(api_client.eliminar_estudiante(self.student_id))
        except Exception as e:
            self.error.emit(str(e))


# ══════════════════════════════════════════════════
# DIÁLOGO: Crear / Editar estudiante
# ══════════════════════════════════════════════════

class DialogoEstudiante(QDialog):
    """Formulario reutilizable para crear y editar estudiantes."""

    def __init__(self, parent=None, datos: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo estudiante" if datos is None else "Editar estudiante")
        self.setFixedSize(420, 380)
        self.setStyleSheet(STYLE_GLOBAL)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(12)

        titulo = QLabel("📋  Datos del estudiante")
        titulo.setObjectName("titulo")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(titulo)

        # ── Formulario ───────────────────────────
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.inp_nombre = QLineEdit()
        self.inp_nombre.setPlaceholderText("Nombre")
        self.inp_nombre.setMinimumHeight(38)

        self.inp_apellido = QLineEdit()
        self.inp_apellido.setPlaceholderText("Apellido")
        self.inp_apellido.setMinimumHeight(38)

        self.inp_correo = QLineEdit()
        self.inp_correo.setPlaceholderText("correo@duocuc.cl")
        self.inp_correo.setMinimumHeight(38)

        self.cmb_genero = QComboBox()
        self.cmb_genero.addItems(["Masculino", "Femenino", "No binario", "Prefiero no decir"])
        self.cmb_genero.setMinimumHeight(38)

        self.date_nacimiento = QDateEdit()
        self.date_nacimiento.setCalendarPopup(True)
        self.date_nacimiento.setDisplayFormat("dd/MM/yyyy")
        self.date_nacimiento.setDate(QDate(2000, 1, 1))
        self.date_nacimiento.setMaximumDate(QDate.currentDate())
        self.date_nacimiento.setMinimumHeight(38)

        form.addRow("Nombre:", self.inp_nombre)
        form.addRow("Apellido:", self.inp_apellido)
        form.addRow("Correo:", self.inp_correo)
        form.addRow("Género:", self.cmb_genero)
        form.addRow("Nacimiento:", self.date_nacimiento)

        layout.addLayout(form)

        # Si es edición, pre-llenar campos
        if datos:
            self.inp_nombre.setText(datos.get("nombre", ""))
            self.inp_apellido.setText(datos.get("apellido", ""))
            self.inp_correo.setText(datos.get("correo", ""))

            genero = datos.get("genero", "")
            idx = self.cmb_genero.findText(genero)
            if idx >= 0:
                self.cmb_genero.setCurrentIndex(idx)

            fn = datos.get("fecha_nacimiento", "")
            if fn:
                partes = fn.split("-")
                if len(partes) == 3:
                    self.date_nacimiento.setDate(QDate(int(partes[0]), int(partes[1]), int(partes[2])))

        # Nota contraseña temporal (solo en creación)
        if datos is None:
            nota = QLabel("ℹ  Se generará una contraseña temporal automáticamente.")
            nota.setObjectName("status")
            nota.setWordWrap(True)
            layout.addWidget(nota)

        layout.addStretch()

        # ── Botones ──────────────────────────────
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("Guardar")
        botones.button(QDialogButtonBox.Ok).setObjectName("btn_primary")
        botones.button(QDialogButtonBox.Cancel).setText("Cancelar")
        botones.button(QDialogButtonBox.Cancel).setObjectName("btn_secondary")
        botones.accepted.connect(self._validar_y_aceptar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def _validar_y_aceptar(self):
        nombre   = self.inp_nombre.text().strip()
        apellido = self.inp_apellido.text().strip()
        correo   = self.inp_correo.text().strip()

        if not nombre or not apellido or not correo:
            QMessageBox.warning(self, "Campos requeridos", "Nombre, apellido y correo son obligatorios.")
            return
        if "@" not in correo or "." not in correo:
            QMessageBox.warning(self, "Correo inválido", "Por favor ingresa un correo válido.")
            return

        self.accept()

    def get_datos(self) -> dict:
        return {
            "nombre":           self.inp_nombre.text().strip(),
            "apellido":         self.inp_apellido.text().strip(),
            "correo":           self.inp_correo.text().strip(),
            "genero":           self.cmb_genero.currentText(),
            "fecha_nacimiento": self.date_nacimiento.date().toString("yyyy-MM-dd"),
        }


# ══════════════════════════════════════════════════
# VENTANA PRINCIPAL — Gestión de estudiantes
# ══════════════════════════════════════════════════

class VistaEstudiantes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienestar Campus — Gestión de Estudiantes")
        self.setMinimumSize(740, 540)
        self.setStyleSheet(STYLE_GLOBAL + STYLE_ESTUDIANTES)

        self.workers              = []
        self._todos_estudiantes   = []
        self.estudiante_seleccionado = None  # dict completo del estudiante

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Topbar ───────────────────────────────
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(56)
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(24, 0, 24, 0)

        titulo = QLabel("👥  Gestión de Estudiantes")
        titulo.setObjectName("topbar_titulo")

        self.btn_nuevo = QPushButton("＋  Nuevo Estudiante")
        self.btn_nuevo.setObjectName("btn_primary")
        self.btn_nuevo.setFixedHeight(34)
        self.btn_nuevo.setCursor(Qt.PointingHandCursor)
        self.btn_nuevo.clicked.connect(self._crear_estudiante)

        tb_layout.addWidget(titulo)
        tb_layout.addStretch()
        tb_layout.addWidget(self.btn_nuevo)

        # ── Contenido ────────────────────────────
        contenido = QWidget()
        cont_layout = QHBoxLayout(contenido)
        cont_layout.setContentsMargins(20, 20, 20, 20)
        cont_layout.setSpacing(16)

        # Panel izquierdo — lista
        panel_lista = QFrame()
        panel_lista.setObjectName("card")
        panel_lista.setMinimumWidth(300)
        lista_layout = QVBoxLayout(panel_lista)
        lista_layout.setContentsMargins(12, 12, 12, 12)
        lista_layout.setSpacing(10)

        lbl_lista = QLabel("Estudiantes registrados")
        lbl_lista.setObjectName("sidebar_titulo")

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Buscar por nombre o correo...")
        self.search.setMinimumHeight(36)
        self.search.textChanged.connect(self._filtrar)

        self.lista = QListWidget()
        self.lista.setObjectName("lista_alumnos")
        self.lista.itemClicked.connect(self._seleccionar)

        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName("status")
        self.lbl_count.setAlignment(Qt.AlignCenter)

        lista_layout.addWidget(lbl_lista)
        lista_layout.addWidget(self.search)
        lista_layout.addWidget(self.lista)
        lista_layout.addWidget(self.lbl_count)

        # Panel derecho — detalle + acciones
        panel_detalle = QFrame()
        panel_detalle.setObjectName("card")
        detalle_layout = QVBoxLayout(panel_detalle)
        detalle_layout.setContentsMargins(20, 20, 20, 20)
        detalle_layout.setSpacing(12)

        self.lbl_selecciona = QLabel("← Selecciona un estudiante")
        self.lbl_selecciona.setObjectName("lbl_vacio")
        self.lbl_selecciona.setAlignment(Qt.AlignCenter)

        # Detalle del estudiante seleccionado
        self.frame_detalle = QFrame()
        self.frame_detalle.hide()
        fd_layout = QVBoxLayout(self.frame_detalle)
        fd_layout.setContentsMargins(0, 0, 0, 0)
        fd_layout.setSpacing(8)

        self.lbl_det_nombre   = QLabel("")
        self.lbl_det_nombre.setObjectName("alumno_nombre")
        self.lbl_det_correo   = QLabel("")
        self.lbl_det_correo.setObjectName("status")
        self.lbl_det_genero   = QLabel("")
        self.lbl_det_genero.setObjectName("status")
        self.lbl_det_fnac     = QLabel("")
        self.lbl_det_fnac.setObjectName("status")
        self.lbl_det_password = QLabel("")
        self.lbl_det_password.setObjectName("status_password")

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separador")

        # Botones de acción
        self.btn_editar = QPushButton("✏️  Editar estudiante")
        self.btn_editar.setObjectName("btn_primary")
        self.btn_editar.setMinimumHeight(40)
        self.btn_editar.setCursor(Qt.PointingHandCursor)
        self.btn_editar.clicked.connect(self._editar_estudiante)

        self.btn_eliminar = QPushButton("🗑️  Eliminar estudiante")
        self.btn_eliminar.setObjectName("btn_danger")
        self.btn_eliminar.setMinimumHeight(40)
        self.btn_eliminar.setCursor(Qt.PointingHandCursor)
        self.btn_eliminar.clicked.connect(self._eliminar_estudiante)

        fd_layout.addWidget(self.lbl_det_nombre)
        fd_layout.addWidget(self.lbl_det_correo)
        fd_layout.addWidget(self.lbl_det_genero)
        fd_layout.addWidget(self.lbl_det_fnac)
        fd_layout.addWidget(self.lbl_det_password)
        fd_layout.addWidget(sep)
        fd_layout.addSpacing(4)
        fd_layout.addWidget(self.btn_editar)
        fd_layout.addWidget(self.btn_eliminar)
        fd_layout.addStretch()

        detalle_layout.addWidget(self.lbl_selecciona)
        detalle_layout.addWidget(self.frame_detalle)

        cont_layout.addWidget(panel_lista, stretch=1)
        cont_layout.addWidget(panel_detalle, stretch=1)

        root.addWidget(topbar)
        root.addWidget(contenido)

        self.cargar_estudiantes()

    # ──────────────────────────────────────────────
    # Cargar y renderizar
    # ──────────────────────────────────────────────
    def cargar_estudiantes(self):
        self.lista.clear()
        self.lista.addItem("  Cargando...")
        self.btn_nuevo.setEnabled(False)

        w = WorkerGetEstudiantes()
        w.finished.connect(self._poblar)
        w.error.connect(lambda e: (
            self.lista.clear(),
            self.lista.addItem("  Error al cargar"),
            QMessageBox.critical(self, "Error", e)
        ))
        w.finished.connect(lambda _: self.btn_nuevo.setEnabled(True))
        w.error.connect(lambda _: self.btn_nuevo.setEnabled(True))
        self.workers.append(w)
        w.start()

    def _poblar(self, estudiantes: list):
        self._todos_estudiantes = estudiantes
        self._renderizar(estudiantes)

    def _renderizar(self, estudiantes: list):
        self.lista.clear()
        if not estudiantes:
            self.lista.addItem("  Sin estudiantes registrados.")
            self.lbl_count.setText("0 estudiantes")
            return
        for e in estudiantes:
            nombre  = f"{e.get('nombre', '')} {e.get('apellido', '')}".strip()
            correo  = e.get('correo', '')
            display = nombre if nombre else correo
            item = QListWidgetItem(f"  {display}")
            item.setData(Qt.UserRole, e)   # guardamos el dict completo
            item.setSizeHint(QSize(0, 44))
            self.lista.addItem(item)
        n = len(estudiantes)
        self.lbl_count.setText(f"{n} estudiante{'s' if n != 1 else ''}")

    def _filtrar(self, texto: str):
        texto = texto.strip().lower()
        if not texto:
            self._renderizar(self._todos_estudiantes)
            return
        filtrados = [
            e for e in self._todos_estudiantes
            if texto in f"{e.get('nombre','')} {e.get('apellido','')} {e.get('correo','')}".lower()
        ]
        self._renderizar(filtrados)

    # ──────────────────────────────────────────────
    # Seleccionar estudiante
    # ──────────────────────────────────────────────
    def _seleccionar(self, item: QListWidgetItem):
        datos = item.data(Qt.UserRole)
        if not datos:
            return
        self.estudiante_seleccionado = datos

        nombre = f"{datos.get('nombre', '')} {datos.get('apellido', '')}".strip()
        correo = datos.get('correo', '—')
        genero = datos.get('genero', '—')
        fnac   = datos.get('fecha_nacimiento', '—')
        debe_cambiar = datos.get('debe_cambiar_password', False)

        self.lbl_det_nombre.setText(f"👤  {nombre}")
        self.lbl_det_correo.setText(f"✉  {correo}")
        self.lbl_det_genero.setText(f"Género: {genero}")
        self.lbl_det_fnac.setText(f"Fecha de nacimiento: {fnac}")

        if debe_cambiar:
            self.lbl_det_password.setText("🔑  Contraseña temporal activa (aún no la ha cambiado)")
        else:
            self.lbl_det_password.setText("✅  Ha cambiado su contraseña")

        self.lbl_selecciona.hide()
        self.frame_detalle.show()

    # ──────────────────────────────────────────────
    # CRUD
    # ──────────────────────────────────────────────
    def _crear_estudiante(self):
        dialogo = DialogoEstudiante(self)
        if dialogo.exec() != QDialog.Accepted:
            return

        datos = dialogo.get_datos()
        self.btn_nuevo.setEnabled(False)
        self.btn_nuevo.setText("Creando...")

        w = WorkerCrearEstudiante(datos)
        w.finished.connect(self._estudiante_creado)
        w.error.connect(lambda e: (
            QMessageBox.critical(self, "Error al crear", e),
            self._reset_btn_nuevo()
        ))
        self.workers.append(w)
        w.start()

    def _estudiante_creado(self, nuevo: dict):
        print("RESPUESTA FASTAPI:", nuevo) 
        nombre       = f"{nuevo.get('nombre', '')} {nuevo.get('apellido', '')}".strip()
        correo       = nuevo.get('email', '')
        password_temp = nuevo.get('password_temp', '—')

        QMessageBox.information(
            self, "✅ Estudiante creado",
            f"El estudiante fue registrado correctamente.\n\n"
            f"👤  {nombre}\n"
            f"✉   {correo}\n\n"
            f"🔑  Contraseña temporal:  {password_temp}\n\n"
            f"Entrégale esta contraseña al estudiante.\n"
            f"Al ingresar por primera vez, el sistema\n"
            f"le pedirá que la cambie."
        )
        self._reset_btn_nuevo()
        self.cargar_estudiantes()

    def _reset_btn_nuevo(self):
        self.btn_nuevo.setEnabled(True)
        self.btn_nuevo.setText("＋  Nuevo Estudiante")

    def _editar_estudiante(self):
        if not self.estudiante_seleccionado:
            return

        dialogo = DialogoEstudiante(self, datos=self.estudiante_seleccionado)
        if dialogo.exec() != QDialog.Accepted:
            return

        datos       = dialogo.get_datos()
        student_id  = self.estudiante_seleccionado.get("id")

        self.btn_editar.setEnabled(False)
        self.btn_editar.setText("Guardando...")

        w = WorkerActualizarEstudiante(student_id, datos)
        w.finished.connect(self._estudiante_actualizado)
        w.error.connect(lambda e: (
            QMessageBox.critical(self, "Error al editar", e),
            self._reset_btn_editar()
        ))
        self.workers.append(w)
        w.start()

    def _estudiante_actualizado(self, actualizado: dict):
        nombre = f"{actualizado.get('nombre', '')} {actualizado.get('apellido', '')}".strip()
        QMessageBox.information(self, "Actualizado", f"✅ Datos de {nombre} actualizados correctamente.")
        self._reset_btn_editar()
        self.cargar_estudiantes()
        # Limpiar selección
        self.frame_detalle.hide()
        self.lbl_selecciona.show()
        self.estudiante_seleccionado = None

    def _reset_btn_editar(self):
        self.btn_editar.setEnabled(True)
        self.btn_editar.setText("✏️  Editar estudiante")

    def _eliminar_estudiante(self):
        if not self.estudiante_seleccionado:
            return

        nombre     = f"{self.estudiante_seleccionado.get('nombre', '')} {self.estudiante_seleccionado.get('apellido', '')}".strip()
        student_id = self.estudiante_seleccionado.get("id")

        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro que quieres eliminar a {nombre}?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp != QMessageBox.Yes:
            return

        self.btn_eliminar.setEnabled(False)
        self.btn_eliminar.setText("Eliminando...")

        w = WorkerEliminarEstudiante(student_id)
        w.finished.connect(self._estudiante_eliminado)
        w.error.connect(lambda e: (
            QMessageBox.critical(self, "Error al eliminar", e),
            self._reset_btn_eliminar()
        ))
        self.workers.append(w)
        w.start()

    def _estudiante_eliminado(self, _):
        QMessageBox.information(self, "Eliminado", "✅ Estudiante eliminado correctamente.")
        self._reset_btn_eliminar()
        self.frame_detalle.hide()
        self.lbl_selecciona.show()
        self.estudiante_seleccionado = None
        self.cargar_estudiantes()

    def _reset_btn_eliminar(self):
        self.btn_eliminar.setEnabled(True)
        self.btn_eliminar.setText("🗑️  Eliminar estudiante")


# ══════════════════════════════════════════════════
# ESTILOS
# ══════════════════════════════════════════════════
STYLE_ESTUDIANTES = """
QFrame#topbar {
    background-color: #ffffff;
    border-bottom: 1px solid #d4ead9;
}
QLabel#topbar_titulo {
    font-size: 15px;
    font-weight: bold;
    color: #1a7a4a;
}
QLabel#alumno_nombre {
    font-size: 16px;
    font-weight: bold;
    color: #1a2e22;
}
QLabel#lbl_vacio {
    color: #9ecfb5;
    font-size: 13px;
    font-style: italic;
}
QLabel#status_password {
    font-size: 12px;
    color: #e67e22;
}
QFrame#separador {
    color: #d4ead9;
    margin: 4px 0;
}
QPushButton#btn_danger {
    background-color: transparent;
    color: #c0392b;
    border: 1.5px solid #c0392b;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#btn_danger:hover { background-color: #fdf0ee; }
QPushButton#btn_danger:disabled { color: #e0a0a0; border-color: #e0a0a0; }
"""
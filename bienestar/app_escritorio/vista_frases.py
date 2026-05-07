from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QFrame, QLineEdit, QTextEdit,
    QDialog, QDialogButtonBox, QFormLayout,
    QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QFont, QColor

from api_service import api_client
from styles import STYLE_GLOBAL


# ══════════════════════════════════════════════════
# WORKERS
# ══════════════════════════════════════════════════

class WorkerGetFrases(QThread):
    finished = Signal(list)
    error    = Signal(str)
    def run(self):
        try:
            self.finished.emit(api_client.get_frases())
        except Exception as e:
            self.error.emit(str(e))


class WorkerCrearFrase(QThread):
    finished = Signal(dict)
    error    = Signal(str)
    def __init__(self, contenido, autor):
        super().__init__()
        self.contenido = contenido
        self.autor     = autor
    def run(self):
        try:
            self.finished.emit(api_client.crear_frase(self.contenido, self.autor))
        except Exception as e:
            self.error.emit(str(e))


class WorkerActualizarFrase(QThread):
    finished = Signal(dict)
    error    = Signal(str)
    def __init__(self, phrase_id, datos):
        super().__init__()
        self.phrase_id = phrase_id
        self.datos     = datos
    def run(self):
        try:
            self.finished.emit(api_client.actualizar_frase(self.phrase_id, self.datos))
        except Exception as e:
            self.error.emit(str(e))


class WorkerEliminarFrase(QThread):
    finished = Signal(dict)
    error    = Signal(str)
    def __init__(self, phrase_id):
        super().__init__()
        self.phrase_id = phrase_id
    def run(self):
        try:
            self.finished.emit(api_client.eliminar_frase(self.phrase_id))
        except Exception as e:
            self.error.emit(str(e))


# ══════════════════════════════════════════════════
# DIÁLOGO: Crear / Editar frase
# ══════════════════════════════════════════════════

class DialogoFrase(QDialog):
    def __init__(self, parent=None, datos: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Nueva frase" if datos is None else "Editar frase")
        self.setFixedSize(460, 320)
        self.setStyleSheet(STYLE_GLOBAL)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(12)

        titulo = QLabel("💬  Frase motivacional")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        # Contenido de la frase
        self.txt_contenido = QTextEdit()
        self.txt_contenido.setPlaceholderText("Escribe aquí la frase motivacional...")
        self.txt_contenido.setObjectName("texto_diario")
        self.txt_contenido.setMaximumHeight(100)

        # Autor
        self.inp_autor = QLineEdit()
        self.inp_autor.setPlaceholderText("Ej: Nelson Mandela (opcional)")
        self.inp_autor.setMinimumHeight(38)

        # Activa (solo en edición)
        self.chk_activa = QCheckBox("Mostrar en el dashboard de estudiantes")
        self.chk_activa.setChecked(True)

        form.addRow("Frase:", self.txt_contenido)
        form.addRow("Autor:", self.inp_autor)
        form.addRow("", self.chk_activa)

        layout.addLayout(form)

        # Pre-llenar si es edición
        if datos:
            self.txt_contenido.setText(datos.get("contenido", ""))
            self.inp_autor.setText(datos.get("autor", "") or "")
            self.chk_activa.setChecked(datos.get("activa", True))
        else:
            # En creación no mostramos el checkbox activa
            self.chk_activa.hide()

        layout.addStretch()

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("Guardar")
        botones.button(QDialogButtonBox.Ok).setObjectName("btn_primary")
        botones.button(QDialogButtonBox.Cancel).setText("Cancelar")
        botones.button(QDialogButtonBox.Cancel).setObjectName("btn_secondary")
        botones.accepted.connect(self._validar_y_aceptar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def _validar_y_aceptar(self):
        contenido = self.txt_contenido.toPlainText().strip()
        if not contenido:
            QMessageBox.warning(self, "Campo requerido", "Por favor escribe el contenido de la frase.")
            return
        self.accept()

    def get_datos(self) -> dict:
        autor = self.inp_autor.text().strip() or None
        return {
            "contenido": self.txt_contenido.toPlainText().strip(),
            "autor":     autor,
            "activa":    self.chk_activa.isChecked(),
        }


# ══════════════════════════════════════════════════
# VENTANA PRINCIPAL — Frases motivacionales
# ══════════════════════════════════════════════════

class VistaFrases(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienestar Campus — Frases Motivacionales")
        self.setMinimumSize(720, 520)
        self.setStyleSheet(STYLE_GLOBAL + STYLE_FRASES)

        self.workers            = []
        self._todas_frases      = []
        self.frase_seleccionada = None

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

        titulo = QLabel("💬  Frases Motivacionales")
        titulo.setObjectName("topbar_titulo")

        subtitulo = QLabel("Las frases activas se muestran en el dashboard de los estudiantes")
        subtitulo.setObjectName("topbar_sub")

        self.btn_nueva = QPushButton("＋  Nueva Frase")
        self.btn_nueva.setObjectName("btn_primary")
        self.btn_nueva.setFixedHeight(34)
        self.btn_nueva.setCursor(Qt.PointingHandCursor)
        self.btn_nueva.clicked.connect(self._crear_frase)

        tb_layout.addWidget(titulo)
        tb_layout.addSpacing(12)
        tb_layout.addWidget(subtitulo)
        tb_layout.addStretch()
        tb_layout.addWidget(self.btn_nueva)

        # ── Contenido ────────────────────────────
        contenido = QWidget()
        cont_layout = QHBoxLayout(contenido)
        cont_layout.setContentsMargins(20, 20, 20, 20)
        cont_layout.setSpacing(16)

        # Panel izquierdo — lista
        panel_lista = QFrame()
        panel_lista.setObjectName("card")
        panel_lista.setMinimumWidth(320)
        lista_layout = QVBoxLayout(panel_lista)
        lista_layout.setContentsMargins(12, 12, 12, 12)
        lista_layout.setSpacing(10)

        lbl_lista = QLabel("Frases registradas")
        lbl_lista.setObjectName("sidebar_titulo")

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Buscar por contenido o autor...")
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

        # Panel derecho — detalle
        panel_detalle = QFrame()
        panel_detalle.setObjectName("card")
        detalle_layout = QVBoxLayout(panel_detalle)
        detalle_layout.setContentsMargins(20, 20, 20, 20)
        detalle_layout.setSpacing(12)

        self.lbl_selecciona = QLabel("← Selecciona una frase")
        self.lbl_selecciona.setObjectName("lbl_vacio")
        self.lbl_selecciona.setAlignment(Qt.AlignCenter)

        self.frame_detalle = QFrame()
        self.frame_detalle.hide()
        fd_layout = QVBoxLayout(self.frame_detalle)
        fd_layout.setContentsMargins(0, 0, 0, 0)
        fd_layout.setSpacing(8)

        lbl_contenido_titulo = QLabel("Frase:")
        lbl_contenido_titulo.setObjectName("sidebar_titulo")

        self.lbl_det_contenido = QLabel("")
        self.lbl_det_contenido.setWordWrap(True)
        self.lbl_det_contenido.setObjectName("frase_contenido")

        self.lbl_det_autor  = QLabel("")
        self.lbl_det_autor.setObjectName("status")

        self.lbl_det_activa = QLabel("")
        self.lbl_det_activa.setObjectName("frase_estado")

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separador")

        self.btn_toggle = QPushButton("")   # texto cambia según estado
        self.btn_toggle.setObjectName("btn_secondary")
        self.btn_toggle.setMinimumHeight(40)
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.clicked.connect(self._toggle_activa)

        self.btn_editar = QPushButton("✏️  Editar frase")
        self.btn_editar.setObjectName("btn_primary")
        self.btn_editar.setMinimumHeight(40)
        self.btn_editar.setCursor(Qt.PointingHandCursor)
        self.btn_editar.clicked.connect(self._editar_frase)

        self.btn_eliminar = QPushButton("🗑️  Eliminar frase")
        self.btn_eliminar.setObjectName("btn_danger")
        self.btn_eliminar.setMinimumHeight(40)
        self.btn_eliminar.setCursor(Qt.PointingHandCursor)
        self.btn_eliminar.clicked.connect(self._eliminar_frase)

        fd_layout.addWidget(lbl_contenido_titulo)
        fd_layout.addWidget(self.lbl_det_contenido)
        fd_layout.addWidget(self.lbl_det_autor)
        fd_layout.addWidget(self.lbl_det_activa)
        fd_layout.addWidget(sep)
        fd_layout.addSpacing(4)
        fd_layout.addWidget(self.btn_toggle)
        fd_layout.addWidget(self.btn_editar)
        fd_layout.addWidget(self.btn_eliminar)
        fd_layout.addStretch()

        detalle_layout.addWidget(self.lbl_selecciona)
        detalle_layout.addWidget(self.frame_detalle)

        cont_layout.addWidget(panel_lista, stretch=1)
        cont_layout.addWidget(panel_detalle, stretch=1)

        root.addWidget(topbar)
        root.addWidget(contenido)

        self.cargar_frases()

    # ──────────────────────────────────────────────
    # Cargar y renderizar
    # ──────────────────────────────────────────────
    def cargar_frases(self):
        self.lista.clear()
        self.lista.addItem("  Cargando...")
        self.btn_nueva.setEnabled(False)

        w = WorkerGetFrases()
        w.finished.connect(self._poblar)
        w.error.connect(lambda e: (
            self.lista.clear(),
            self.lista.addItem("  Error al cargar"),
            QMessageBox.critical(self, "Error", e)
        ))
        w.finished.connect(lambda _: self.btn_nueva.setEnabled(True))
        w.error.connect(lambda _: self.btn_nueva.setEnabled(True))
        self.workers.append(w)
        w.start()

    def _poblar(self, frases: list):
        self._todas_frases = frases
        self._renderizar(frases)

    def _renderizar(self, frases: list):
        self.lista.clear()
        if not frases:
            self.lista.addItem("  Sin frases registradas aún.")
            self.lbl_count.setText("0 frases")
            return

        for f in frases:
            contenido = f.get("contenido", "")
            autor     = f.get("autor", "")
            activa    = f.get("activa", True)

            # Truncar si es muy larga
            preview = contenido[:60] + "..." if len(contenido) > 60 else contenido
            estado  = "✅" if activa else "⏸"
            display = f"  {estado}  {preview}"
            if autor:
                display += f"  — {autor}"

            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, f)
            item.setSizeHint(QSize(0, 52))

            if not activa:
                item.setForeground(QColor("#9ecfb5"))  # gris-verde para inactivas

            self.lista.addItem(item)

        n = len(frases)
        activas = sum(1 for f in frases if f.get("activa", True))
        self.lbl_count.setText(f"{n} frases  ·  {activas} activas")

    def _filtrar(self, texto: str):
        texto = texto.strip().lower()
        if not texto:
            self._renderizar(self._todas_frases)
            return
        filtradas = [
            f for f in self._todas_frases
            if texto in f.get("contenido", "").lower()
            or texto in (f.get("autor", "") or "").lower()
        ]
        self._renderizar(filtradas)

    # ──────────────────────────────────────────────
    # Seleccionar frase
    # ──────────────────────────────────────────────
    def _seleccionar(self, item: QListWidgetItem):
        datos = item.data(Qt.UserRole)
        if not datos:
            return
        self.frase_seleccionada = datos
        self._mostrar_detalle(datos)

    def _mostrar_detalle(self, datos: dict):
        contenido = datos.get("contenido", "")
        autor     = datos.get("autor", "") or "—"
        activa    = datos.get("activa", True)

        self.lbl_det_contenido.setText(f'"{contenido}"')
        self.lbl_det_autor.setText(f"— {autor}")

        if activa:
            self.lbl_det_activa.setText("✅  Activa — visible en el dashboard")
            self.btn_toggle.setText("⏸  Desactivar frase")
        else:
            self.lbl_det_activa.setText("⏸  Inactiva — no visible para estudiantes")
            self.btn_toggle.setText("▶️  Activar frase")

        self.lbl_selecciona.hide()
        self.frame_detalle.show()

    # ──────────────────────────────────────────────
    # CRUD
    # ──────────────────────────────────────────────
    def _crear_frase(self):
        dialogo = DialogoFrase(self)
        if dialogo.exec() != QDialog.Accepted:
            return

        datos = dialogo.get_datos()
        self.btn_nueva.setEnabled(False)
        self.btn_nueva.setText("Guardando...")

        w = WorkerCrearFrase(datos["contenido"], datos["autor"])
        w.finished.connect(self._frase_creada)
        w.error.connect(lambda e: (
            QMessageBox.critical(self, "Error al crear", e),
            self._reset_btn_nueva()
        ))
        self.workers.append(w)
        w.start()

    def _frase_creada(self, nueva: dict):
        QMessageBox.information(self, "Frase creada", "✅ Frase creada y activada correctamente.")
        self._reset_btn_nueva()
        self.cargar_frases()

    def _reset_btn_nueva(self):
        self.btn_nueva.setEnabled(True)
        self.btn_nueva.setText("＋  Nueva Frase")

    def _editar_frase(self):
        if not self.frase_seleccionada:
            return

        dialogo = DialogoFrase(self, datos=self.frase_seleccionada)
        if dialogo.exec() != QDialog.Accepted:
            return

        datos      = dialogo.get_datos()
        phrase_id  = self.frase_seleccionada.get("id")

        self.btn_editar.setEnabled(False)
        self.btn_editar.setText("Guardando...")

        w = WorkerActualizarFrase(phrase_id, datos)
        w.finished.connect(self._frase_actualizada)
        w.error.connect(lambda e: (
            QMessageBox.critical(self, "Error al editar", e),
            self._reset_btn_editar()
        ))
        self.workers.append(w)
        w.start()

    def _frase_actualizada(self, actualizada: dict):
        QMessageBox.information(self, "Actualizada", "✅ Frase actualizada correctamente.")
        self._reset_btn_editar()
        self.frase_seleccionada = actualizada
        self._mostrar_detalle(actualizada)
        self.cargar_frases()

    def _reset_btn_editar(self):
        self.btn_editar.setEnabled(True)
        self.btn_editar.setText("✏️  Editar frase")

    def _toggle_activa(self):
        """Activa o desactiva la frase sin abrir el diálogo."""
        if not self.frase_seleccionada:
            return

        phrase_id  = self.frase_seleccionada.get("id")
        nueva_activa = not self.frase_seleccionada.get("activa", True)

        self.btn_toggle.setEnabled(False)

        w = WorkerActualizarFrase(phrase_id, {"activa": nueva_activa})
        w.finished.connect(self._toggle_completado)
        w.error.connect(lambda e: (
            QMessageBox.critical(self, "Error", e),
            self._reset_btn_toggle()
        ))
        self.workers.append(w)
        w.start()

    def _toggle_completado(self, actualizada: dict):
        self.frase_seleccionada = actualizada
        self._mostrar_detalle(actualizada)
        self._reset_btn_toggle()
        self.cargar_frases()

    def _reset_btn_toggle(self):
        self.btn_toggle.setEnabled(True)

    def _eliminar_frase(self):
        if not self.frase_seleccionada:
            return

        contenido  = self.frase_seleccionada.get("contenido", "")[:50]
        phrase_id  = self.frase_seleccionada.get("id")

        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Eliminar esta frase?\n\n\"{contenido}...\"\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp != QMessageBox.Yes:
            return

        self.btn_eliminar.setEnabled(False)
        self.btn_eliminar.setText("Eliminando...")

        w = WorkerEliminarFrase(phrase_id)
        w.finished.connect(self._frase_eliminada)
        w.error.connect(lambda e: (
            QMessageBox.critical(self, "Error al eliminar", e),
            self._reset_btn_eliminar()
        ))
        self.workers.append(w)
        w.start()

    def _frase_eliminada(self, _):
        QMessageBox.information(self, "Eliminada", "✅ Frase eliminada correctamente.")
        self._reset_btn_eliminar()
        self.frame_detalle.hide()
        self.lbl_selecciona.show()
        self.frase_seleccionada = None
        self.cargar_frases()

    def _reset_btn_eliminar(self):
        self.btn_eliminar.setEnabled(True)
        self.btn_eliminar.setText("🗑️  Eliminar frase")


# ══════════════════════════════════════════════════
# ESTILOS
# ══════════════════════════════════════════════════
STYLE_FRASES = """
QFrame#topbar {
    background-color: #ffffff;
    border-bottom: 1px solid #d4ead9;
}
QLabel#topbar_titulo {
    font-size: 15px;
    font-weight: bold;
    color: #1a7a4a;
}
QLabel#topbar_sub {
    font-size: 11px;
    color: #9ecfb5;
}
QLabel#lbl_vacio {
    color: #9ecfb5;
    font-size: 13px;
    font-style: italic;
}
QLabel#frase_contenido {
    font-size: 14px;
    font-style: italic;
    color: #1a2e22;
    line-height: 1.6;
    padding: 8px 0;
}
QLabel#frase_estado {
    font-size: 12px;
    color: #6b8f77;
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
QCheckBox {
    font-size: 13px;
    color: #2d4a38;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1.5px solid #b8d9c5;
    border-radius: 4px;
    background-color: white;
}
QCheckBox::indicator:checked {
    background-color: #2e9e62;
    border-color: #2e9e62;
}
"""
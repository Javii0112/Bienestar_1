from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QFrame, QTabWidget, QTextEdit,
    QSplitter, QScrollArea, QLineEdit, QDateEdit,
    QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QDate
from PySide6.QtGui import QFont, QColor

import pyqtgraph as pg
from collections import Counter
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

pg.setConfigOption('background', '#ffffff')
pg.setConfigOption('foreground', '#2d4a38')

from api_service import api_client
from styles import STYLE_GLOBAL


# ══════════════════════════════════════════════════
# WORKERS
# ══════════════════════════════════════════════════

class WorkerAlumnos(QThread):
    finished = Signal(list)
    error    = Signal(str)
    def run(self):
        try:
            self.finished.emit(api_client.get_alumnos())
        except Exception as e:
            self.error.emit(str(e))


class WorkerPerfil(QThread):
    finished = Signal(dict)
    error    = Signal(str)
    def __init__(self, alumno_id):
        super().__init__()
        self.alumno_id = alumno_id
    def run(self):
        try:
            self.finished.emit(api_client.get_alumno_perfil(self.alumno_id))
        except Exception as e:
            self.error.emit(str(e))


class WorkerEmociones(QThread):
    finished = Signal(list)
    error    = Signal(str)
    def __init__(self, alumno_id):
        super().__init__()
        self.alumno_id = alumno_id
    def run(self):
        try:
            self.finished.emit(api_client.get_alumno_emociones(self.alumno_id))
        except Exception as e:
            self.error.emit(str(e))


class WorkerHabitos(QThread):
    finished = Signal(list)
    error    = Signal(str)
    def __init__(self, alumno_id):
        super().__init__()
        self.alumno_id = alumno_id
    def run(self):
        try:
            self.finished.emit(api_client.get_alumno_habitos(self.alumno_id))
        except Exception as e:
            self.error.emit(str(e))


class WorkerDiario(QThread):
    finished = Signal(list)
    error    = Signal(str)
    def __init__(self, alumno_id):
        super().__init__()
        self.alumno_id = alumno_id
    def run(self):
        try:
            self.finished.emit(api_client.get_alumno_diario(self.alumno_id))
        except Exception as e:
            self.error.emit(str(e))


class WorkerNotas(QThread):
    finished = Signal(list)
    error    = Signal(str)
    def __init__(self, alumno_id):
        super().__init__()
        self.alumno_id = alumno_id
    def run(self):
        try:
            self.finished.emit(api_client.get_alumno_notas(self.alumno_id))
        except Exception as e:
            self.error.emit(str(e))


class WorkerCrearNota(QThread):
    finished = Signal(dict)
    error    = Signal(str)
    def __init__(self, alumno_id, contenido):
        super().__init__()
        self.alumno_id = alumno_id
        self.contenido = contenido
    def run(self):
        try:
            self.finished.emit(api_client.crear_nota(self.alumno_id, self.contenido))
        except Exception as e:
            self.error.emit(str(e))


# ══════════════════════════════════════════════════
# DASHBOARD PRINCIPAL
# ══════════════════════════════════════════════════

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienestar Campus — Panel Psicólogo")
        self.setMinimumSize(900, 620)
        self.setStyleSheet(STYLE_GLOBAL + STYLE_EXTRA)

        self.alumno_seleccionado_id = None
        self.workers = []
        self._todos_alumnos   = []  # cache para el buscador
        self._todas_emociones = []  # cache para filtro por fecha
        self._todos_habitos   = []  # cache para filtro por fecha

        self._build_ui()

    # ──────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Topbar ───────────────────────────────
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(56)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(24, 0, 24, 0)

        logo = QLabel("🌿  Bienestar Campus")
        logo.setObjectName("topbar_titulo")

        self.btn_logout = QPushButton("Cerrar sesión")
        self.btn_logout.setObjectName("btn_secondary")
        self.btn_logout.setFixedWidth(130)
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.clicked.connect(self.cerrar_sesion)

        topbar_layout.addWidget(logo)
        topbar_layout.addStretch()
        topbar_layout.addWidget(self.btn_logout)

        # ── Splitter: sidebar + detalle ──────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setObjectName("splitter")
        splitter.setHandleWidth(1)

        # Sidebar — lista de alumnos
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(240)
        sidebar.setMaximumWidth(300)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)
        sidebar_layout.setSpacing(10)

        sidebar_header = QHBoxLayout()
        lbl_alumnos = QLabel("👥  Alumnos")
        lbl_alumnos.setObjectName("sidebar_titulo")

        self.btn_recargar = QPushButton("↺")
        self.btn_recargar.setObjectName("btn_icon")
        self.btn_recargar.setFixedSize(30, 30)
        self.btn_recargar.setToolTip("Recargar lista")
        self.btn_recargar.setCursor(Qt.PointingHandCursor)
        self.btn_recargar.clicked.connect(self.cargar_alumnos)

        sidebar_header.addWidget(lbl_alumnos)
        sidebar_header.addStretch()
        sidebar_header.addWidget(self.btn_recargar)

        self.lista_alumnos = QListWidget()
        self.lista_alumnos.setObjectName("lista_alumnos")
        self.lista_alumnos.itemClicked.connect(self.seleccionar_alumno)

        self.lbl_status_lista = QLabel("")
        self.lbl_status_lista.setObjectName("status")
        self.lbl_status_lista.setAlignment(Qt.AlignCenter)

        sidebar_layout.addLayout(sidebar_header)

        # ── Buscador ─────────────────────────────
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar alumno...")
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self._filtrar_alumnos)
        sidebar_layout.addWidget(self.search_input)

        sidebar_layout.addWidget(self.lista_alumnos)
        sidebar_layout.addWidget(self.lbl_status_lista)

        # Panel derecho — detalle del alumno
        self.panel_detalle = QFrame()
        self.panel_detalle.setObjectName("panel_detalle")
        detalle_layout = QVBoxLayout(self.panel_detalle)
        detalle_layout.setContentsMargins(24, 24, 24, 24)
        detalle_layout.setSpacing(16)

        # Estado vacío
        self.lbl_vacio = QLabel("← Selecciona un alumno para ver su información")
        self.lbl_vacio.setObjectName("lbl_vacio")
        self.lbl_vacio.setAlignment(Qt.AlignCenter)

        # Header del alumno seleccionado
        self.alumno_header = QFrame()
        self.alumno_header.setObjectName("card")
        self.alumno_header.hide()
        header_layout = QHBoxLayout(self.alumno_header)
        header_layout.setContentsMargins(20, 16, 20, 16)

        self.lbl_avatar = QLabel("👤")
        self.lbl_avatar.setFont(QFont("Segoe UI", 28))

        info_layout = QVBoxLayout()
        self.lbl_nombre_alumno = QLabel("")
        self.lbl_nombre_alumno.setObjectName("alumno_nombre")
        self.lbl_email_alumno  = QLabel("")
        self.lbl_email_alumno.setObjectName("status")
        self.lbl_meta_alumno   = QLabel("")
        self.lbl_meta_alumno.setObjectName("status")

        info_layout.addWidget(self.lbl_nombre_alumno)
        info_layout.addWidget(self.lbl_email_alumno)
        info_layout.addWidget(self.lbl_meta_alumno)

        header_layout.addWidget(self.lbl_avatar)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()

        # Botón exportar PDF — fila separada
        self.btn_pdf = QPushButton("📄  Exportar PDF")
        self.btn_pdf.setObjectName("btn_secondary")
        self.btn_pdf.setFixedWidth(160)
        self.btn_pdf.setMinimumHeight(36)
        self.btn_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_pdf.clicked.connect(self.exportar_pdf)
        self.btn_pdf.setEnabled(False)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("tabs")
        self.tabs.hide()

        self.tab_emociones_container, self.tab_emociones = self._make_filtered_tab(self._aplicar_filtro_emociones)
        self.tab_habitos_container,   self.tab_habitos   = self._make_filtered_tab(self._aplicar_filtro_habitos)
        self.tab_diario  = self._make_text_tab()
        self.tab_grafico = self._make_grafico_tab()
        self.tab_notas_container, self.notas_lista, self.notas_input, self.notas_btn = self._make_notas_tab()

        self.tabs.addTab(self.tab_emociones_container, "😊  Emociones")
        self.tabs.addTab(self.tab_habitos_container,   "💪  Hábitos")
        self.tabs.addTab(self.tab_diario,              "📓  Diario")
        self.tabs.addTab(self.tab_grafico,             "📊  Gráfico")
        self.tabs.addTab(self.tab_notas_container,     "🗒️  Notas")
        self.tabs.currentChanged.connect(self.tab_cambiada)

        detalle_layout.addWidget(self.lbl_vacio)
        detalle_layout.addWidget(self.alumno_header)
        detalle_layout.addWidget(self.btn_pdf)
        detalle_layout.addWidget(self.tabs)

        # Ensamblar splitter
        splitter.addWidget(sidebar)
        splitter.addWidget(self.panel_detalle)
        splitter.setStretchFactor(1, 1)

        root.addWidget(topbar)
        root.addWidget(splitter)

        # Cargar alumnos al abrir
        self.cargar_alumnos()

    def _make_list_tab(self):
        widget = QListWidget()
        widget.setObjectName("lista_alumnos")
        return widget

    def _make_filtered_tab(self, on_filter):
        """Crea un tab con filtro de fecha + lista."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Fila de filtros
        filter_row = QHBoxLayout()

        lbl_desde = QLabel("Desde:")
        lbl_desde.setFixedWidth(48)
        date_desde = QDateEdit()
        date_desde.setCalendarPopup(True)
        date_desde.setDate(QDate.currentDate().addMonths(-1))
        date_desde.setDisplayFormat("dd/MM/yyyy")
        date_desde.setMinimumHeight(32)

        lbl_hasta = QLabel("Hasta:")
        lbl_hasta.setFixedWidth(44)
        date_hasta = QDateEdit()
        date_hasta.setCalendarPopup(True)
        date_hasta.setDate(QDate.currentDate())
        date_hasta.setDisplayFormat("dd/MM/yyyy")
        date_hasta.setMinimumHeight(32)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setObjectName("btn_primary")
        btn_filtrar.setFixedWidth(90)
        btn_filtrar.setMinimumHeight(32)
        btn_filtrar.setCursor(Qt.PointingHandCursor)

        btn_limpiar = QPushButton("Ver todo")
        btn_limpiar.setObjectName("btn_secondary")
        btn_limpiar.setFixedWidth(90)
        btn_limpiar.setMinimumHeight(32)
        btn_limpiar.setCursor(Qt.PointingHandCursor)

        filter_row.addWidget(lbl_desde)
        filter_row.addWidget(date_desde)
        filter_row.addSpacing(8)
        filter_row.addWidget(lbl_hasta)
        filter_row.addWidget(date_hasta)
        filter_row.addSpacing(8)
        filter_row.addWidget(btn_filtrar)
        filter_row.addWidget(btn_limpiar)
        filter_row.addStretch()

        lista = QListWidget()
        lista.setObjectName("lista_alumnos")

        layout.addLayout(filter_row)
        layout.addWidget(lista)

        # Conectar botones
        btn_filtrar.clicked.connect(lambda: on_filter(
            date_desde.date().toString("yyyy-MM-dd"),
            date_hasta.date().toString("yyyy-MM-dd"),
            lista
        ))
        btn_limpiar.clicked.connect(lambda: on_filter(None, None, lista))

        return container, lista

    def _make_notas_tab(self):
        """Crea el tab de notas del psicólogo."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Lista de notas anteriores
        lbl = QLabel("Notas anteriores:")
        lbl.setObjectName("sidebar_titulo")

        lista = QListWidget()
        lista.setObjectName("lista_alumnos")
        lista.setMinimumHeight(160)

        # Área para escribir nueva nota
        lbl_nueva = QLabel("Nueva nota:")
        lbl_nueva.setObjectName("sidebar_titulo")

        texto_input = QTextEdit()
        texto_input.setPlaceholderText("Escribe aquí tu observación sobre el alumno...")
        texto_input.setObjectName("texto_diario")
        texto_input.setMaximumHeight(120)

        btn_guardar = QPushButton("💾  Guardar nota")
        btn_guardar.setObjectName("btn_primary")
        btn_guardar.setMinimumHeight(40)
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.clicked.connect(self._guardar_nota)

        layout.addWidget(lbl)
        layout.addWidget(lista)
        layout.addWidget(lbl_nueva)
        layout.addWidget(texto_input)
        layout.addWidget(btn_guardar)

        return container, lista, texto_input, btn_guardar

    def _make_grafico_tab(self):
        """Crea el tab del gráfico con pyqtgraph embebido."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        lbl = QLabel("Frecuencia de emociones registradas")
        lbl.setObjectName("status")
        lbl.setAlignment(Qt.AlignCenter)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#f7fbf8')
        self.plot_widget.showGrid(x=False, y=True, alpha=0.3)
        self.plot_widget.getAxis('bottom').setStyle(tickTextOffset=8)
        self.plot_widget.getAxis('left').setLabel('Frecuencia')

        layout.addWidget(lbl)
        layout.addWidget(self.plot_widget)
        return container

    def _make_text_tab(self):
        widget = QTextEdit()
        widget.setReadOnly(True)
        widget.setObjectName("texto_diario")
        return widget

    # ──────────────────────────────────────────────
    # Cargar lista de alumnos
    # ──────────────────────────────────────────────
    def cargar_alumnos(self):
        self.lista_alumnos.clear()
        self.lbl_status_lista.setText("Cargando...")
        self.btn_recargar.setEnabled(False)

        w = WorkerAlumnos()
        w.finished.connect(self._poblar_alumnos)
        w.error.connect(lambda e: (
            self.lbl_status_lista.setText("Error al cargar"),
            QMessageBox.critical(self, "Error", e)
        ))
        w.finished.connect(lambda: self.btn_recargar.setEnabled(True))
        w.error.connect(lambda: self.btn_recargar.setEnabled(True))
        self.workers.append(w)
        w.start()

    def _poblar_alumnos(self, alumnos: list):
        self._todos_alumnos = alumnos  # guardar para el buscador
        self._renderizar_alumnos(alumnos)
        count = len(alumnos)
        self.lbl_status_lista.setText(f"{count} alumno{'s' if count != 1 else ''} registrado{'s' if count != 1 else ''}")

    def _renderizar_alumnos(self, alumnos: list):
        self.lista_alumnos.clear()
        for alumno in alumnos:
            nombre  = f"{alumno.get('nombre', '')} {alumno.get('apellido', '')}".strip()
            email   = alumno.get('email', '')
            display = nombre if nombre else email
            item = QListWidgetItem(f"  {display}")
            item.setData(Qt.UserRole, alumno.get('id'))
            item.setSizeHint(QSize(0, 44))
            self.lista_alumnos.addItem(item)

    def _filtrar_alumnos(self, texto: str):
        texto = texto.strip().lower()
        if not texto:
            self._renderizar_alumnos(self._todos_alumnos)
            return
        filtrados = [
            a for a in self._todos_alumnos
            if texto in f"{a.get('nombre','')} {a.get('apellido','')} {a.get('email','')}".lower()
        ]
        self._renderizar_alumnos(filtrados)

    # ──────────────────────────────────────────────
    # Seleccionar alumno
    # ──────────────────────────────────────────────
    def seleccionar_alumno(self, item: QListWidgetItem):
        alumno_id = item.data(Qt.UserRole)
        if not alumno_id:
            return

        self.alumno_seleccionado_id = alumno_id
        self.lbl_vacio.hide()
        self.alumno_header.show()
        self.tabs.show()
        self.btn_pdf.setEnabled(True)

        # Cargar perfil
        w = WorkerPerfil(alumno_id)
        w.finished.connect(self._mostrar_perfil)
        w.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self.workers.append(w)
        w.start()

        # Pre-cargar emociones siempre (para el gráfico y el tab)
        w2 = WorkerEmociones(alumno_id)
        w2.finished.connect(self._poblar_emociones)
        w2.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self.workers.append(w2)
        w2.start()

        # Cargar el resto del tab activo si no es emociones
        idx = self.tabs.currentIndex()
        if idx != 0:
            self._cargar_tab_activa()

    def _mostrar_perfil(self, perfil: dict):
        nombre   = f"{perfil.get('nombre', '')} {perfil.get('apellido', '')}".strip()
        email    = perfil.get('email', '')
        genero   = perfil.get('genero', '—')
        edad     = perfil.get('edad', '—')

        self.lbl_nombre_alumno.setText(nombre or email)
        self.lbl_email_alumno.setText(f"✉  {email}")
        self.lbl_meta_alumno.setText(f"Género: {genero}   ·   Edad: {edad} años")

    # ──────────────────────────────────────────────
    # Tabs
    # ──────────────────────────────────────────────
    def tab_cambiada(self, index):
        if self.alumno_seleccionado_id:
            self._cargar_tab_activa()

    def _cargar_tab_activa(self):
        idx = self.tabs.currentIndex()
        aid = self.alumno_seleccionado_id

        if idx == 0:
            self.tab_emociones.clear()
            self.tab_emociones.addItem("  Cargando...")
            w = WorkerEmociones(aid)
            w.finished.connect(self._poblar_emociones)
            w.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
            self.workers.append(w)
            w.start()

        elif idx == 1:
            self.tab_habitos.clear()
            self.tab_habitos.addItem("  Cargando...")
            w = WorkerHabitos(aid)
            w.finished.connect(self._poblar_habitos)
            w.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
            self.workers.append(w)
            w.start()

        elif idx == 2:
            self.tab_diario.setText("Cargando...")
            w = WorkerDiario(aid)
            w.finished.connect(self._poblar_diario)
            w.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
            self.workers.append(w)
            w.start()

        elif idx == 3:
            self._actualizar_grafico()

        elif idx == 4:
            self.notas_lista.clear()
            self.notas_lista.addItem("  Cargando...")
            w = WorkerNotas(aid)
            w.finished.connect(self._poblar_notas)
            w.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
            self.workers.append(w)
            w.start()

    def _poblar_emociones(self, emociones: list):
        self._todas_emociones = emociones
        self._renderizar_emociones(emociones)
        # Actualizar gráfico automáticamente con los nuevos datos
        self._actualizar_grafico()

    def _renderizar_emociones(self, emociones: list):
        self.tab_emociones.clear()
        if not emociones:
            self.tab_emociones.addItem("  Sin registros de emociones.")
            return
        for r in emociones:
            nombre     = r.get('emocion_nombre', '—')
            intensidad = r.get('intensidad', '—')
            fecha      = r.get('fecha', '')[:10]
            comentario = r.get('comentario', '')
            texto = f"  {fecha}   {nombre}   · Intensidad: {intensidad}"
            if comentario:
                texto += f"   — {comentario}"
            item = QListWidgetItem(texto)
            item.setSizeHint(QSize(0, 40))
            self.tab_emociones.addItem(item)

    def _aplicar_filtro_emociones(self, desde, hasta, lista):
        if desde is None:
            self._renderizar_emociones(self._todas_emociones)
            return
        filtradas = [
            e for e in self._todas_emociones
            if desde <= e.get('fecha', '')[:10] <= hasta
        ]
        self.tab_emociones.clear()
        if not filtradas:
            self.tab_emociones.addItem("  Sin registros en ese rango de fechas.")
            return
        for r in filtradas:
            nombre     = r.get('emocion_nombre', '—')
            intensidad = r.get('intensidad', '—')
            fecha      = r.get('fecha', '')[:10]
            comentario = r.get('comentario', '')
            texto = f"  {fecha}   {nombre}   · Intensidad: {intensidad}"
            if comentario:
                texto += f"   — {comentario}"
            item = QListWidgetItem(texto)
            item.setSizeHint(QSize(0, 40))
            self.tab_emociones.addItem(item)

    def _poblar_habitos(self, habitos: list):
        self._todos_habitos = habitos  # guardar cache
        self._renderizar_habitos(habitos)

    def _renderizar_habitos(self, habitos: list):
        self.tab_habitos.clear()
        if not habitos:
            self.tab_habitos.addItem("  Sin registros de hábitos.")
            return
        for r in habitos:
            nombre = r.get('habito_nombre', '—')
            fecha  = r.get('fecha', '')
            valor  = r.get('valor', '—')
            item = QListWidgetItem(f"  {fecha}   {nombre}   · Valor: {valor}")
            item.setSizeHint(QSize(0, 40))
            self.tab_habitos.addItem(item)

    def _aplicar_filtro_habitos(self, desde, hasta, lista):
        if desde is None:
            self._renderizar_habitos(self._todos_habitos)
            return
        filtrados = [
            h for h in self._todos_habitos
            if desde <= h.get('fecha', '') <= hasta
        ]
        self.tab_habitos.clear()
        if not filtrados:
            self.tab_habitos.addItem("  Sin registros en ese rango de fechas.")
            return
        for r in filtrados:
            nombre = r.get('habito_nombre', '—')
            fecha  = r.get('fecha', '')
            valor  = r.get('valor', '—')
            item = QListWidgetItem(f"  {fecha}   {nombre}   · Valor: {valor}")
            item.setSizeHint(QSize(0, 40))
            self.tab_habitos.addItem(item)

    def _poblar_diario(self, entradas: list):
        if not entradas:
            self.tab_diario.setText("Sin entradas en el diario.")
            return
        texto = ""
        for e in entradas:
            fecha     = e.get('fecha', '')[:10]
            contenido = e.get('contenido', '')
            texto += f"📅 {fecha}\n{contenido}\n{'─' * 40}\n\n"
        self.tab_diario.setText(texto)

    def _poblar_notas(self, notas: list):
        self.notas_lista.clear()
        if not notas:
            self.notas_lista.addItem("  Sin notas registradas aún.")
            return
        for nota in notas:
            fecha     = nota.get('fecha', '')[:10]
            contenido = nota.get('contenido', '')
            respuestas = nota.get('respuestas', [])

            # Nota del psicólogo
            item_nota = QListWidgetItem(f"  🧑‍⚕️ {fecha} — {contenido}")
            item_nota.setSizeHint(QSize(0, 44))
            self.notas_lista.addItem(item_nota)

            # Respuestas del alumno
            for resp in respuestas:
                fecha_r   = resp.get('fecha', '')[:10]
                contenido_r = resp.get('contenido', '')
                nombre_r  = resp.get('alumno_nombre', 'Alumno')
                item_resp = QListWidgetItem(f"      💬 {fecha_r} — {nombre_r}: {contenido_r}")
                item_resp.setSizeHint(QSize(0, 40))
                item_resp.setForeground(QColor('#2e9e62'))
                self.notas_lista.addItem(item_resp)

            # Separador visual
            sep = QListWidgetItem("  " + "─" * 40)
            sep.setForeground(QColor('#d4ead9'))
            sep.setFlags(Qt.NoItemFlags)
            self.notas_lista.addItem(sep)

    def _guardar_nota(self):
        contenido = self.notas_input.toPlainText().strip()
        if not contenido:
            QMessageBox.warning(self, "Campo vacío", "Por favor escribe una nota antes de guardar.")
            return
        if not self.alumno_seleccionado_id:
            return

        self.notas_btn.setEnabled(False)
        self.notas_btn.setText("Guardando...")

        w = WorkerCrearNota(self.alumno_seleccionado_id, contenido)
        w.finished.connect(self._nota_guardada)
        w.error.connect(lambda e: (
            QMessageBox.critical(self, "Error", e),
            self._reset_btn_nota()
        ))
        self.workers.append(w)
        w.start()

    def _nota_guardada(self, nota: dict):
        self.notas_input.clear()
        self._reset_btn_nota()
        # Recargar lista de notas
        w = WorkerNotas(self.alumno_seleccionado_id)
        w.finished.connect(self._poblar_notas)
        w.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self.workers.append(w)
        w.start()

    def _reset_btn_nota(self):
        self.notas_btn.setEnabled(True)
        self.notas_btn.setText("💾  Guardar nota")

    # ──────────────────────────────────────────────
    # Exportar PDF
    # ──────────────────────────────────────────────
    def exportar_pdf(self):
        nombre = self.lbl_nombre_alumno.text().strip() or "alumno"
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", f"Informe_{nombre.replace(' ', '_')}.pdf",
            "PDF Files (*.pdf)"
        )
        if not ruta:
            return

        try:
            self._generar_pdf(ruta, nombre)
            QMessageBox.information(self, "PDF exportado", f"Informe guardado en:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el PDF:\n{str(e)}")

    def _generar_pdf(self, ruta: str, nombre: str):
        doc = SimpleDocTemplate(ruta, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        verde  = colors.HexColor('#1a7a4a')
        verde_claro = colors.HexColor('#d6f0e3')

        estilo_titulo = ParagraphStyle('titulo', fontSize=20, textColor=verde,
                                       fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=6)
        estilo_sub    = ParagraphStyle('sub', fontSize=10, textColor=colors.HexColor('#6b8f77'),
                                       alignment=TA_CENTER, spaceAfter=20)
        estilo_seccion = ParagraphStyle('seccion', fontSize=13, textColor=verde,
                                        fontName='Helvetica-Bold', spaceBefore=16, spaceAfter=8)
        estilo_normal = ParagraphStyle('normal', fontSize=10, leading=16,
                                       textColor=colors.HexColor('#1a2e22'), spaceAfter=4)
        estilo_muted  = ParagraphStyle('muted', fontSize=9, textColor=colors.HexColor('#6b8f77'),
                                       spaceAfter=12)

        story = []

        # ── Encabezado ───────────────────────────
        story.append(Paragraph("🌿 Bienestar Campus", estilo_titulo))
        story.append(Paragraph("Informe de seguimiento del alumno", estilo_sub))
        story.append(HRFlowable(width="100%", thickness=1, color=verde_claro))
        story.append(Spacer(1, 0.4*cm))

        # ── Datos del perfil ─────────────────────
        story.append(Paragraph("Datos del alumno", estilo_seccion))
        email  = self.lbl_email_alumno.text().replace("✉  ", "")
        meta   = self.lbl_meta_alumno.text()
        story.append(Paragraph(f"<b>Nombre:</b> {nombre}", estilo_normal))
        story.append(Paragraph(f"<b>Email:</b> {email}", estilo_normal))
        story.append(Paragraph(f"<b>{meta}</b>", estilo_normal))
        story.append(Spacer(1, 0.3*cm))

        # ── Emociones ────────────────────────────
        story.append(HRFlowable(width="100%", thickness=0.5, color=verde_claro))
        story.append(Paragraph("Registro de emociones", estilo_seccion))

        if self._todas_emociones:
            data = [["Fecha", "Emoción", "Intensidad", "Comentario"]]
            for e in self._todas_emociones[:30]:
                data.append([
                    e.get('fecha', '')[:10],
                    e.get('emocion_nombre', '—'),
                    str(e.get('intensidad', '—')),
                    e.get('comentario', '') or '—'
                ])
            tabla = Table(data, colWidths=[3*cm, 4*cm, 3*cm, 7*cm])
            tabla.setStyle(TableStyle([
                ('BACKGROUND',  (0,0), (-1,0), verde),
                ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
                ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',    (0,0), (-1,-1), 9),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f7f2')]),
                ('GRID',        (0,0), (-1,-1), 0.5, colors.HexColor('#d4ead9')),
                ('ALIGN',       (2,0), (2,-1), 'CENTER'),
                ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING',  (0,0), (-1,-1), 5),
                ('BOTTOMPADDING',(0,0), (-1,-1), 5),
            ]))
            story.append(tabla)
        else:
            story.append(Paragraph("Sin registros de emociones.", estilo_muted))

        # ── Hábitos ──────────────────────────────
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=verde_claro))
        story.append(Paragraph("Registro de hábitos", estilo_seccion))

        if self._todos_habitos:
            data = [["Fecha", "Hábito", "Valor"]]
            for h in self._todos_habitos[:30]:
                data.append([
                    h.get('fecha', ''),
                    h.get('habito_nombre', '—'),
                    str(h.get('valor', '—'))
                ])
            tabla = Table(data, colWidths=[3*cm, 10*cm, 4*cm])
            tabla.setStyle(TableStyle([
                ('BACKGROUND',  (0,0), (-1,0), verde),
                ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
                ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE',    (0,0), (-1,-1), 9),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f7f2')]),
                ('GRID',        (0,0), (-1,-1), 0.5, colors.HexColor('#d4ead9')),
                ('ALIGN',       (2,0), (2,-1), 'CENTER'),
                ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING',  (0,0), (-1,-1), 5),
                ('BOTTOMPADDING',(0,0), (-1,-1), 5),
            ]))
            story.append(tabla)
        else:
            story.append(Paragraph("Sin registros de hábitos.", estilo_muted))

        # ── Diario ───────────────────────────────
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=verde_claro))
        story.append(Paragraph("Entradas del diario", estilo_seccion))

        # Obtener entradas del diario desde el QTextEdit
        texto_diario = self.tab_diario.toPlainText().strip()
        if texto_diario and texto_diario != "Cargando..." and texto_diario != "Sin entradas en el diario.":
            for linea in texto_diario.split('\n'):
                if linea.strip():
                    story.append(Paragraph(linea.replace('─', '-'), estilo_normal))
        else:
            story.append(Paragraph("Sin entradas en el diario.", estilo_muted))

        # ── Pie de página ────────────────────────
        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=1, color=verde_claro))
        from datetime import date
        story.append(Paragraph(
            f"Informe generado el {date.today().strftime('%d/%m/%Y')} · Bienestar Campus",
            ParagraphStyle('pie', fontSize=8, textColor=colors.HexColor('#9ecfb5'),
                           alignment=TA_CENTER, spaceBefore=8)
        ))

        doc.build(story)

    def _actualizar_grafico(self):
        """Dibuja el gráfico de frecuencia de emociones con pyqtgraph."""
        self.plot_widget.clear()

        if not self._todas_emociones:
            self.plot_widget.addItem(pg.TextItem(
                text="Sin datos de emociones",
                color='#9ecfb5', anchor=(0.5, 0.5)
            ))
            return

        # Contar frecuencia de cada emoción
        nombres  = [e.get('emocion_nombre', 'Desconocida') for e in self._todas_emociones]
        conteo   = Counter(nombres)
        etiquetas = list(conteo.keys())
        valores   = list(conteo.values())

        # Colores verdes
        colores = [
            (46, 158, 98), (68, 184, 122), (94, 207, 146),
            (125, 224, 170), (158, 239, 192), (26, 122, 74),
            (58, 184, 112), (80, 200, 130)
        ]

        # Dibujar barras
        for i, (etiqueta, valor) in enumerate(zip(etiquetas, valores)):
            color = colores[i % len(colores)]
            barra = pg.BarGraphItem(
                x=[i], height=[valor], width=0.6,
                brush=pg.mkBrush(*color, 220),
                pen=pg.mkPen('w', width=1)
            )
            self.plot_widget.addItem(barra)

            # Número encima de cada barra
            texto = pg.TextItem(text=str(valor), color='#1a2e22', anchor=(0.5, 1))
            texto.setPos(i, valor + 0.1)
            self.plot_widget.addItem(texto)

        # Etiquetas eje X
        eje_x = self.plot_widget.getAxis('bottom')
        eje_x.setTicks([[(i, nombre) for i, nombre in enumerate(etiquetas)]])

        self.plot_widget.setXRange(-0.5, len(etiquetas) - 0.5)
        self.plot_widget.setYRange(0, max(valores) + 1)

    # ──────────────────────────────────────────────
    # Cerrar sesión
    # ──────────────────────────────────────────────
    def cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Estás seguro que quieres cerrar sesión?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            api_client.logout()
            from login import LoginWindow
            self.login = LoginWindow()
            self.login.show()
            self.close()


# ══════════════════════════════════════════════════
# ESTILOS EXTRA (complementan styles.py)
# ══════════════════════════════════════════════════
STYLE_EXTRA = """
QFrame#topbar {
    background-color: #ffffff;
    border-bottom: 1px solid #d4ead9;
}

QLabel#topbar_titulo {
    font-size: 16px;
    font-weight: bold;
    color: #1a7a4a;
}

QFrame#sidebar {
    background-color: #f7fbf8;
    border-right: 1px solid #d4ead9;
}

QLabel#sidebar_titulo {
    font-size: 13px;
    font-weight: bold;
    color: #2d4a38;
}

QFrame#panel_detalle {
    background-color: #f0f7f2;
}

QLabel#lbl_vacio {
    color: #9ecfb5;
    font-size: 14px;
    font-style: italic;
}

QLabel#alumno_nombre {
    font-size: 16px;
    font-weight: bold;
    color: #1a2e22;
}

QTabWidget#tabs::pane {
    background-color: #ffffff;
    border: 1.5px solid #b8d9c5;
    border-radius: 12px;
}

QTabBar::tab {
    background-color: transparent;
    color: #6b8f77;
    padding: 10px 20px;
    font-size: 13px;
    border-bottom: 2px solid transparent;
}

QTabBar::tab:selected {
    color: #2e9e62;
    border-bottom: 2px solid #2e9e62;
    font-weight: bold;
}

QTabBar::tab:hover {
    color: #2e9e62;
}

QTextEdit#texto_diario {
    background-color: #ffffff;
    border: none;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    color: #2d4a38;
    padding: 12px;
    line-height: 1.6;
}

QPushButton#btn_icon {
    background-color: transparent;
    border: 1px solid #b8d9c5;
    border-radius: 6px;
    color: #2e9e62;
    font-size: 16px;
    font-weight: bold;
}

QPushButton#btn_icon:hover {
    background-color: #e8f7ef;
}

QDateEdit {
    background-color: #ffffff;
    border: 1.5px solid #b8d9c5;
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 12px;
    color: #1a2e22;
}

QDateEdit:focus {
    border-color: #2e9e62;
}

QDateEdit::drop-down {
    border: none;
    width: 20px;
}

QCalendarWidget {
    background-color: #ffffff;
    border: 1px solid #b8d9c5;
    border-radius: 8px;
}

QCalendarWidget QAbstractItemView {
    selection-background-color: #2e9e62;
    selection-color: white;
}

"""
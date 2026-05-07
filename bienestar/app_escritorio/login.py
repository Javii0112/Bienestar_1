from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from api_service import api_client
from styles import STYLE_GLOBAL


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bienestar Campus — Acceso")
        self.setFixedSize(380, 500)
        self.setStyleSheet(STYLE_GLOBAL + STYLE_LOGIN_EXTRA)

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setContentsMargins(30, 30, 30, 30)

        # ── Tarjeta central ──────────────────────
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(320)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(30, 32, 30, 32)

        # ── Encabezado ───────────────────────────
        emoji = QLabel("🌿")
        emoji.setAlignment(Qt.AlignCenter)
        emoji.setFont(QFont("Segoe UI", 32))

        titulo = QLabel("Bienestar Campus")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)

        subtitulo = QLabel("Acceso para administradores y psicólogos")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setWordWrap(True)

        # ── Campos ───────────────────────────────
        lbl_email = QLabel("Email institucional:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("✉  usuario@duocuc.cl")
        self.email_input.setMinimumHeight(42)

        lbl_pass = QLabel("Contraseña:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("🔒  Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(42)
        self.password_input.returnPressed.connect(self.handle_login)

        # ── Botón ────────────────────────────────
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setObjectName("btn_primary")
        self.login_button.setMinimumHeight(44)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)

        # ── Status ───────────────────────────────
        self.status_label = QLabel("")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)

        # ── Ensamblar ─────────────────────────────
        card_layout.addWidget(emoji)
        card_layout.addWidget(titulo)
        card_layout.addWidget(subtitulo)
        card_layout.addSpacing(10)
        card_layout.addWidget(lbl_email)
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(lbl_pass)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(4)
        card_layout.addWidget(self.login_button)
        card_layout.addWidget(self.status_label)

        root.addWidget(card)

    # ─────────────────────────────────────────────
    def handle_login(self):
        email    = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            self.status_label.setText("⚠ Por favor ingresa email y contraseña.")
            return

        self._set_loading(True)

        try:
            resultado = api_client.login(email, password)

            # Login exitoso — abrir la ventana correcta según el rol
            rol    = resultado["rol"]
            nombre = resultado["nombre"]

            if rol == "admin":
                self._abrir_panel_admin(nombre)
            elif rol == "psicologa":
                self._abrir_panel_psicologa(nombre)
            else:
                QMessageBox.critical(self, "Error", f"Rol desconocido: {rol}")

        except Exception as e:
            self.status_label.setText(f"✗ {str(e)}")
            self.password_input.clear()
            self.password_input.setFocus()

        finally:
            self._set_loading(False)

    def _abrir_panel_admin(self, nombre: str):
        """El admin ve el panel completo con gestión de estudiantes."""
        from dashboard import DashboardWindow
        self.dashboard = DashboardWindow(rol="admin", nombre=nombre)
        self.dashboard.show()
        self.close()

    def _abrir_panel_psicologa(self, nombre: str):
        """La psicóloga ve el panel de seguimiento y frases."""
        from dashboard import DashboardWindow
        self.dashboard = DashboardWindow(rol="psicologa", nombre=nombre)
        self.dashboard.show()
        self.close()

    def _set_loading(self, loading: bool):
        self.login_button.setEnabled(not loading)
        self.login_button.setText("Conectando..." if loading else "Iniciar Sesión")
        self.status_label.setText("Verificando credenciales..." if loading else "")


# ── Estilos adicionales para el login ─────────────
STYLE_LOGIN_EXTRA = """
QLabel {
    font-size: 13px;
    color: #2d4a38;
}

QLabel#status {
    font-size: 12px;
    color: #c0392b;
    min-height: 20px;
}
"""
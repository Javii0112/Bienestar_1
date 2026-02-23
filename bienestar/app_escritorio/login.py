from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from api_service import api_client
from dashboard import DashboardWindow
from styles import STYLE_GLOBAL


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bienestar Campus")
        self.setFixedSize(380, 480)
        self.setStyleSheet(STYLE_GLOBAL)

        # Layout raíz — centra la tarjeta
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

        subtitulo = QLabel("Inicia sesión con tu cuenta institucional")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setWordWrap(True)

        # ── Campos ───────────────────────────────
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("✉  usuario@duocuc.cl")
        self.email_input.setMinimumHeight(42)

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

        # ── Ensamblar tarjeta ─────────────────────
        card_layout.addWidget(emoji)
        card_layout.addWidget(titulo)
        card_layout.addWidget(subtitulo)
        card_layout.addSpacing(10)
        card_layout.addWidget(QLabel("Email:"))
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(QLabel("Contraseña:"))
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
            QMessageBox.warning(self, "Campos vacíos", "Por favor ingresa email y contraseña.")
            return

        self._set_loading(True)

        try:
            success = api_client.login(email, password)

            if success:
                self.dashboard = DashboardWindow()
                self.dashboard.show()
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Credenciales incorrectas.")
                self.password_input.clear()
                self.password_input.setFocus()

        except Exception as e:
            QMessageBox.critical(self, "Error de conexión", str(e))

        finally:
            self._set_loading(False)

    def _set_loading(self, loading: bool):
        self.login_button.setEnabled(not loading)
        self.login_button.setText("Conectando..." if loading else "Iniciar Sesión")
        self.status_label.setText("Verificando credenciales..." if loading else "")
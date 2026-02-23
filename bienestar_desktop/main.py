import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)

API_URL = "http://127.0.0.1:8000/api/token/"
PROTECTED_URL = "http://127.0.0.1:8000/api/emociones/"


# -----------------------
# DASHBOARD WINDOW
# -----------------------

class DashboardWindow(QWidget):
    def __init__(self, token):
        super().__init__()
        self.token = token

        self.setWindowTitle("Bienestar - Dashboard")
        self.setFixedSize(400, 250)

        layout = QVBoxLayout()

        self.label = QLabel("Bienvenida al Dashboard 🎉")

        self.token_button = QPushButton("Mostrar token en consola")
        self.token_button.clicked.connect(self.show_token)

        self.api_button = QPushButton("Consultar endpoint protegido")
        self.api_button.clicked.connect(self.call_api)

        layout.addWidget(self.label)
        layout.addWidget(self.token_button)
        layout.addWidget(self.api_button)

        self.setLayout(layout)

    def show_token(self):
        print("TOKEN ACTUAL:", self.token)

    def call_api(self):
        try:
            headers = {
                "Authorization": f"Bearer {self.token}"
            }

            response = requests.get(PROTECTED_URL, headers=headers)

            print("STATUS:", response.status_code)
            print("DATA:", response.text)

            if response.status_code == 200:
                QMessageBox.information(self, "Éxito", "Consulta exitosa ✅")
            else:
                QMessageBox.warning(self, "Error", f"Error:\n{response.text}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{e}")


# -----------------------
# LOGIN WINDOW
# -----------------------

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienestar - Login")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Iniciar sesión")
        self.login_button.clicked.connect(self.login)

        layout.addWidget(QLabel("Correo"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Contraseña"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return

        try:
            response = requests.post(
                API_URL,
                json={
                    "email": email,
                    "password": password
                }
            )

            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)

            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access")

                QMessageBox.information(self, "Éxito", "Login correcto 🎉")

                # Abrir Dashboard
                self.dashboard = DashboardWindow(access_token)
                self.dashboard.show()

                # Cerrar Login
                self.close()

            elif response.status_code == 401:
                QMessageBox.warning(self, "Error", "Correo o contraseña incorrectos")

            else:
                QMessageBox.critical(self, "Error", f"Error:\n{response.text}")

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error", "No se pudo conectar al servidor.\n¿Está Django ejecutándose?")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{e}")


# -----------------------
# MAIN
# -----------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
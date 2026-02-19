import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)


API_URL = "http://127.0.0.1:8000/api/token/"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienestar - Login")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo")

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
            
        try:
            response = requests.get("http://localhost:8000/")
            print("STATUS CODE:", response.status_code)
            QMessageBox.information(self, "Conexión", "Conexión exitosa al servidor")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar\n{e}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

# styles.py
# Importa este archivo en login.py y dashboard.py:
# from styles import STYLE_GLOBAL

STYLE_GLOBAL = """
/* ── Ventana base ─────────────────────────────── */
QWidget {
    background-color: #f0f7f2;
    color: #1a2e22;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

/* ── Labels ───────────────────────────────────── */
QLabel {
    color: #2d4a38;
    font-size: 13px;
}

QLabel#titulo {
    font-size: 22px;
    font-weight: bold;
    color: #1a7a4a;
}

QLabel#subtitulo {
    font-size: 12px;
    color: #6b8f77;
}

QLabel#status {
    font-size: 11px;
    color: #6b8f77;
}

/* ── Inputs ───────────────────────────────────── */
QLineEdit {
    background-color: #ffffff;
    border: 1.5px solid #b8d9c5;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: #1a2e22;
    selection-background-color: #4caf82;
}

QLineEdit:focus {
    border: 1.5px solid #2e9e62;
    background-color: #f7fff9;
}

QLineEdit:hover {
    border: 1.5px solid #80c9a0;
}

QLineEdit::placeholder {
    color: #a0bfac;
}

/* ── Botón primario ───────────────────────────── */
QPushButton#btn_primary {
    background-color: #2e9e62;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 11px 20px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#btn_primary:hover {
    background-color: #268a55;
}

QPushButton#btn_primary:pressed {
    background-color: #1e7044;
}

QPushButton#btn_primary:disabled {
    background-color: #9ecfb5;
    color: #d0ead9;
}

/* ── Botón secundario ─────────────────────────── */
QPushButton#btn_secondary {
    background-color: transparent;
    color: #2e9e62;
    border: 1.5px solid #2e9e62;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton#btn_secondary:hover {
    background-color: #e8f7ef;
}

QPushButton#btn_secondary:disabled {
    color: #9ecfb5;
    border-color: #9ecfb5;
}

/* ── Tarjeta (frame con fondo blanco) ─────────── */
QFrame#card {
    background-color: #ffffff;
    border-radius: 16px;
    border: 1px solid #d4ead9;
}

/* ── Lista ────────────────────────────────────── */
QListWidget {
    background-color: #ffffff;
    border: 1.5px solid #b8d9c5;
    border-radius: 12px;
    padding: 6px;
    outline: none;
}

QListWidget::item {
    padding: 10px 12px;
    border-radius: 8px;
    color: #1a2e22;
    margin: 2px 0;
}

QListWidget::item:selected {
    background-color: #d6f0e3;
    color: #1a7a4a;
}

QListWidget::item:hover {
    background-color: #eef7f2;
}

/* ── Scrollbar ────────────────────────────────── */
QScrollBar:vertical {
    background: #f0f7f2;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #b8d9c5;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #2e9e62;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ── MessageBox ───────────────────────────────── */
QMessageBox {
    background-color: #f0f7f2;
}

QMessageBox QPushButton {
    background-color: #2e9e62;
    color: white;
    border-radius: 8px;
    padding: 6px 18px;
    font-weight: bold;
    min-width: 70px;
}

QMessageBox QPushButton:hover {
    background-color: #268a55;
}
"""
# main.py

import sys
import multiprocessing
from PyQt5.QtWidgets import QApplication
from gui import VentanaPrincipal

if __name__ == '__main__':
    multiprocessing.freeze_support()  # Necesario para Windows
    app = QApplication(sys.argv)

    # Cargar y aplicar la hoja de estilo
    with open("style.qss", "r") as f:
        style = f.read()
        app.setStyleSheet(style)

    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())

import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("BACK UP - DJ ROBERTO RIVERA")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

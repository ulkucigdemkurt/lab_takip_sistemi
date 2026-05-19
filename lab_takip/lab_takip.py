
import sys
from PyQt5.QtWidgets import QApplication
from ana_pencere import AnaPencere

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = AnaPencere()
    w.show()
    sys.exit(app.exec_())

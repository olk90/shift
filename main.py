import sys

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QWidget

from logic.database import init_database
from views.mainView import MainWindow

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)

    init_database()

    app = QApplication()
    form = QWidget(None)
    MainWindow(form)
    form.show()
    sys.exit(app.exec())

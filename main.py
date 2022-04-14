import locale
import sys

import qdarktheme
from PySide6 import QtCore
from PySide6.QtCore import QTranslator, QLocale
from PySide6.QtWidgets import QApplication, QWidget

from logic.config import properties
from logic.database import init_database
from views.mainView import MainWindow

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)

    init_database()
    properties.load_config_file()

    app = QApplication()

    translator = QTranslator(app)
    path = './translations'
    if properties.locale_index == 1:
        translator.load(QLocale(QLocale.German, QLocale.Germany), 'base', '_', path)
        locale.setlocale(locale.LC_TIME, "de_DE.utf8")
        app.installTranslator(translator)

    if properties.theme_index == 0:
        app.setStyleSheet(qdarktheme.load_stylesheet())
    elif properties.theme_index == 1:
        app.setStyleSheet(qdarktheme.load_stylesheet("light"))
    else:
        print("Use system style sheet")
        app.setStyleSheet(None)

    form = QWidget(None)
    MainWindow(form)
    form.show()
    sys.exit(app.exec())

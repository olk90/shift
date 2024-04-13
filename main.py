import locale
import sys

import qdarktheme
from PySide6 import QtCore
from PySide6.QtCore import QTranslator, QLocale
from PySide6.QtWidgets import QApplication, QWidget

from logic.config import properties
from logic.database import init_database, cleanup_database
from views.mainView import MainWindow


def load_translations():
    translator = QTranslator(app)
    path = './translations'
    if properties.locale_index == 1:
        translator.load(QLocale(QLocale.German, QLocale.Germany), 'base', '_', path)
        locale.setlocale(locale.LC_TIME, "de_DE.utf8")
        app.installTranslator(translator)


def load_theme():
    if properties.theme_index == 0:
        app.setStyleSheet(qdarktheme.load_stylesheet())
    elif properties.theme_index == 1:
        app.setStyleSheet(qdarktheme.load_stylesheet("light"))


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication()

    properties.load_config_file()
    init_database()

    load_translations()
    load_theme()
    cleanup_database()

    form = QWidget(None)
    MainWindow(form)
    form.show()
    sys.exit(app.exec())

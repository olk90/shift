import sys
from typing import Union

from PySide6.QtCore import QFile, QCoreApplication, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QItemDelegate, QStyleOptionViewItem, QStyleOptionButton


def load_ui_file(filename):
    ui_file = QFile(filename)
    if not ui_file.open(QFile.ReadOnly):
        print("Cannot open {}: {}".format(filename, ui_file.errorString()))
        sys.exit(-1)
    return ui_file


def translate(context, text):
    return QCoreApplication.translate(context, text, None)


class CenteredItemDelegate(QItemDelegate):

    def __init__(self):
        super(CenteredItemDelegate, self).__init__()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: Union[QModelIndex, QPersistentModelIndex]):
        option.displayAlignment = Qt.AlignCenter
        super(CenteredItemDelegate, self).paint(painter, option, index)


class EmployeeItemDelegate(CenteredItemDelegate):

    def __init__(self):
        super(EmployeeItemDelegate, self).__init__()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: Union[QModelIndex, QPersistentModelIndex]):
        if index.column() == 4:
            model = index.model()
            data = model.index(index.row(), index.column()).data()
            opt: QStyleOptionButton = QStyleOptionButton()
            opt.rect = option.rect
            if data:
                value = Qt.Checked
            else:
                value = Qt.Unchecked
            self.drawCheck(painter, option, option.rect, value)
            self.drawFocus(painter, option, option.rect)
        else:
            super(EmployeeItemDelegate, self).paint(painter, option, index)

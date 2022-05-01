import datetime
from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QPainter, QColor, QBrush
from PySide6.QtWidgets import QItemDelegate, QStyleOptionViewItem, QStyleOptionButton

from logic.config import properties


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


class OffPeriodItemDelegate(CenteredItemDelegate):

    def __init__(self):
        super(OffPeriodItemDelegate, self).__init__()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: Union[QModelIndex, QPersistentModelIndex]):
        model = index.model()
        if index.column() in [1, 2]:
            date_str: str = model.index(index.row(), index.column()).data()
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            text = date.strftime("%a, %d %b %Y")
            option.displayAlignment = Qt.AlignCenter
            self.drawDisplay(painter, option, option.rect, text)
        else:
            super(OffPeriodItemDelegate, self).paint(painter, option, index)


class ScheduleItemDelegate(CenteredItemDelegate):

    def __init__(self):
        super(ScheduleItemDelegate, self).__init__()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: Union[QModelIndex, QPersistentModelIndex]):
        model = index.model()
        date_str: str = model.index(index.row(), 1).data()
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        if date.weekday() > 3:
            theme: int = properties.theme_index
            color: QColor = QColor("#3f4042") if theme == 0 else QColor("#dadce0")
            brush: QBrush = QBrush(color)
            painter.setBrush(brush)
            # TODO the borders still need a bit tweaking
            painter.drawRect(option.rect)
        if index.column() == 1:
            text = date.strftime("%a, %d %b %Y")
            option.displayAlignment = Qt.AlignCenter
            self.drawDisplay(painter, option, option.rect, text)
        else:
            super(ScheduleItemDelegate, self).paint(painter, option, index)

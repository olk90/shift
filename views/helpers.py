import calendar
import sys
import datetime
from typing import Union

from PySide6.QtCore import QFile, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtWidgets import QItemDelegate, QStyleOptionViewItem, QStyleOptionButton, QComboBox, QWidget, QSpinBox

from logic.config import properties


def load_ui_file(filename):
    ui_file = QFile(filename)
    if not ui_file.open(QFile.ReadOnly):
        print("Cannot open {}: {}".format(filename, ui_file.errorString()))
        sys.exit(-1)
    return ui_file


def configure_month_box(parent: QWidget, month_box: QComboBox):
    months: list = [
        parent.tr("January"),
        parent.tr("February"),
        parent.tr("March"),
        parent.tr("April"),
        parent.tr("May"),
        parent.tr("June"),
        parent.tr("July"),
        parent.tr("August"),
        parent.tr("September"),
        parent.tr("October"),
        parent.tr("November"),
        parent.tr("December")
    ]
    month_box.addItems(months)
    date = datetime.date.today()
    month: int = date.month - 1  # indices start at 0!
    month_box.setCurrentIndex(month)


def configure_weekday_box(parent: QWidget, weekday_box: QComboBox):
    months: list = [
        parent.tr("Monday"),
        parent.tr("Tuesday"),
        parent.tr("Wednesday"),
        parent.tr("Thursday"),
        parent.tr("Friday"),
        parent.tr("Saturday"),
        parent.tr("Sunday")
    ]
    weekday_box.addItems(months)
    date = datetime.date.today()
    day: int = date.day - 1  # indices start at 0!
    weekday_box.setCurrentIndex(day)


def configure_year_box(year_box: QSpinBox):
    date = datetime.date.today()
    year: int = date.year
    year_box.setMinimum(year)
    year_box.setValue(year)
    year_box.setMaximum(9999)


def get_day_range(month: int, year: int):
    start_day = datetime.date(year, month, 1).day
    end_day = calendar.monthrange(year, month)[1]
    day_range = range(start_day, end_day + 1)
    return day_range


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

import calendar
import datetime
import sys

from PySide6.QtCore import QFile
from PySide6.QtWidgets import QComboBox, QSpinBox

from views.lists import MonthList, WeekdayList


def load_ui_file(filename):
    ui_file = QFile(filename)
    if not ui_file.open(QFile.ReadOnly):
        print("Cannot open {}: {}".format(filename, ui_file.errorString()))
        sys.exit(-1)
    return ui_file


def configure_month_box(month_box: QComboBox):
    items = MonthList().months
    month_box.addItems(items)
    date = datetime.date.today()
    month: int = date.month - 1  # indices start at 0!
    month_box.setCurrentIndex(month)


def configure_weekday_box(weekday_box: QComboBox):
    items = WeekdayList().weekdays
    weekday_box.addItems(items)
    date = datetime.date.today()
    day: int = date.day - 1  # indices start at 0!
    weekday_box.setCurrentIndex(day)


def configure_year_box(year_box: QSpinBox):
    date = datetime.date.today()
    year: int = date.year
    year_box.setMinimum(year)
    year_box.setValue(year)
    year_box.setMaximum(9999)


def get_day_range(month: int, year: int) -> range:
    end_day = calendar.monthrange(year, month)[1]
    day_range = range(1, end_day + 1)
    return day_range

import calendar
import datetime
import sys

from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication, QComboBox, QSpinBox


def load_ui_file(filename):
    ui_file = QFile(filename)
    if not ui_file.open(QFile.ReadOnly):
        print("Cannot open {}: {}".format(filename, ui_file.errorString()))
        sys.exit(-1)
    return ui_file


def configure_month_box(app: QApplication, month_box: QComboBox):
    months: list = [
        app.translate("app", "January"),
        app.translate("app", "February"),
        app.translate("app", "March"),
        app.translate("app", "April"),
        app.translate("app", "May"),
        app.translate("app", "June"),
        app.translate("app", "July"),
        app.translate("app", "August"),
        app.translate("app", "September"),
        app.translate("app", "October"),
        app.translate("app", "November"),
        app.translate("app", "December")
    ]
    month_box.addItems(months)
    date = datetime.date.today()
    month: int = date.month - 1  # indices start at 0!
    month_box.setCurrentIndex(month)


def configure_weekday_box(app: QApplication, weekday_box: QComboBox):
    months: list = [
        app.translate("app", "Monday"),
        app.translate("app", "Tuesday"),
        app.translate("app", "Wednesday"),
        app.translate("app", "Thursday"),
        app.translate("app", "Friday"),
        app.translate("app", "Saturday"),
        app.translate("app", "Sunday")
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

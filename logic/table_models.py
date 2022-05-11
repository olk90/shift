from datetime import datetime

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import Qt
from PySide6.QtSql import QSqlQueryModel
from xlsxwriter import Workbook
from xlsxwriter.format import Format

from logic.queries import employee_type_query, employee_query, off_period_query, schedule_query


class SearchTableModel(QSqlQueryModel):
    def __init__(self, search: str = ""):
        super(SearchTableModel, self).__init__()
        self.search = search


class EmployeeTypeModel(SearchTableModel):
    def __init__(self, search: str = ""):
        super(EmployeeTypeModel, self).__init__(search)
        query = employee_type_query(self.search)
        self.setQuery(query)
        self.setHeaderData(0, Qt.Horizontal, "ID")
        self.setHeaderData(1, Qt.Horizontal, self.tr("Designation"))
        self.setHeaderData(2, Qt.Horizontal, self.tr("Rotation Period"))


class EmployeeModel(SearchTableModel):
    def __init__(self, search: str = ""):
        super(EmployeeModel, self).__init__(search)
        query = employee_query(self.search)
        self.setQuery(query)
        self.setHeaderData(0, Qt.Horizontal, "ID")
        self.setHeaderData(1, Qt.Horizontal, self.tr("First Name"))
        self.setHeaderData(2, Qt.Horizontal, self.tr("Last Name"))
        self.setHeaderData(3, Qt.Horizontal, self.tr("Reference Value"))
        self.setHeaderData(4, Qt.Horizontal, self.tr("Night Shifts"))
        self.setHeaderData(5, Qt.Horizontal, self.tr("Score"))
        self.setHeaderData(6, Qt.Horizontal, self.tr("Type"))


class OffPeriodModel(SearchTableModel):
    def __init__(self, search: str = ""):
        super(OffPeriodModel, self).__init__(search)
        query = off_period_query(self.search)
        self.setQuery(query)
        self.setHeaderData(0, Qt.Horizontal, "ID")
        self.setHeaderData(1, Qt.Horizontal, self.tr("Start"))
        self.setHeaderData(2, Qt.Horizontal, self.tr("End"))
        self.setHeaderData(3, Qt.Horizontal, self.tr("Employee"))


class ScheduleModel(SearchTableModel):
    def __init__(self, year: int, month: int, search: str = ""):
        super(ScheduleModel, self).__init__(search)

        self.year: int = year
        self.month: int = month

        query = schedule_query(year, month, self.search)
        self.setQuery(query)
        self.setHeaderData(0, Qt.Horizontal, "ID")
        self.setHeaderData(1, Qt.Horizontal, self.tr("Date"))
        self.setHeaderData(2, Qt.Horizontal, self.tr("Day Shift"))
        self.setHeaderData(3, Qt.Horizontal, self.tr("Night Shift"))
        self.setHeaderData(4, Qt.Horizontal, self.tr("Comment"))

    def export_schedule(self, file_path: str, root_index: QModelIndex):
        wb = Workbook(file_path)
        bold: Format = wb.add_format({"bold": True})
        weekend: Format = wb.add_format({"bg_color": "#dadce0"})
        ws = wb.add_worksheet("{month}-{year}".format(month=self.month, year=self.year))
        ws.write("A1", self.tr("Date"), bold)
        ws.write("B1", self.tr("Day Shift"), bold)
        ws.write("C1", self.tr("Night Shift"), bold)
        ws.write("D1", self.tr("Comment"), bold)
        for row in range(self.rowCount(root_index)):
            use_weekend = False
            for column in range(1, 5):
                content = self.index(row, column, root_index).data()
                if column == 1:
                    date_ = datetime.strptime(content, "%Y-%m-%d")
                    content = date_.strftime("%a, %d %b %Y")
                    use_weekend = date_.weekday() > 3
                if use_weekend:
                    ws.write(row + 1, column - 1, content, weekend)
                else:
                    ws.write(row + 1, column - 1, content)
        wb.close()

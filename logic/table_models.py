from datetime import datetime

from PySide6.QtCore import QModelIndex, QAbstractTableModel
from PySide6.QtGui import Qt
from xlsxwriter import Workbook
from xlsxwriter.format import Format

from logic.config import properties
from logic.crypt import decrypt_string
from logic.database import find_all_off, find_by_id
from logic.model import Employee, EmployeeType, OffPeriod, Schedule


class SearchTableModel(QAbstractTableModel):
    def __init__(self, col_count, search: str = "", items=None):
        super(SearchTableModel, self).__init__()
        self.col_count = col_count
        self.search = search
        if items is None:
            items = []
        self.items = items

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def columnCount(self, parent=QModelIndex()):
        return self.col_count

    def data(self, index, role=Qt.DisplayRole):
        """Must be implemented by subclass"""
        pass

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Must be implemented by subclass"""
        pass


class EmployeeTypeModel(SearchTableModel):
    def __init__(self, search: str = ""):
        items = find_all_off(EmployeeType)
        super(EmployeeTypeModel, self).__init__(3, search, items)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            employee_type: EmployeeType = self.items[index.row()]
            column = index.column()
            if column == 0:
                return employee_type.id
            elif column == 1:
                return employee_type.designation
            elif column == 2:
                return employee_type.rotation_period
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return "ID"
            elif section == 1:
                return self.tr("Designation")
            elif section == 2:
                return self.tr("Rotation Period")
        return None


class EmployeeModel(SearchTableModel):
    def __init__(self, search: str = ""):
        items = find_all_off(Employee)
        super(EmployeeModel, self).__init__(7, search, items)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            employee: Employee = self.items[index.row()]
            column = index.column()
            key = properties.encryption_key
            if column == 0:
                return employee.id
            elif column == 1:
                if key is not None:
                    return decrypt_string(key, employee.firstname)
                else:
                    return employee.firstname
            elif column == 2:
                if key is not None:
                    return decrypt_string(key, employee.lastname)
                else:
                    return employee.lastname
            elif column == 3:
                return employee.reference_value
            elif column == 4:
                return employee.night_shifts
            elif column == 5:
                return employee.score
            elif column == 6:
                et: EmployeeType = find_by_id(employee.e_type_id, EmployeeType)
                return et.designation
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return "ID"
            elif section == 1:
                return self.tr("First Name")
            elif section == 2:
                return self.tr("Last Name")
            elif section == 3:
                return self.tr("Reference Value")
            elif section == 4:
                return self.tr("Night Shifts")
            elif section == 5:
                return self.tr("Score")
            elif section == 6:
                return self.tr("Type")
        return None


class OffPeriodModel(SearchTableModel):
    def __init__(self, year: int, month: int, search: str = ""):
        items = find_all_off(OffPeriod)
        super(OffPeriodModel, self).__init__(4, search, items)

        self.year: int = year
        self.month: int = month

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            period: OffPeriod = self.items[index.row()]
            column = index.column()
            if column == 0:
                return period.id
            elif column == 1:
                return period.start
            elif column == 2:
                return period.end
            elif column == 3:
                employee: Employee = find_by_id(period.e_id, Employee)
                return employee.get_full_name()
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return "ID"
            elif section == 1:
                return self.tr("Start")
            elif section == 2:
                return self.tr("End")
            elif section == 3:
                return self.tr("Employee")
        return None


class ScheduleModel(SearchTableModel):
    def __init__(self, year: int, month: int, search: str = ""):
        items = find_all_off(Schedule)
        super(ScheduleModel, self).__init__(5, search, items)

        self.year: int = year
        self.month: int = month

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            schedule: Schedule = self.items[index.row()]
            column = index.column()
            if column == 0:
                return schedule.id
            elif column == 1:
                return schedule.date
            elif column == 2:
                return schedule.day_id
            elif column == 3:
                return schedule.night_id
            elif column == 4:
                return schedule.comment
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return "ID"
            elif section == 1:
                return self.tr("Date")
            elif section == 2:
                return self.tr("Day Shift")
            elif section == 3:
                return self.tr("Night Shift")
            elif section == 4:
                return self.tr("Comment")
        return None

    def export_schedule(self, file_path: str, root_index: QModelIndex):
        wb = Workbook(file_path)
        bold: Format = wb.add_format({"bold": True})
        weekend: Format = wb.add_format({"bg_color": "#dadce0"})
        ws = wb.add_worksheet("{month}-{year}".format(month=self.month, year=self.year))
        ws.write("A1", self.tr("Date"), bold)
        ws.write("B1", self.tr("Day Shift"), bold)
        ws.write("C1", self.tr("Night Shift"), bold)
        ws.write("D1", self.tr("Comment"), bold)
        for row in range(self.rowCount()):
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

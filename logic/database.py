import sys
from datetime import datetime

from PySide6.QtCore import QDate
from PySide6.QtGui import Qt
from PySide6.QtSql import QSqlQueryModel, QSqlDatabase
from PySide6.QtWidgets import QComboBox
from sqlalchemy import create_engine as ce, desc
from sqlalchemy.orm import sessionmaker as sm, join

from logic.model import create_tables, Employee, EmployeeType, OffPeriod, Schedule
from logic.queries import build_employee_query, build_employee_type_query, build_off_period_query, build_schedule_query

db = ce("sqlite:///shift.db")


def init_database():
    print("Connecting to database {}".format(db))
    db.connect()

    print("Initializing database")
    create_tables(db)

    print("Connect database to PySide")
    database = QSqlDatabase.addDatabase("QSQLITE")
    database.setDatabaseName("shift.db")

    if not database.open():
        print("Unable to open database")
        sys.exit(1)


class SearchTableModel(QSqlQueryModel):
    def __init__(self, search: str = ""):
        super(SearchTableModel, self).__init__()
        self.search = search


class EmployeeTypeModel(SearchTableModel):
    def __init__(self, search: str = ""):
        super(EmployeeTypeModel, self).__init__(search)
        query = build_employee_type_query(self.search)
        self.setQuery(query)
        self.setHeaderData(0, Qt.Horizontal, "ID")
        self.setHeaderData(1, Qt.Horizontal, self.tr("Designation"))
        self.setHeaderData(2, Qt.Horizontal, self.tr("Rotation Period"))


class EmployeeModel(SearchTableModel):
    def __init__(self, search: str = ""):
        super(EmployeeModel, self).__init__(search)
        query = build_employee_query(self.search)
        self.setQuery(query)
        self.setHeaderData(0, Qt.Horizontal, "ID")
        self.setHeaderData(1, Qt.Horizontal, self.tr("First Name"))
        self.setHeaderData(2, Qt.Horizontal, self.tr("Last Name"))
        self.setHeaderData(3, Qt.Horizontal, self.tr("Reference Value"))
        self.setHeaderData(4, Qt.Horizontal, self.tr("Night Shifts"))
        self.setHeaderData(5, Qt.Horizontal, self.tr("Penalty"))
        self.setHeaderData(6, Qt.Horizontal, self.tr("Type"))


class OffPeriodModel(SearchTableModel):
    def __init__(self, search: str = ""):
        super(OffPeriodModel, self).__init__(search)
        query = build_off_period_query(self.search)
        self.setQuery(query)
        self.setHeaderData(0, Qt.Horizontal, "ID")
        self.setHeaderData(1, Qt.Horizontal, self.tr("Start"))
        self.setHeaderData(2, Qt.Horizontal, self.tr("End"))
        self.setHeaderData(3, Qt.Horizontal, self.tr("Employee"))


class ScheduleModel(SearchTableModel):
    def __init__(self, year: int, month: int, search: str = ""):
        super(ScheduleModel, self).__init__(search)
        query = build_schedule_query(year, month, self.search)
        self.setQuery(query)
        self.setHeaderData(0, Qt.Horizontal, "ID")
        self.setHeaderData(1, Qt.Horizontal, self.tr("Date"))
        self.setHeaderData(2, Qt.Horizontal, self.tr("Day Shift"))
        self.setHeaderData(3, Qt.Horizontal, self.tr("Night Shift"))
        self.setHeaderData(4, Qt.Horizontal, self.tr("Comment"))


def configure_query_model(box: QComboBox, query: str):
    model = QSqlQueryModel(box)
    model.setQuery(query)
    model.setHeaderData(0, Qt.Horizontal, "Name")
    box.setModel(model)
    box.setEditable(True)


def persist_employee_type(employee_type: EmployeeType):
    session = sm(bind=db)
    s = session()
    s.add(employee_type)
    s.commit()


def find_employee_types() -> list:
    session = sm(bind=db)
    s = session()
    types = s.query(EmployeeType).all()
    s.close()
    return types


def persist_employee(employee: Employee):
    session = sm(bind=db)
    s = session()
    s.add(employee)
    s.commit()


def find_employee_type_by_id(e_id: int) -> EmployeeType:
    session = sm(bind=db)
    s = session()
    e_type: EmployeeType = s.query(EmployeeType).filter_by(id=e_id).first()
    s.close()
    return e_type


def find_employee_by_id(e_id: int) -> Employee:
    session = sm(bind=db)
    s = session()
    employee: Employee = s.query(Employee).filter_by(id=e_id).first()
    s.close()
    return employee


def update_employee_type(value_dict: dict):
    session = sm(bind=db)
    s = session()
    e_type: EmployeeType = s.query(EmployeeType).filter_by(id=value_dict["item_id"]).first()
    e_type.designation = value_dict["designation"]
    e_type.rotation_period = value_dict["rotation_period"]
    s.commit()


def find_e_type_by_e_id(e_id: int) -> EmployeeType:
    session = sm(bind=db)
    s = session()
    e_type: EmployeeType = s.query(EmployeeType).select_from(join(EmployeeType, Employee)).filter(
        Employee.id == e_id).first()
    s.close()
    return e_type


def delete_employee_type(e_type: EmployeeType):
    session = sm(bind=db)
    s = session()
    s.delete(e_type)
    s.commit()


def update_employee(value_dict: dict):
    session = sm(bind=db)
    s = session()
    employee: Employee = s.query(Employee).filter_by(id=value_dict["item_id"]).first()
    employee.firstname = value_dict["firstname"]
    employee.lastname = value_dict["lastname"]
    employee.referenceValue = value_dict["reference_value"]
    employee.penalty = value_dict["penalty"]
    employee.night_shifts = value_dict["night_shifts"]
    e_type = s.query(EmployeeType).filter_by(designation=value_dict["e_type"]).one()
    employee.e_type = e_type
    s.commit()


def delete_employee(employee: Employee):
    session = sm(bind=db)
    s = session()
    s.delete(employee)
    s.commit()


def find_off_period_by_id(p_id: int) -> OffPeriod:
    session = sm(bind=db)
    s = session()
    period: OffPeriod = s.query(OffPeriod).filter_by(id=p_id).first()
    s.close()
    return period


def update_off_period(value_dict: dict):
    session = sm(bind=db)
    s = session()
    period: OffPeriod = s.query(OffPeriod).filter_by(id=value_dict["item_id"]).first()
    q_start: QDate = value_dict["start"]
    q_end: QDate = value_dict["end"]
    period.start = datetime(q_start.year(), q_start.month(), q_start.day())
    period.end = datetime(q_end.year(), q_end.month(), q_end.day())
    s.commit()


def persist_off_period(period: OffPeriod):
    session = sm(bind=db)
    s = session()
    s.add(period)
    s.commit()


def delete_off_period(period: OffPeriod):
    session = sm(bind=db)
    s = session()
    s.delete(period)
    s.commit()


def persist_schedule(schedule: Schedule):
    session = sm(bind=db)
    s = session()
    s.add(schedule)
    s.commit()


def get_day_shift_candidates() -> list:
    session = sm(bind=db)
    s = session()
    employees: list = s.query(Employee).order_by(desc(Employee.penalty), desc(Employee.referenceValue)).all()
    s.close()
    return employees


def get_night_shift_candidates() -> list:
    session = sm(bind=db)
    s = session()
    employees: list = s.query(Employee)\
        .filter_by(night_shifts=True) \
        .order_by(desc(Employee.penalty), desc(Employee.referenceValue)).all()
    s.close()
    return employees

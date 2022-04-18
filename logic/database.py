import sys
from datetime import datetime, date

from PySide6.QtCore import QDate
from PySide6.QtGui import Qt
from PySide6.QtSql import QSqlQueryModel, QSqlDatabase
from PySide6.QtWidgets import QComboBox
from sqlalchemy import create_engine as ce, desc, asc
from sqlalchemy.orm import sessionmaker as sm, join

from logic.model import create_tables, Employee, EmployeeType, OffPeriod, Schedule, Base
from logic.queries import employee_query, employee_type_query, off_period_query, schedule_query

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
        query = schedule_query(year, month, self.search)
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


def find_employee_types() -> list:
    session = sm(bind=db)
    s = session()
    types = s.query(EmployeeType).all()
    s.close()
    return types


def persist_item(item: Base):
    session = sm(bind=db)
    s = session()
    s.add(item)
    s.commit()


def delete_item(item: Base):
    session = sm(bind=db)
    s = session()
    s.delete(item)
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


def update_employee(value_dict: dict):
    session = sm(bind=db)
    s = session()
    employee: Employee = s.query(Employee).filter_by(id=value_dict["item_id"]).first()
    employee.firstname = value_dict["firstname"]
    employee.lastname = value_dict["lastname"]
    employee.referenceValue = value_dict["reference_value"]
    employee.global_score = value_dict["global_score"]
    employee.night_shifts = value_dict["night_shifts"]
    e_type = s.query(EmployeeType).filter_by(designation=value_dict["e_type"]).one()
    employee.e_type = e_type
    s.commit()


def reset_scores():
    session = sm(bind=db)
    s = session()
    employees: list = s.query(Employee).all()
    for e in employees:
        e.score = 0
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


def update_schedule(value_dict: dict):
    session = sm(bind=db)
    s = session()
    schedule: Schedule = s.query(Schedule).filter_by(id=value_dict["item_id"]).first()
    s_date = schedule.date
    new_day_id: int = value_dict["d_id"]
    new_night_id: int = value_dict["n_id"]
    if schedule.activated:
        current_day_id: int = schedule.day_id
        update_global_score(s, current_day_id, new_day_id, s_date)

        current_night_id: int = schedule.night_id
        update_global_score(s, current_night_id, new_night_id, s_date)
    else:
        if new_day_id is not None:
            update_score(s, new_day_id, s_date)
        if new_night_id is not None:
            update_score(s, new_night_id, s_date)
    schedule.day_id = new_day_id
    schedule.night_id = new_night_id
    schedule.comment = value_dict["comment"]
    s.commit()


def update_global_score(s, current_id: int, new_id: int, s_date: date):
    score_offset: int = 2 if s_date.weekday() > 3 else 1
    off_period_bonus: int = 3
    if current_id != new_id:
        current_night: Employee = s.query(Employee).filter_by(id=current_id).first()
        new_night: Employee = s.query(Employee).filter_by(id=new_id).first()
        if current_night:
            current_night.global_score -= score_offset
        if new_night:
            if new_night.has_off_period(s_date):
                new_night.global_score += off_period_bonus
            else:
                new_night.global_score += score_offset


def update_score(s, e_id: int, s_date: date):
    score_offset: int = 10 if s_date.weekday() > 3 else 1
    employee: Employee = s.query(Employee).filter_by(id=e_id).first()
    employee.score += score_offset


def find_schedule_by_id(s_id: int) -> Schedule:
    session = sm(bind=db)
    s = session()
    schedule: Schedule = s.query(Schedule).filter_by(id=s_id).first()
    s.close()
    return schedule


def find_schedule_by_date(d: datetime.date) -> Schedule:
    session = sm(bind=db)
    s = session()
    schedule: Schedule = s.query(Schedule).filter_by(date=d).first()
    s.close()
    return schedule


def schedule_exists(year: int, month: int) -> bool:
    session = sm(bind=db)
    s = session()
    start_day = date(year, month, 1)
    schedule: Schedule = s.query(Schedule).filter_by(date=start_day).first()
    s.close()
    return schedule is not None


def shift_plan_active(year: int, month: int) -> bool:
    session = sm(bind=db)
    s = session()
    start_day = date(year, month, 1)
    schedule: Schedule = s.query(Schedule).filter_by(date=start_day).first()
    s.close()
    return schedule is not None and schedule.activated


def find_day_shift_candidate_ids(day: date) -> list:
    session = sm(bind=db)
    s = session()
    employees: list = s.query(Employee).order_by(asc(Employee.score), desc(Employee.referenceValue)).all()
    filtered = filter(lambda e: not e.has_off_period(day), employees)
    ids = [e.id for e in filtered]
    s.close()
    return ids


def find_night_shift_candidate_ids(day: date) -> list:
    session = sm(bind=db)
    s = session()
    employees: list = s.query(Employee).filter_by(night_shifts=True) \
        .order_by(asc(Employee.score),
                  desc(Employee.referenceValue)).all()
    filtered = filter(lambda e: not e.has_off_period(day), employees)
    ids = [e.id for e in filtered]
    s.close()
    return ids

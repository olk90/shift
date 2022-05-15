import logging
import sys
from datetime import datetime, date, timedelta
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import QDate
from PySide6.QtGui import Qt
from PySide6.QtSql import QSqlQueryModel, QSqlDatabase
from PySide6.QtWidgets import QComboBox
from sqlalchemy import create_engine as ce, and_, extract, or_

from logic import configure_file_handler
from logic.config import properties
from logic.model import create_tables, Employee, EmployeeType, OffPeriod, Schedule, Base

rfh: RotatingFileHandler = configure_file_handler("database")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(rfh)

logger.info("Logger initialised")


def init_database(remove_old: bool = False):
    db = ce("sqlite:///" + properties.database_path)
    logger.info("Connecting to database %s", db)
    db.connect()

    logger.info("Initialising database")
    create_tables(db)

    logger.info("Connect database to PySide")

    if remove_old:
        QSqlDatabase.removeDatabase("QSQLITE")
    database = QSqlDatabase.addDatabase("QSQLITE")
    database.setDatabaseName(properties.database_path)

    if not database.open():
        logger.error("Unable to open database")
        sys.exit(1)


def configure_query_model(box: QComboBox, query: str):
    model = QSqlQueryModel(box)
    model.setQuery(query)
    model.setHeaderData(0, Qt.Horizontal, "Name")
    box.setModel(model)
    box.setEditable(True)


def persist_item(item: Base):
    s = properties.open_session()
    s.add(item)
    s.commit()
    logger.info("Added new item to database: %s", item)


def delete_item(item: Base):
    s = properties.open_session()
    s.delete(item)
    s.commit()
    logger.info("Removed entry from database: %s", item)


def find_employee_type_by_id(e_id: int) -> EmployeeType:
    s = properties.open_session()
    e_type: EmployeeType = s.query(EmployeeType).filter_by(id=e_id).first()
    s.close()
    return e_type


def find_employee_by_id(e_id: int) -> Employee:
    s = properties.open_session()
    employee: Employee = s.query(Employee).filter_by(id=e_id).first()
    s.close()
    return employee


def update_employee_type(value_dict: dict):
    s = properties.open_session()
    e_type: EmployeeType = s.query(EmployeeType).filter_by(id=value_dict["item_id"]).first()
    e_type.designation = value_dict["designation"]
    e_type.rotation_period = value_dict["rotation_period"]
    s.commit()


def update_employee(value_dict: dict):
    s = properties.open_session()
    employee: Employee = s.query(Employee).filter_by(id=value_dict["item_id"]).first()
    employee.firstname = value_dict["firstname"]
    employee.lastname = value_dict["lastname"]
    employee.reference_value = value_dict["reference_value"]
    employee.score = value_dict["score"]
    employee.night_shifts = value_dict["night_shifts"]
    e_type = s.query(EmployeeType).filter_by(designation=value_dict["e_type"]).one()
    employee.e_type = e_type
    s.commit()


def find_off_period_by_id(p_id: int) -> OffPeriod:
    s = properties.open_session()
    period: OffPeriod = s.query(OffPeriod).filter_by(id=p_id).first()
    s.close()
    return period


def update_off_period(value_dict: dict):
    s = properties.open_session()
    period: OffPeriod = s.query(OffPeriod).filter_by(id=value_dict["item_id"]).first()
    q_start: QDate = value_dict["start"]
    q_end: QDate = value_dict["end"]
    period.start = datetime(q_start.year(), q_start.month(), q_start.day())
    period.end = datetime(q_end.year(), q_end.month(), q_end.day())
    s.commit()


def update_schedule(value_dict: dict):
    s = properties.open_session()
    schedule: Schedule = s.query(Schedule).filter_by(id=value_dict["item_id"]).first()
    s_date = schedule.date
    new_day_id: int = value_dict["d_id"]
    new_night_id: int = value_dict["n_id"]
    if schedule.activated:
        current_day_id: int = schedule.day_id
        update_score(s, current_day_id, new_day_id, s_date)

        current_night_id: int = schedule.night_id
        update_score(s, current_night_id, new_night_id, s_date)
    schedule.day_id = new_day_id
    schedule.night_id = new_night_id
    schedule.comment = value_dict["comment"]
    s.commit()


def update_score(s, current_id: int, new_id: int, s_date: date):
    score_offset: int = 2 if s_date.weekday() > 3 else 1
    off_period_bonus: int = 3
    if current_id != new_id:
        current_night: Employee = s.query(Employee).filter_by(id=current_id).first()
        new_night: Employee = s.query(Employee).filter_by(id=new_id).first()
        if current_night:
            current_night.score -= score_offset
        if new_night:
            if new_night.has_off_period(s_date):
                new_night.score += off_period_bonus
            else:
                new_night.score += score_offset


def find_schedule_by_id(s_id: int) -> Schedule:
    s = properties.open_session()
    schedule: Schedule = s.query(Schedule).filter_by(id=s_id).first()
    s.close()
    return schedule


def find_surrounding_schedules(schedule: Schedule) -> dict:
    s = properties.open_session()
    before = schedule.date - timedelta(days=1)
    after = schedule.date + timedelta(days=1)
    schedule_before: Schedule = s.query(Schedule).filter_by(date=before).first()
    schedule_after: Schedule = s.query(Schedule).filter_by(date=after).first()
    s.close()
    return {
        "d_before": schedule_before.day_id if schedule_before else None,
        "n_before": schedule_before.night_id if schedule_before else None,
        "d_today": schedule.day_id,
        "n_today": schedule.night_id,
        "d_after": schedule_after.day_id if schedule_after else None,
        "n_after": schedule_after.night_id if schedule_after else None
    }


def find_schedule_by_year_and_month(year: int, month: int) -> Schedule | None:
    if month < 1:
        return None
    s = properties.open_session()
    start_day = date(year, month, 1)
    schedule: Schedule = s.query(Schedule).filter_by(date=start_day).first()
    s.close()
    return schedule


def schedule_exists(year: int, month: int) -> bool:
    schedule = find_schedule_by_year_and_month(year, month)
    return schedule is not None


def shift_plan_active(year: int, month: int) -> bool:
    schedule = find_schedule_by_year_and_month(year, month)
    return schedule is not None and schedule.activated


def find_candidates() -> list:
    s = properties.open_session()
    employees: list = s.query(Employee).all()
    s.close()
    return employees


def find_days_off(month: int, year: int, e_id: int) -> list:
    s = properties.open_session()
    periods = s.query(OffPeriod).filter(
        and_(OffPeriod.e_id == e_id, (
            or_(
                and_(extract("year", OffPeriod.start) == year, extract("month", OffPeriod.start) == month),
                and_(extract("year", OffPeriod.end) == year, extract("month", OffPeriod.end) == month)))
             )
    ).all()
    s.close()
    day_list = []
    for p in periods:
        start = p.start.day
        end = p.end.day
        day_range = range(start, end + 1)
        for day in day_range:
            d = date(year, month, day)
            day_list.append(d)
    logger.info("Days off for Employee %d in %d/%d: %s", e_id, month, year, list(map(lambda x: str(x), day_list)))
    return day_list


def count_shifts(month: int, year: int, e_id: int) -> int:
    s = properties.open_session()
    day_count: int = s.query(Schedule).filter(
        and_(
            extract("year", Schedule.date) == year,
            extract("month", Schedule.date) == month,
            Schedule.day_id == e_id
        )
    ).count()
    night_count: int = s.query(Schedule).filter(
        and_(
            extract("year", Schedule.date) == year,
            extract("month", Schedule.date) == month,
            Schedule.night_id == e_id
        )
    ).count()
    s.close()
    logger.info("Employee %d occupies %d days and %d nights in %d/%d", e_id, day_count, night_count, month, year)
    return day_count + night_count

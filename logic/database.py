import sys

from PySide6.QtGui import Qt
from PySide6.QtSql import QSqlQueryModel, QSqlDatabase
from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker as sm

from logic.model import create_tables, Employee

from logic.queries import build_employee_query

db = ce("sqlite:///shiftPlanner.db")


def init_database():
    print("Connecting to database {}".format(db))
    db.connect()

    print("Initializing database")
    create_tables(db)

    print("Connect database to PySide")
    database = QSqlDatabase.addDatabase("QSQLITE")
    database.setDatabaseName("shiftPlanner.db")

    if not database.open():
        print("Unable to open database")
        sys.exit(1)


def configure_employee_model(search: str = "") -> QSqlQueryModel:
    employeeQuery = build_employee_query(search)
    model = QSqlQueryModel()
    model.setQuery(employeeQuery)
    model.setHeaderData(0, Qt.Horizontal, "First Name")
    model.setHeaderData(1, Qt.Horizontal, "Last Name")
    model.setHeaderData(2, Qt.Horizontal, "E-Mail")
    model.setHeaderData(3, Qt.Horizontal, "ID")
    return model


def persist_employee(employee: Employee):
    session = sm(bind=db)
    s = session()
    s.add(employee)
    s.commit()


def find_employee_by_id(e_id) -> Employee:
    session = sm(bind=db)
    s = session()
    employee: Employee = s.query(Employee).filter_by(id=e_id).first()
    s.close()
    return employee


def delete_employee(employee: Employee):
    session = sm(bind=db)
    s = session()
    s.delete(employee)
    s.commit()

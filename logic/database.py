import sys

from PySide6.QtGui import Qt
from PySide6.QtSql import QSqlQueryModel, QSqlDatabase
from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker as sm

from logic.model import create_tables, Employee

from logic.queries import employeeQuery

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


def configure_employee_model() -> QSqlQueryModel:
    model = QSqlQueryModel()
    model.setQuery(employeeQuery)
    model.setHeaderData(0, Qt.Horizontal, "First Name")
    model.setHeaderData(1, Qt.Horizontal, "Last Name")
    model.setHeaderData(2, Qt.Horizontal, "E-Mail")
    return model


def persist_employee(employee: Employee):
    session = sm(bind=db)
    s = session()
    s.add(employee)
    s.commit()

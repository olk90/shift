import sys

from PySide6.QtGui import Qt
from PySide6.QtSql import QSqlQueryModel, QSqlDatabase
from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker as sm

from logic.model import create_tables, Employee, EmployeeType
from logic.queries import build_employee_query

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


def configure_employee_model(search: str = "") -> QSqlQueryModel:
    employeeQuery = build_employee_query(search)
    model = QSqlQueryModel()
    model.setQuery(employeeQuery)
    model.setHeaderData(0, Qt.Horizontal, "ID")
    model.setHeaderData(1, Qt.Horizontal, "First Name")
    model.setHeaderData(2, Qt.Horizontal, "Last Name")
    model.setHeaderData(3, Qt.Horizontal, "Reference Value")
    model.setHeaderData(4, Qt.Horizontal, "Type")
    return model


def persist_employee(employee: Employee):
    session = sm(bind=db)
    s = session()
    s.add(employee)
    s.commit()


def find_employee_by_id(e_id: int) -> Employee:
    session = sm(bind=db)
    s = session()
    employee: Employee = s.query(Employee).filter_by(id=e_id).first()
    s.close()
    return employee


def update_employee(value_dict: dict):
    session = sm(bind=db)
    s = session()
    employee: Employee = s.query(Employee).filter_by(id=value_dict["e_id"]).first()
    employee.firstname = value_dict["firstname"]
    employee.lastname = value_dict["lastname"]
    employee.referenceValue = value_dict["reference_value"]
    employee.e_type = value_dict["e_type"]
    s.commit()


def delete_employee(employee: Employee):
    session = sm(bind=db)
    s = session()
    s.delete(employee)
    s.commit()

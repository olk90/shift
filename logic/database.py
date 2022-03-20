import sys

from PySide6.QtGui import Qt
from PySide6.QtSql import QSqlQueryModel, QSqlDatabase
from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker as sm, join

from logic.model import create_tables, Employee, EmployeeType
from logic.queries import build_employee_query, build_employee_type_query

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
        self.setHeaderData(4, Qt.Horizontal, self.tr("Type"))


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
    e_type = s.query(EmployeeType).filter_by(designation=value_dict["e_type"]).one()
    employee.e_type = e_type
    s.commit()


def delete_employee(employee: Employee):
    session = sm(bind=db)
    s = session()
    s.delete(employee)
    s.commit()

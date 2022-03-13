from sqlalchemy import (Column, Integer, String)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
employeeTableName: str = "Employee"


class EmployeeType:
    FOREGROUND = "Foreground"
    BACKGROUND = "Background"
    types = [FOREGROUND, BACKGROUND]


class ShiftType:
    DAY = "Day"
    NIGHT = "Night"
    types = [DAY, NIGHT]


class Employee(Base):
    __tablename__ = employeeTableName

    id = Column(Integer, primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    referenceValue = Column(Integer, nullable=False, default=0)
    e_type = Column(String(15), nullable=False, default=EmployeeType.FOREGROUND)

    def get_full_name(self):
        return "{} {}".format(self.firstname, self.lastname)


def create_tables(engine):
    Base.metadata.create_all(engine)

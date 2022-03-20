from sqlalchemy import (Column, Integer, String, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
employeeTypeTableName: str = "EmployeeType"
employeeTableName: str = "Employee"


class ShiftType:
    DAY = "Day"
    NIGHT = "Night"
    types = [DAY, NIGHT]


class RotationPeriod:
    SHIFT = "SHIFT"
    WEEKLY = "WEEKLY"
    periods = [SHIFT, WEEKLY]


class EmployeeType(Base):
    __tablename__ = employeeTypeTableName

    id = Column(Integer, primary_key=True)
    designation = Column(String(100), nullable=False)
    rotation_period = Column(String(100), nullable=False)


class Employee(Base):
    __tablename__ = employeeTableName

    id = Column(Integer, primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    referenceValue = Column(Integer, nullable=False, default=0)

    e_type_id = Column(Integer, ForeignKey("EmployeeType.id"))
    e_type = relationship(employeeTypeTableName, backref="employees")

    def get_full_name(self):
        return "{} {}".format(self.firstname, self.lastname)


def create_tables(engine):
    Base.metadata.create_all(engine)

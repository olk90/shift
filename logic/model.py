from sqlalchemy import (Column, Integer, String, ForeignKey, Date, Boolean)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
employeeTypeTableName: str = "EmployeeType"
employeeTableName: str = "Employee"
offPeriodTableName: str = "OffPeriod"
scheduleTableName: str = "Schedule"


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
    night_shifts = Column(Boolean, nullable=False, default=True)

    e_type_id = Column(Integer, ForeignKey("EmployeeType.id"))
    e_type = relationship(employeeTypeTableName, backref="employees")

    def get_full_name(self):
        return "{} {}".format(self.firstname, self.lastname)


class OffPeriod(Base):
    __tablename__ = offPeriodTableName

    id = Column(Integer, primary_key=True)
    start = Column(Date, nullable=False)
    end = Column(Date, nullable=False)
    e_id = Column(Integer, ForeignKey("Employee.id"))
    employee = relationship(employeeTableName, backref="off_periods")


class Schedule(Base):
    __tablename__ = scheduleTableName

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    day_id = Column(Integer, ForeignKey("Employee.id"))
    day_shift = relationship(employeeTableName, backref="day_shifts")
    night_id = Column(Integer, ForeignKey("Employee.id"))
    night_shift = relationship(employeeTableName, backref="night_shifts")
    comment = Column(String(280))


def create_tables(engine):
    Base.metadata.create_all(engine)

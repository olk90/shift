from sqlalchemy import (Column, Integer, String)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
employeeTableName: str = "Employee"


class Employee(Base):
    __tablename__ = employeeTableName

    id = Column(Integer, primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    email = Column(String(100))

    def get_full_name(self):
        return "{} {}".format(self.firstname, self.lastname)


def create_tables(engine):
    Base.metadata.create_all(engine)

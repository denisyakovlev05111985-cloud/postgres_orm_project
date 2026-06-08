from sqlalchemy import(
    Boolean,
    Date,
    Integer,
    Numeric,
    Text,
    ForeignKey,
    CheckConstraint,
    text
)
from datetime import date

from typing import Optional

from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int]= mapped_column(Integer, primary_key=True)
    name: Mapped[str]= mapped_column(Text, nullable=False, unique=True)
    employees: Mapped[list["Employee"]]= relationship(
        back_populates= "department"
    )

class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint("salary > 0", name="check_employee_salary_positive" ),
    )

    id: Mapped[int]= mapped_column(Integer, primary_key=True)
    name: Mapped[str]= mapped_column(Text, nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True
    )
    salary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10,2),
        nullable=True
    )
    hired_at: Mapped[date] = mapped_column(
        Date,
        server_default=text("CURRENT_DATE")
    )
    projects: Mapped[list["Project"]]= relationship(
        back_populates="employee"
    )
    department: Mapped[Optional["Department"]]= relationship(
        back_populates="employees"
    )

class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint("budget > 0", name="check_project_budjet_not_negative" ),
    )

    id: Mapped[int]= mapped_column(Integer, primary_key=True)
    name: Mapped[str]= mapped_column(Text, nullable=False)

    employee_id:Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id"),
        nullable=True
    )

    budget: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12,2),
        nullable=True
    )

    is_active: Mapped[bool]= mapped_column(
        Boolean,
        server_default=text("TRUE")
    )

    employee: Mapped[Optional["Employee"]]= relationship(
        back_populates="projects"
    )
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    employees: Mapped[list["Employee"]] = relationship(
        back_populates="department"
    )


class Employee(Base):
    __tablename__ = "employees"

    __table_args__ = (
        CheckConstraint("salary > 0", name="check_employee_salary_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    salary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True,
    )

    hired_at: Mapped[date] = mapped_column(
        Date,
        server_default=text("CURRENT_DATE"),
    )

    department: Mapped[Optional["Department"]] = relationship(
        back_populates="employees"
    )

    projects: Mapped[list["Project"]] = relationship(
        back_populates="employee"
    )

    profile: Mapped[Optional["EmployeeProfile"]] = relationship(
        back_populates="employee",
        uselist=False,
    )


class Project(Base):
    __tablename__ = "projects"

    __table_args__ = (
        CheckConstraint("budget >= 0", name="check_project_budget_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    employee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id"),
        nullable=True,
    )

    budget: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("TRUE"),
    )

    employee: Mapped[Optional["Employee"]] = relationship(
        back_populates="projects"
    )

class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    employee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id"),
        unique=True,
        nullable=True,
    )

    phone: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        unique=True
    )

    address: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    birth_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    employee: Mapped[Optional["Employee"]] = relationship(
        back_populates="profile"
    )

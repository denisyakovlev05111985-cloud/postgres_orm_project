from database import SessionLocal
from models import Department, Employee, Project
from decimal import Decimal
from sqlalchemy import select, update, delete, func


def create_department(name: str):
    with SessionLocal() as session:
        department = Department(name=name)

        session.add(department)
        session.commit()
        session.refresh(department)

        return department
    
def create_employee(
        name: str,
        salary: Decimal,
        department_id: int | None=None
):
    with SessionLocal() as session:
        employee= Employee(
            name=name,
            salary=salary,
            department_id=department_id
        )
        session.add(employee)
        session.commit()
        session.refresh(employee)
    
def create_project(
        name: str,
        budget: Decimal,
        employee_id: int | None=None
        
):
    with SessionLocal as session:
        project= Project(
        name=name,
        budget=budget,
        employee_id=employee_id
    )

        session.add(project)
        session.commit()
        session.refresh(project)

        return project



# with SessionLocal() as session:
#     department = Department(name="Dev")
#     employee= Employee(
#         name="Иван",
#         salary=Decimal("100000.00")
#     )
#     project=Project(
#         name="Mobile",
#         budget=Decimal("200000.00")
#     )

#     department.employees.append(employee)
#     employee.projects.append(project)
#     session.add(department)
#     session.commit()

def get_employee_by_id(employee_id: int):
    with SessionLocal() as session:
        return session.get(Employee, employee_id)
    
def get_all_employees():
    with SessionLocal() as session:
        stmt= select(Employee)
        employees= session.execute(stmt).scalars().all()
        return employees

def get_all_departments():
    with SessionLocal() as session:
        stmt= select(Department)
        departments= session.execute(stmt).scalars().all()
        return departments
    
def get_all_projects():
    with SessionLocal() as session:
        stmt= select(Project)
        projects= session.execute(stmt).scalars().all()
        return projects
    
def get_employees_with_salary_gt(amount: Decimal):
    with SessionLocal() as session:
        stmt= select(Employee).where(Employee.salary > amount)
        return session.execute(stmt).scalars().all()
    
def get_employees_order_by_salary_desc():
    with SessionLocal() as session:
        stmt= select(Employee).order_by(Employee.salary.desc())
        return session.execute(stmt).scalars().all()
    
def get_employees_page(page: int, per_page: int):
    with SessionLocal() as session:
        stmt=(select(Employee).offset((page-1)*per_page).limit(per_page))
        return session.execute(stmt).scalars().all()
    
def update_employee_salary(employee_id: int, salary: int):
    with SessionLocal() as session:
        employee= session.get(Employee, employee_id)
        if employee is None:
            return None
        
        employee.salary= salary
        session.commit()
        session.refresh(employee)
        return employee

def update_employee_salary_via_update(employee_id: int, salary: int):
    with SessionLocal() as session:
        stmt= (update(Employee).where(Employee.id == employee_id).value(salary=salary))
    session.execute(stmt)
    session.commit()

def delet_project(project_id: int):
    with SessionLocal() as session:
        project= session.get(Project, project_id)

        if project is None:
            return False
        session.delete(project)
        session.commit()

        return True
    
def delet_project_via_delete(project_id: int):
    with SessionLocal() as session:
        stmt= (delete(Project).where(Project.id==project_id))

        session.execute(stmt)
        session.commit()

def get_employees_with_department_names():
    with SessionLocal() as session:
        stmt= select(Employee.name, Department.name).join(Department, Employee.department_id==Department.id)
        return session.execute(stmt).all()
    
def get_employees_with_optional_department():
    with SessionLocal() as session:
        stmt= select(Employee.name, Department.name).outerjoin(Department, Employee.department_id==Department.id)
        return session.execute(stmt).all()
    
def get_project_employees_departments():
    with SessionLocal() as session:
        stmt= select(Project.name.label("project_name"), Employee.name.label("employee_name"), Department.name.label("department_name")).join(Employee, Project.employee_id == Employee.id).join(Department, Employee.department_id == Department.id)
        return session.execute(stmt).all()
    
def count_employees():
    with SessionLocal() as session:
        stmt= select(func.count(Employee.id))
        return session.execute(stmt).scalar()
    
def get_average_salary():
    with SessionLocal() as session:
        stmt= select(func.avg(Employee.salary))
        return session.execute(stmt).scalar()
    
def get_min_salary():
    with SessionLocal() as session:
        stmt= select(func.min(Employee.salary))
        return session.execute(stmt).scalar()
    
def get_max_salary():
    with SessionLocal() as session:
        stmt= select(func.max(Employee.salary))
        return session.execute(stmt).scalar()
    
def get_total_active_projects_budget():
    with SessionLocal() as session:
        stmt= select(func.sum(Project.budget)).where(Project.is_active._is(True))

        return session.execute(stmt).scalar()
    
def count_employees_by_department():
    with SessionLocal() as session:
        stmt= select(Department.name, func.count(Employee.id)).join(Employee, Employee.department_id==Department.id).group_by(Department.name)
        return session.execute(stmt).all()
    
def get_average_salary_by_department():
    with SessionLocal() as session:
        stmt= select(Department.name, func.avg(Employee.salary).label("avg_salary")).join(Employee, Employee.department_id==Department.id).group_by(Department.name)
        return session.execute(stmt).all()
    
def deactivate_project(project_id: int):
    with SessionLocal() as session:
        project= session.get(Project, project_id)

        if project is None:
            return None
        
        project.is_active= False
        session.commit()
        session.refresh(project)
        return project
    

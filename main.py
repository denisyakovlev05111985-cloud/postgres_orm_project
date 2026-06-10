from decimal import Decimal
from database import Base, engine
from crud import (
    create_department,
    create_employee,
    create_project,
    deactivate_project,
    get_all_employees,
    get_all_departments,
    get_all_projects,
    get_employees_with_department_names,
    get_project_employees_departments,
    update_employee_salary
)

def main():
    Base.metadata.create_all(engine)

    it = create_department("IT")
    hr= create_department("HR")

    if it:
        ivan= create_employee(
            name="Иван",
            salary=Decimal(120000.00),
            department_id=it.id
        )

        anna= create_employee(
            name="Анна",
            salary=Decimal(125000.00),
            department_id=it.id
        )

        if ivan:
            create_project(
                name="Internal CRM",
                budget=Decimal("50000.00"),
                employee_id=ivan.id
            )

        if anna:
            create_project(
                name="Mobile CRM",
                budget=Decimal("100000.00"),
                employee_id=anna.id
            )
    print("Все отделы") 
    for department in get_all_departments():
        print(department.id, department.name)

    print("Все сотрудники") 
    for employee in get_all_employees():
        print(employee.id, employee.name)

    print("Все проекты") 
    for project in get_all_projects():
        print(project.id, project.name)

    print("сотрудники и отделы") 
    for employee_name, department_name in get_employees_with_department_names():
        print(employee_name, department_name)

    print("проекты сотрудники и отделы") 
    for row in get_project_employees_departments():
        print(row.project_name,row.employee_name,row.department_name)

main()
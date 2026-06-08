from database import Base, engine
from models import Department, Employee, Project

Base.metadata.create_all(engine)
print("таблицы созданы!")
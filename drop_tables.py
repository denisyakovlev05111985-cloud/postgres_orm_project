from database import Base, engine
from models import Department, Employee, Project

Base.metadata.drop_all(engine)
print("таблицы удалены")
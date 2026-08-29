from database import engine, Base

# Создаёт все таблицы, если их нет. Если таблица уже есть — ничего не делает.
Base.metadata.create_all(bind=engine)
print("Таблицы созданы (или уже существовали).")

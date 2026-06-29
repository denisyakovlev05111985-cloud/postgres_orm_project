import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import psycopg2
from psycopg2 import extras

# --- НАСТРОЙКИ ПОДКЛЮЧЕНИЯ ---
DB_CONFIG = {
    "dbname": '"Больница"',    
    "user": "postgres",
    "password": "postgres", 
    "host": "localhost",
    "port": 5432,
}

def get_conn():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_client_encoding('UTF8')
    extras.register_uuid()
    return conn


class DBStructureTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление структурой БД «Больница»")
        self.root.geometry("1000x700")

        # Меню
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Просмотр", menu=view_menu)
        view_menu.add_command(label="Список всех таблиц", command=self.show_tables)
        view_menu.add_command(label="Столбцы таблицы", command=self.show_columns_names)
        view_menu.add_command(label="Столбцы и типы", command=self.show_columns_with_types)
        view_menu.add_command(label="Связи между таблицами", command=self.show_foreign_keys)

        alter_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Изменение структуры", menu=alter_menu)
        alter_menu.add_command(label="Создать таблицу", command=self.create_table_dialog)
        alter_menu.add_command(label="Удалить таблицу", command=self.drop_table_dialog)
        alter_menu.add_separator()
        alter_menu.add_command(label="Добавить столбец", command=self.add_column_dialog)
        alter_menu.add_command(label="Обновить столбец (тип/default)", command=self.alter_column_dialog)
        alter_menu.add_command(label="Удалить столбец", command=self.drop_column_dialog)
        alter_menu.add_separator()
        alter_menu.add_command(label="Добавить связь (FK)", command=self.add_foreign_key_dialog)
        alter_menu.add_command(label="Удалить связь (FK)", command=self.drop_foreign_key_dialog)

        self.output = tk.Text(root, wrap="word", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True, padx=5, pady=5)

    def log(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    # ---------------------------------------------------------
    # Просмотр: таблицы, столбцы, типы, связи
    # ---------------------------------------------------------

    def show_tables(self):
        self.output.delete(1.0, tk.END)
        self.log("=== Все таблицы в схеме public ===")
        conn = None
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            rows = cur.fetchall()
            if not rows:
                self.log("Таблиц не найдено.")
            else:
                for (table_name,) in rows:
                    self.log(table_name)
        except Exception as e:
            self.log(f"Ошибка: {e}")
        finally:
            if conn: conn.close()

    def ask_table_name(self, prompt):
        return simpledialog.askstring("Таблица", prompt)

    def show_columns_names(self):
        table = self.ask_table_name("Введите имя таблицы:")
        if not table: return
        self.output.delete(1.0, tk.END)
        self.log(f"=== Столбцы таблицы: {table} ===")
        conn = None
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s
                  AND table_schema = 'public'
                ORDER BY ordinal_position;
            """, (table.lower(),))  # PostgreSQL хранит имена таблиц/колонок в нижнем регистре, если не было кавычек
            rows = cur.fetchall()
            if not rows:
                self.log("Столбцов не найдено (проверьте имя таблицы).")
            else:
                for (col_name,) in rows:
                    self.log(col_name)
        except Exception as e:
            self.log(f"Ошибка: {e}")
        finally:
            if conn: conn.close()

    def show_columns_with_types(self):
        table = self.ask_table_name("Введите имя таблицы:")
        if not table: return
        self.output.delete(1.0, tk.END)
        self.log(f"=== Столбцы и типы данных: {table} ===")
        conn = None
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                  AND table_schema = 'public'
                ORDER BY ordinal_position;
            """, (table.lower(),))
            rows = cur.fetchall()
            if not rows:
                self.log("Нет информации о столбцах (проверьте имя таблицы).")
                return
            # Заголовки
            header = f"{'Column':<25} {'Type':<20} {'MaxLen':<8} {'Nullable':<8} {'Default':<20}"
            self.log(header)
            self.log("-" * len(header))
            for col_name, data_type, max_len, nullable, default in rows:
                ml = str(max_len) if max_len else ""
                self.log(f"{col_name:<25} {data_type:<20} {ml:<8} {nullable:<8} {str(default):<20}")
        except Exception as e:
            self.log(f"Ошибка: {e}")
        finally:
            if conn: conn.close()

    def show_foreign_keys(self):
        self.output.delete(1.0, tk.END)
        self.log("=== Внешние ключи (связи между таблицами) ===")
        conn = None
        try:
            conn = get_conn()
            cur = conn.cursor()
            # Стандартный запрос к information_schema для внешних ключей
            cur.execute("""
                SELECT
                  tc.table_name AS foreign_table,
                  kcu.column_name AS foreign_column,
                  ccu.table_name AS referenced_table,
                  ccu.column_name AS referenced_column,
                  rc.update_rule,
                  rc.delete_rule
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                JOIN information_schema.referential_constraints AS rc
                  ON rc.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = 'public';
            """)
            rows = cur.fetchall()
            if not rows:
                self.log("Внешние ключи не найдены.")
                return
            header = f"{'Foreign Table':<20} {'Column':<15} {'Ref Table':<15} {'Ref Column':<15} {'On Update':<10} {'On Delete':<10}"
            self.log(header)
            self.log("-" * len(header))
            for ft, fc, rt, rc, up, dn in rows:
                self.log(f"{ft:<20} {fc:<15} {rt:<15} {rc:<15} {up:<10} {dn:<10}")
        except Exception as e:
            self.log(f"Ошибка: {e}")
        finally:
            if conn: conn.close()

    # ---------------------------------------------------------
    # Создание / удаление таблиц
    # ---------------------------------------------------------

    def create_table_dialog(self):
        name = simpledialog.askstring("Создание таблицы", "Имя таблицы (например, nurses):")
        if not name: return

        cols_input = simpledialog.askstring(
            "Создание таблицы",
            "Столбцы в формате: имя тип, имя тип, ...\n"
            "Пример: id SERIAL PRIMARY KEY, name VARCHAR(50) NOT NULL, salary NUMERIC(10,2)"
        )
        if not cols_input: return

        sql = f"CREATE TABLE {name} ({cols_input});"
        if messagebox.askyesno("Подтверждение", f"Создать таблицу {name}?\nSQL:\n{sql}"):
            conn = None
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()
                self.log(f"Таблица {name} успешно создана.")
            except Exception as e:
                self.log(f"Ошибка создания таблицы: {e}")
                if conn: conn.rollback()
            finally:
                if conn: conn.close()

    def drop_table_dialog(self):
        name = self.ask_table_name("Имя таблицы для удаления:")
        if not name: return
        if not messagebox.askokcancel("ОПАСНО", f"Вы собираетесь удалить таблицу {name} и все её данные! Подтвердите."):
            return

        conn = None
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(f"DROP TABLE IF EXISTS {name.lower()} CASCADE;")
            conn.commit()
            self.log(f"Таблица {name} удалена (CASCADE).")
        except Exception as e:
            self.log(f"Ошибка удаления таблицы: {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()

    # ---------------------------------------------------------
    # Изменение столбцов
    # ---------------------------------------------------------

    def add_column_dialog(self):
        table = self.ask_table_name("Таблица:")
        if not table: return
        col_def = simpledialog.askstring("Добавление столбца", "Определение столбца (например, middle_name VARCHAR(50)):")
        if not col_def: return

        sql = f"ALTER TABLE {table.lower()} ADD COLUMN {col_def};"
        if messagebox.askyesno("Подтверждение", f"Добавить столбец?\n{sql}"):
            conn = None
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()
                self.log(f"Столбец добавлен в таблицу {table}.")
            except Exception as e:
                self.log(f"Ошибка добавления столбца: {e}")
                if conn: conn.rollback()
            finally:
                if conn: conn.close()

    def alter_column_dialog(self):
        # Самый безопасный вариант: меняем тип и/или default.
        table = self.ask_table_name("Таблица:")
        if not table: return
        col = simpledialog.askstring("Столбец", "Имя столбца:")
        if not col: return

        new_type = simpledialog.askstring("Тип данных", "Новый тип (например, VARCHAR(100), NUMERIC(10,2)):")
        default_val = simpledialog.askstring("DEFAULT", "Новое значение по умолчанию (или оставьте пустым):")

        parts = []
        if new_type:
            parts.append(f"SET DATA TYPE {new_type}")
        if default_val is not None:
            # Если оставили пустым — не ставим DEFAULT NULL явно, лучше ничего не делать.
            if default_val.strip() == "":
                parts.append("DROP DEFAULT")
            else:
                parts.append(f"SET DEFAULT {default_val}")

        if not parts:
            self.log("Ничего не указано для изменения.")
            return

        set_clause = ", ".join(parts)
        sql = f"ALTER TABLE {table.lower()} ALTER COLUMN {col.lower()} {set_clause};"

        if messagebox.askyesno("Подтверждение", f"Изменить столбец?\n{sql}"):
            conn = None
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()
                self.log(f"Столбец {col} в таблице {table} изменён.")
            except Exception as e:
                self.log(f"Ошибка изменения столбца: {e}")
                if conn: conn.rollback()
            finally:
                if conn: conn.close()

    def drop_column_dialog(self):
        table = self.ask_table_name("Таблица:")
        if not table: return
        col = simpledialog.askstring("Столбец", "Имя столбца для удаления:")
        if not col: return

        if not messagebox.askokcancel("ОПАСНО", f"Удалить столбец {col} из таблицы {table}? Данные будут потеряны."):
            return

        conn = None
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(f"ALTER TABLE {table.lower()} DROP COLUMN {col.lower()};")
            conn.commit()
            self.log(f"Столбец {col} удалён из таблицы {table}.")
        except Exception as e:
            self.log(f"Ошибка удаления столбца: {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()

    # ---------------------------------------------------------
    # Управление связями (Foreign Keys)
    # ---------------------------------------------------------

    def add_foreign_key_dialog(self):
        table = self.ask_table_name("Таблица, где будет FK (дочерняя):")
        if not table: return
        fk_col = simpledialog.askstring("Внешний ключ", "Имя столбца-FK в этой таблице:")
        ref_table = simpledialog.askstring("Целевая таблица", "Имя родительской таблицы:")
        ref_col = simpledialog.askstring("Целевой столбец", "Имя целевого столбца (обычно PK):")
        on_update = simpledialog.askstring("ON UPDATE (CASCADE/SET NULL/NO ACTION)", "ON UPDATE (или оставьте NO ACTION):") or "NO ACTION"
        on_delete = simpledialog.askstring("ON DELETE (CASCADE/SET NULL/NO ACTION)", "ON DELETE (или оставьте NO ACTION):") or "NO ACTION"

        constraint_name = f"{table}_{fk_col}_fk"
        sql = (
            f"ALTER TABLE {table.lower()} "
            f"ADD CONSTRAINT {constraint_name} "
            f"FOREIGN KEY ({fk_col.lower()}) "
            f"REFERENCES {ref_table.lower()}({ref_col.lower()}) "
            f"ON UPDATE {on_update} ON DELETE {on_delete};"
        )
        if messagebox.askyesno("Подтверждение", f"Добавить связь?\n{sql}"):
            conn = None
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()
                self.log(f"Связь (FK) добавлена: {constraint_name}.")
            except Exception as e:
                self.log(f"Ошибка добавления связи: {e}")
                if conn: conn.rollback()
            finally:
                if conn: conn.close()

    def drop_foreign_key_dialog(self):
        table = self.ask_table_name("Таблица, где находится FK:")
        if not table: return

        # Сначала покажем список FK в этой таблице, чтобы пользователь мог выбрать имя ограничения
        conn = None
        try:
            conn = get_conn()
            cur = conn.cursor()
            # Получаем имена ограничений FOREIGN KEY для таблицы
            cur.execute("""
                SELECT tc.constraint_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_name = %s
                  AND tc.table_schema = 'public';
            """, (table.lower(),))
            fks = [row[0] for row in cur.fetchall()]

            if not fks:
                self.log(f"В таблице {table} нет внешних ключей.")
                return

            fk_name = simpledialog.askstring(
                "Удаление связи",
                f"Выберите имя ограничения из списка:\n{', '.join(fks)}\n(или введите вручную):"
            )
            if not fk_name or fk_name not in fks:
                # Если ввели вручную и такого нет — можно либо отклонить, либо всё равно попробовать удалить (ошибка скажет сама)
                if fk_name and not messagebox.askyesno(
                    "Внимание",
                    f"Ограничение {fk_name} не найдено в списке для таблицы {table}.\nВсё равно попробовать удалить?"
                ):
                    return

            sql = f"ALTER TABLE {table.lower()} DROP CONSTRAINT {fk_name};"

            if messagebox.askokcancel("ОПАСНО", f"Удалить ограничение {fk_name}?\nSQL:\n{sql}"):
                cur2 = conn.cursor()
                try:
                    cur2.execute(sql)
                    conn.commit()
                    self.log(f"Ограничение {fk_name} удалено.")
                except Exception as e:
                    self.log(f"Ошибка удаления связи: {e}")
                    conn.rollback()
                finally:
                    cur2.close()
        except Exception as e:
            self.log(f"Ошибка при получении списка FK: {e}")
        finally:
            if conn: conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = DBStructureTool(root)
    root.mainloop()

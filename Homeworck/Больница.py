import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import psycopg2
from psycopg2 import extras

# --- НАСТРОЙКИ ПОДКЛЮЧЕНИЯ ---
# База создана как "Больница" (с кавычками) → передаём '"Больница"'
DB_CONFIG = {
    "dbname": '"Больница"',
    "user": "postgres",
    "password": "postgres", 
    "host": "localhost",
    "port": 5432,
}

def get_conn():
    conn = psycopg2.connect(**DB_CONFIG)
    extras.register_uuid()
    return conn

class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Больница (PostgreSQL)")
        self.root.geometry("900x600")

        menubar = tk.Menu(root)
        root.config(menu=menubar)

        crud_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="CRUD", menu=crud_menu)
        crud_menu.add_command(label="Вставить строку", command=self.insert_dialog)
        crud_menu.add_command(label="Обновить строку", command=self.update_dialog)
        crud_menu.add_command(label="Удалить строку", command=self.delete_dialog)

        report_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отчёты", menu=report_menu)
        report_menu.add_command(label="Имена врачей и специализации", command=lambda: self.run_report(1))
        report_menu.add_command(label="Фамилии и зарплаты врачей (не в отпуске)", command=lambda: self.run_report(2))
        report_menu.add_command(label="Палаты конкретного отделения", command=lambda: self.run_report(3))
        report_menu.add_command(label="Отделения, спонсируемые компанией", command=lambda: self.run_report(4))
        report_menu.add_command(label="Пожертвования за месяц", command=lambda: self.run_report(5))
        report_menu.add_command(label="Врачи и отделения обследований", command=lambda: self.run_report(6))

        self.output_text = tk.Text(root, wrap="word")
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)

    def log(self, text):
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)

    # --- ВСТАВКА (для doctors) ---
    def insert_dialog(self):
        table = simpledialog.askstring("Вставка", "Таблица (например, doctors):")
        if not table: return
        self.log(f"--- ВСТАВКА в таблицу {table} ---")

        if table == "doctors":
            first_name = simpledialog.askstring(table, "Имя:")
            last_name = simpledialog.askstring(table, "Фамилия:")
            specialization = simpledialog.askstring(table, "Специализация:")
            department_id = simpledialog.askinteger(table, "ID отделения:")
            base_salary = simpledialog.askfloat(table, "Ставка:")
            bonus = simpledialog.askfloat(table, "Надбавка (0 если нет):") or 0
            is_on_vacation = messagebox.askyesno(table, "В отпуске?")

            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO doctors (first_name, last_name, specialization, department_id, base_salary, bonus, is_on_vacation)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (first_name, last_name, specialization, department_id, base_salary, bonus, is_on_vacation))
                conn.commit()
                self.log("Строка успешно вставлена.")
            except Exception as e:
                self.log(f"Ошибка: {e}")
                conn.rollback()
            finally:
                cur.close()
                conn.close()
        else:
            self.log("Для других таблиц требуется доработка формы ввода.")

    # --- ОБНОВЛЕНИЕ ---
    def update_dialog(self):
        table = simpledialog.askstring("Обновление", "Таблица:")
        if not table: return

        where_clause = simpledialog.askstring("Обновление", "Условие WHERE (например, doctor_id=1). Оставьте пустым для ВСЕХ строк:")
        set_clause = simpledialog.askstring("Обновление", "SET выражение (например, base_salary=50000):")
        if not set_clause:
            self.log("SET не указан.")
            return

        conn = get_conn()
        cur = conn.cursor()

        if not where_clause or where_clause.strip() == "":
            confirm = messagebox.askokcancel("ВНИМАНИЕ", "Вы собираетесь обновить ВСЕ строки в таблице! Подтвердите действие.")
            if not confirm:
                self.log("Обновление отменено пользователем.")
                cur.close()
                conn.close()
                return

        sql_query = f"UPDATE {table} SET {set_clause}"
        if where_clause:
            sql_query += f" WHERE {where_clause}"

        try:
            cur.execute(sql_query)
            conn.commit()
            self.log(f"Обновлено строк: {cur.rowcount}")
        except Exception as e:
            self.log(f"Ошибка обновления: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    # --- УДАЛЕНИЕ ---
    def delete_dialog(self):
        table = simpledialog.askstring("Удаление", "Таблица:")
        if not table: return

        where_clause = simpledialog.askstring("Удаление", "Условие WHERE (например, doctor_id=1). Оставьте пустым для ВСЕХ строк:")

        conn = get_conn()
        cur = conn.cursor()

        if not where_clause or where_clause.strip() == "":
            confirm = messagebox.askokcancel("ОПАСНО", "Вы собираетесь удалить ВСЕ строки в таблице! Это необратимо. Подтвердите.")
            if not confirm:
                self.log("Удаление отменено пользователем.")
                cur.close()
                conn.close()
                return

        sql_query = f"DELETE FROM {table}"
        if where_clause:
            sql_query += f" WHERE {where_clause}"

        try:
            cur.execute(sql_query)
            conn.commit()
            self.log(f"Удалено строк: {cur.rowcount}")
        except Exception as e:
            self.log(f"Ошибка удаления: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    # --- ОТЧЁТЫ ---
    def run_report(self, report_id):
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        self.output_text.delete(1.0, tk.END)
        self.log(f"=== ОТЧЁТ #{report_id} ===")

        try:
            if report_id == 1:
                cur.execute("SELECT first_name, last_name, specialization FROM doctors")
                rows = cur.fetchall()
                for r in rows:
                    self.log(f"{r['first_name']} {r['last_name']} — {r['specialization']}")

            elif report_id == 2:
                cur.execute("""
                    SELECT last_name, (base_salary + bonus) AS total_salary
                    FROM doctors
                    WHERE is_on_vacation = FALSE
                """)
                rows = cur.fetchall()
                for r in rows:
                    self.log(f"{r['last_name']}: {r['total_salary']} руб.")

            elif report_id == 3:
                dep_id = simpledialog.askinteger("Отчёт 3", "Введите ID отделения:")
                if dep_id is None: return
                cur.execute("SELECT ward_name FROM wards WHERE department_id = %s", (dep_id,))
                rows = cur.fetchall()
                if not rows:
                    self.log("Палат не найдено.")
                else:
                    for r in rows:
                        self.log(r['ward_name'])

            elif report_id == 4:
                company = simpledialog.askstring("Отчёт 4", "Название компании-спонсора:")
                if not company: return
                cur.execute("""
                    SELECT DISTINCT d.name
                    FROM departments d
                    JOIN donations don ON d.department_id = don.department_id
                    JOIN sponsors s ON don.sponsor_id = s.sponsor_id
                    WHERE s.company_name = %s
                """, (company,))
                rows = cur.fetchall()
                if not rows:
                    self.log("Отделения не найдены.")
                else:
                    for r in rows:
                        self.log(r['name'])

            elif report_id == 5:
                month = simpledialog.askstring("Отчёт 5", "Месяц в формате ГГГГ-ММ (например, 2024-06):")
                if not month: return
                year, month_num = month.split("-")
                cur.execute("""
                    SELECT d.name AS department, s.company_name AS sponsor, don.amount, don.donation_date
                    FROM donations don
                    JOIN departments d ON don.department_id = d.department_id
                    JOIN sponsors s ON don.sponsor_id = s.sponsor_id
                    WHERE EXTRACT(YEAR FROM don.donation_date) = %s
                      AND EXTRACT(MONTH FROM don.donation_date) = %s
                    ORDER BY don.donation_date
                """, (int(year), int(month_num)))
                rows = cur.fetchall()
                if not rows:
                    self.log("Пожертвований за этот месяц не найдено.")
                else:
                    for r in rows:
                        self.log(f"{r['department']} | {r['sponsor']} | {r['amount']} | {r['donation_date']}")

            elif report_id == 6:
                cur.execute("""
                    SELECT doc.last_name, dep.name AS exam_department
                    FROM examinations ex
                    JOIN doctors doc ON ex.doctor_id = doc.doctor_id
                    JOIN departments dep ON ex.department_id = dep.department_id
                """)
                rows = cur.fetchall()
                if not rows:
                    self.log("Данных об обследованиях нет.")
                else:
                    for r in rows:
                        self.log(f"{r['last_name']} проводит обследования в отделении: {r['exam_department']}")
        except Exception as e:
            self.log(f"Ошибка отчёта: {e}")
        finally:
            cur.close()
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalApp(root)
    root.mainloop()

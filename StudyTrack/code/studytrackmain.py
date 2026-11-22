
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import textwrap

BLUE = "#245A9B"
DARK = "#102F55"
BG = "#EAF1FA"
WHITE = "#FFFFFF"
GREEN = "#198754"
RED = "#D9534F"

def connect():
    return mysql.connector.connect(
        host="localhost", user="root",
        password="opshadow1234##", database="StudyTrack"
    )

def execute(query, values=(), fetch=False):
    con = connect()
    cur = con.cursor()
    try:
        cur.execute(query, values)
        if fetch:
            return cur.fetchall()
        con.commit()
    finally:
        cur.close()
        con.close()

def button(parent, text, command, color=BLUE):
    return tk.Button(parent, text=text, command=command,
                     bg=color, fg=WHITE, font=("Arial", 10, "bold"),
                     relief="flat", padx=12, pady=7)

def field(parent, name):
    tk.Label(parent, text=name, bg=WHITE, fg=DARK,
             font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 3))
    entry = tk.Entry(parent, font=("Arial", 11))
    entry.pack(fill="x", ipady=5)
    return entry

root = tk.Tk()
root.title("StudyTrack - Student Learning Portal")
root.geometry("1150x720")
root.minsize(950, 600)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", rowheight=55, font=("Arial", 10),
                background=WHITE, fieldbackground=WHITE, foreground=DARK)
style.configure("Treeview.Heading", background=BLUE,
                foreground=WHITE, font=("Arial", 10, "bold"))

pages = {}
category = "Homework"
selected_id = None
schedule_id = None

def make_page(name):
    pages[name] = tk.Frame(root, bg=BG)
    return pages[name]

def show_page(name):
    for p in pages.values():
        p.pack_forget()
    pages[name].pack(fill="both", expand=True)

def title(parent, text):
    tk.Label(parent, text=text, bg=BG, fg=DARK,
             font=("Arial", 22, "bold")).pack(anchor="w", padx=25, pady=20)

def home_button(parent):
    button(parent, "Home", lambda: show_page("home")).place(
        relx=0.98, y=15, anchor="ne")

home = make_page("home")
activity = make_page("activity")
profile = make_page("profile")
timetable = make_page("timetable")

logo = tk.Canvas(home, width=160, height=160, bg=BG, highlightthickness=0)
logo.place(relx=0.85, y=35)

logo.create_oval(10, 10, 150, 150, fill="#D5E4F5", outline="#245A9B", width=3)
logo.create_oval(20, 20, 140, 140, outline="white", width=3)
logo.create_text(80, 55, text="★", font=("Arial", 25, "bold"), fill="#245A9B")
logo.create_text(80, 105, text="ST", font=("Arial", 32, "bold"), fill="#102F55")


tk.Label(home, text="StudyTrack", bg=BG, fg=DARK,
         font=("Arial", 30, "bold")).pack(pady=(75, 5))
tk.Label(home, text="Student Learning Portal", bg=BG, fg=BLUE,
         font=("Arial", 14)).pack()
tk.Label(home, text="Welcome to StudyTrack!", bg=BG, fg=DARK,
         font=("Arial", 18, "bold")).pack(pady=35)

cards = tk.Frame(home, bg=BG)
cards.pack(pady=35)
home_links = tk.Frame(home, bg=BG)
home_links.pack(pady=15)

title_label = tk.Label(activity, text="", bg=BG, fg=DARK,
                       font=("Arial", 22, "bold"))
title_label.pack(anchor="w", padx=25, pady=20)
home_button(activity)

body = tk.Frame(activity, bg=BG)
body.pack(fill="both", expand=True, padx=25, pady=10)

form = tk.Frame(body, bg=WHITE, padx=18, pady=15)
form.pack(side="left", fill="y", padx=(0, 18))

priority = field(form, "Priority No.")
subject = field(form, "Subject")
task = field(form, "Activity Name")
due_date = field(form, "Due Date")

status = tk.StringVar(value="Pending")
tk.Label(form, text="Status", bg=WHITE, fg=DARK).pack(anchor="w", pady=5)
ttk.Combobox(form, textvariable=status,
             values=["Pending", "In Progress", "Completed"],
             state="readonly").pack(fill="x")

table_area = tk.Frame(body, bg=BG)
table_area.pack(side="left", fill="both", expand=True)

search = tk.Entry(table_area, font=("Arial", 11))
search.pack(side="top", fill="x", ipady=7, pady=(0, 10))

columns = ("ID", "Priority No.", "Subject", "Activity", "Due Date", "Status")
tree = ttk.Treeview(table_area, columns=columns,
                    displaycolumns=columns[1:], show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=110)

tree.column("ID", width=0, stretch=False)
tree.column("Activity", width=250)

scroll = ttk.Scrollbar(table_area, command=tree.yview)
tree.configure(yscrollcommand=scroll.set)
tree.pack(side="left", fill="both", expand=True)
scroll.pack(side="right", fill="y")

def clear_activity():
    global selected_id
    selected_id = None
    for entry in (priority, subject, task, due_date):
        entry.delete(0, tk.END)
    status.set("Pending")
    tree.selection_remove(tree.selection())

def load_activities():
    tree.delete(*tree.get_children())
    word = "%" + search.get() + "%"
    rows = execute(
        """SELECT homework_id, serial_no, subject, task, due_date, status
        FROM Homework WHERE category=%s
        AND (subject LIKE %s OR task LIKE %s OR due_date LIKE %s)
        ORDER BY serial_no""",
        (category, word, word, word), True)
    for row in rows:
        tree.insert("", "end", values=(
            row[0], row[1], row[2],
            textwrap.fill(str(row[3]), 28), row[4], row[5]))

def add_activity():
    if not priority.get().isdigit() or int(priority.get()) <= 0:
        messagebox.showwarning("Invalid Priority", "Enter a positive priority number.")
        return
    if not subject.get().strip() or not task.get().strip():
        messagebox.showwarning("Missing Details", "Enter subject and activity.")
        return
    if execute(
        "SELECT homework_id FROM Homework WHERE category=%s AND serial_no=%s",
        (category, int(priority.get())), True):
        messagebox.showwarning("Priority Used", "This priority is already assigned.")
        return
    execute(
        """INSERT INTO Homework
        (serial_no, category, subject, task, due_date, status)
        VALUES (%s,%s,%s,%s,%s,%s)""",
        (int(priority.get()), category, subject.get().strip(),
         task.get().strip(), due_date.get().strip(), status.get()))
    clear_activity()
    search.delete(0, tk.END)
    load_activities()
    messagebox.showinfo("Success", "Activity added successfully.")

def select_activity(event):
    global selected_id
    item = tree.focus()
    if not item:
        return
    values = tree.item(item, "values")
    selected_id = values[0]
    for entry, value in zip(
        (priority, subject, task, due_date),
        (values[1], values[2], values[3].replace("\n", " "), values[4])):
        entry.delete(0, tk.END)
        entry.insert(0, value)
    status.set(values[5])

def update_activity():
    if not selected_id:
        messagebox.showwarning("Select Activity", "Select a record first.")
        return
    if not priority.get().isdigit() or int(priority.get()) <= 0:
        messagebox.showwarning("Invalid Priority", "Enter a positive priority number.")
        return
    if not subject.get().strip() or not task.get().strip():
        messagebox.showwarning("Missing Details", "Enter subject and activity.")
        return

    con = connect()
    cur = con.cursor()
    swapped = False
    try:
        new = int(priority.get())
        cur.execute(
            "SELECT serial_no FROM Homework WHERE homework_id=%s AND category=%s",
            (selected_id, category))
        row = cur.fetchone()
        if not row:
            messagebox.showwarning("Not Found", "Activity no longer exists.")
            return
        old = row[0]

        if new != old:
            cur.execute(
                """SELECT homework_id FROM Homework
                WHERE category=%s AND serial_no=%s AND homework_id!=%s""",
                (category, new, selected_id))
            other = cur.fetchone()

            if other:
                other_id = other[0]
                cur.execute(
                    "SELECT COALESCE(MAX(serial_no),0)+1 FROM Homework WHERE category=%s",
                    (category,))
                temp = cur.fetchone()[0]

                cur.execute("UPDATE Homework SET serial_no=%s WHERE homework_id=%s",
                            (temp, other_id))
                cur.execute("UPDATE Homework SET serial_no=%s WHERE homework_id=%s",
                            (new, selected_id))
                cur.execute("UPDATE Homework SET serial_no=%s WHERE homework_id=%s",
                            (old, other_id))
                swapped = True
            else:
                cur.execute("UPDATE Homework SET serial_no=%s WHERE homework_id=%s",
                            (new, selected_id))

        cur.execute(
            """UPDATE Homework SET subject=%s, task=%s, due_date=%s,
            status=%s WHERE homework_id=%s AND category=%s""",
            (subject.get().strip(), task.get().strip(),
             due_date.get().strip(), status.get(), selected_id, category))
        con.commit()
    except mysql.connector.Error as error:
        con.rollback()
        messagebox.showerror("Database Error", str(error))
        return
    finally:
        cur.close()
        con.close()

    clear_activity()
    load_activities()
    if swapped:
        messagebox.showinfo("Success", "Priorities swapped successfully!")
    else:
        messagebox.showinfo("Success", "Activity updated successfully!")

def delete_activity():
    if not selected_id:
        messagebox.showwarning("Select Activity", "Select a record first.")
        return
    if messagebox.askyesno("Confirm", "Delete this activity?"):
        execute("DELETE FROM Homework WHERE homework_id=%s", (selected_id,))
        clear_activity()
        load_activities()
        messagebox.showinfo("Success", "Activity deleted successfully.")

def open_activity(name):
    global category
    category = name
    title_label.config(text=name)
    clear_activity()
    search.delete(0, tk.END)
    load_activities()
    show_page("activity")

for name, symbol in [("Homework", "📚"), ("Assignments", "📝"), ("Projects", "📁")]:
    tk.Button(cards, text=symbol + "\n\n" + name,
              command=lambda n=name: open_activity(n),
              bg=WHITE, fg=DARK, font=("Arial", 15, "bold"),
              width=17, height=5).pack(side="left", padx=12)

actions = tk.Frame(form, bg=WHITE)
actions.pack(pady=15)
button(actions, "Add", add_activity, GREEN).pack(fill="x", pady=4)
button(actions, "Update", update_activity).pack(fill="x", pady=4)
button(actions, "Delete", delete_activity, RED).pack(fill="x", pady=4)
button(actions, "Clear", clear_activity).pack(fill="x", pady=4)
button(table_area, "Search", load_activities).pack(side="bottom", pady=5)
button(table_area, "Show All",
       lambda: (search.delete(0, tk.END), load_activities())).pack(side="bottom", pady=5)

tree.bind("<<TreeviewSelect>>", select_activity)

title(profile, "Student Profile")
home_button(profile)
profile_form = tk.Frame(profile, bg=WHITE, padx=30, pady=20)
profile_form.pack(fill="x", padx=25, pady=10)

student_name = field(profile_form, "Student Name")
class_entry = field(profile_form, "Class")
roll_entry = field(profile_form, "Roll Number")
school_entry = field(profile_form, "School Name")

def load_profile():
    rows = execute(
        "SELECT name, class_name, roll_number, school FROM Students WHERE student_id=1",
        fetch=True)
    if rows:
        for entry, value in zip(
            (student_name, class_entry, roll_entry, school_entry), rows[0]):
            entry.delete(0, tk.END)
            entry.insert(0, str(value or ""))

def update_profile():
    if not student_name.get().strip():
        messagebox.showwarning("Missing Details", "Enter student name.")
        return
    execute(
        """UPDATE Students SET name=%s, class_name=%s,
        roll_number=%s, school=%s WHERE student_id=1""",
        (student_name.get().strip(), class_entry.get().strip(),
         roll_entry.get().strip(), school_entry.get().strip()))
    messagebox.showinfo("Success", "Profile updated successfully.")

button(profile_form, "Save Profile", update_profile, GREEN).pack(
    anchor="w", pady=15)

title(timetable, "Study Timetable")
home_button(timetable)

schedule_body = tk.Frame(timetable, bg=BG)
schedule_body.pack(fill="both", expand=True, padx=25, pady=10)
schedule_form = tk.Frame(schedule_body, bg=WHITE, padx=18, pady=15)
schedule_form.pack(side="left", fill="y", padx=(0, 18))

schedule_subject = field(schedule_form, "Subject")
schedule_topic = field(schedule_form, "Topic")
schedule_date = field(schedule_form, "Study Date")
schedule_time = field(schedule_form, "Start Time")
schedule_duration = field(schedule_form, "Duration")

schedule_table = tk.Frame(schedule_body, bg=BG)
schedule_table.pack(side="left", fill="both", expand=True)

schedule_columns = ("ID", "Subject", "Topic", "Study Date", "Start Time", "Duration")
schedule_tree = ttk.Treeview(
    schedule_table, columns=schedule_columns,
    displaycolumns=schedule_columns[1:], show="headings")

for col in schedule_columns:
    schedule_tree.heading(col, text=col)
    schedule_tree.column(col, width=110)

schedule_tree.column("ID", width=0, stretch=False)
schedule_tree.column("Topic", width=200)

schedule_scroll = ttk.Scrollbar(schedule_table, command=schedule_tree.yview)
schedule_tree.configure(yscrollcommand=schedule_scroll.set)
schedule_tree.pack(side="left", fill="both", expand=True)
schedule_scroll.pack(side="right", fill="y")

def clear_schedule():
    global schedule_id
    schedule_id = None
    for entry in (schedule_subject, schedule_topic, schedule_date,
                  schedule_time, schedule_duration):
        entry.delete(0, tk.END)
    schedule_tree.selection_remove(schedule_tree.selection())

def load_timetable():
    schedule_tree.delete(*schedule_tree.get_children())
    rows = execute(
        """SELECT schedule_id, subject, topic, study_date, start_time, duration
        FROM StudySchedule ORDER BY study_date, start_time""", fetch=True)
    for row in rows:
        schedule_tree.insert("", "end", values=row)

def add_schedule():
    if not schedule_subject.get().strip() or not schedule_topic.get().strip():
        messagebox.showwarning("Missing Details", "Enter subject and topic.")
        return
    execute(
        """INSERT INTO StudySchedule
        (subject, topic, study_date, start_time, duration)
        VALUES (%s,%s,%s,%s,%s)""",
        (schedule_subject.get().strip(), schedule_topic.get().strip(),
         schedule_date.get().strip(), schedule_time.get().strip(),
         schedule_duration.get().strip()))
    clear_schedule()
    load_timetable()
    messagebox.showinfo("Success", "Study schedule added.")

def select_schedule(event):
    global schedule_id
    item = schedule_tree.focus()
    if not item:
        return
    values = schedule_tree.item(item, "values")
    schedule_id = values[0]
    for entry, value in zip(
        (schedule_subject, schedule_topic, schedule_date,
         schedule_time, schedule_duration), values[1:]):
        entry.delete(0, tk.END)
        entry.insert(0, value)

def update_schedule():
    if not schedule_id:
        messagebox.showwarning("Select Schedule", "Select a timetable record.")
        return
    execute(
        """UPDATE StudySchedule SET subject=%s, topic=%s, study_date=%s,
        start_time=%s, duration=%s WHERE schedule_id=%s""",
        (schedule_subject.get(), schedule_topic.get(),
         schedule_date.get(), schedule_time.get(),
         schedule_duration.get(), schedule_id))
    clear_schedule()
    load_timetable()
    messagebox.showinfo("Success", "Study schedule updated.")

def delete_schedule():
    if not schedule_id:
        messagebox.showwarning("Select Schedule", "Select a timetable record.")
        return
    if messagebox.askyesno("Confirm", "Delete this timetable record?"):
        execute("DELETE FROM StudySchedule WHERE schedule_id=%s", (schedule_id,))
        clear_schedule()
        load_timetable()
        messagebox.showinfo("Success", "Study schedule deleted.")

schedule_actions = tk.Frame(schedule_form, bg=WHITE)
schedule_actions.pack(pady=15)
button(schedule_actions, "Add", add_schedule, GREEN).pack(fill="x", pady=4)
button(schedule_actions, "Update", update_schedule).pack(fill="x", pady=4)
button(schedule_actions, "Delete", delete_schedule, RED).pack(fill="x", pady=4)
button(schedule_actions, "Clear", clear_schedule).pack(fill="x", pady=4)

schedule_tree.bind("<<TreeviewSelect>>", select_schedule)

button(home_links, "Student Profile",
       lambda: (load_profile(), show_page("profile"))).pack(side="left", padx=10)
button(home_links, "Study Timetable",
       lambda: (load_timetable(), show_page("timetable"))).pack(side="left", padx=10)

def start_app():
    try:
        load_profile()
        load_activities()
        load_timetable()
        show_page("home")
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", "Unable to connect to MySQL.\n\n" + str(error))

start_app()
root.mainloop()

import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from datetime import datetime

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Application")

        self.conn = sqlite3.connect('todo.db')
        self.create_table()

        self.create_widgets()
        self.load_tasks()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                          (id INTEGER PRIMARY KEY,
                           task TEXT NOT NULL,
                           priority TEXT,
                           due_date TEXT,
                           completed INTEGER DEFAULT 0)''')
        self.conn.commit()

    def create_widgets(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.task_listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE, width=50)
        self.task_listbox.grid(row=0, column=0, columnspan=4)
        self.task_listbox.bind('<<ListboxSelect>>', self.on_task_select)

        self.add_button = tk.Button(self.frame, text="Add Task", command=self.add_task)
        self.add_button.grid(row=1, column=0)

        self.update_button = tk.Button(self.frame, text="Update Task", command=self.update_task)
        self.update_button.grid(row=1, column=1)

        self.delete_button = tk.Button(self.frame, text="Delete Task", command=self.delete_task)
        self.delete_button.grid(row=1, column=2)

        self.complete_button = tk.Button(self.frame, text="Mark Complete", command=self.mark_complete)
        self.complete_button.grid(row=1, column=3)

        self.filter_button = tk.Button(self.frame, text="Filter Tasks", command=self.filter_tasks)
        self.filter_button.grid(row=2, column=0, columnspan=4)

    def load_tasks(self, filter_query=None):
        self.task_listbox.delete(0, tk.END)
        cursor = self.conn.cursor()

        if filter_query:
            cursor.execute(filter_query)
        else:
            cursor.execute("SELECT id, task, priority, due_date, completed FROM tasks")

        for row in cursor.fetchall():
            task_text = f"{row[1]} | Priority: {row[2]} | Due: {row[3]} | {'Completed' if row[4] else 'Pending'}"
            self.task_listbox.insert(tk.END, task_text)

        self.conn.commit()

    def on_task_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.selected_task_index = selection[0]
            self.selected_task_id = self.get_task_id(self.selected_task_index)

    def get_task_id(self, index):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM tasks")
        return cursor.fetchall()[index][0]

    def add_task(self):
        task = simpledialog.askstring("Task", "Enter task description:")
        if task:
            priority = simpledialog.askstring("Priority", "Enter task priority (High, Medium, Low):")
            due_date = simpledialog.askstring("Due Date", "Enter due date (YYYY-MM-DD):")
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO tasks (task, priority, due_date) VALUES (?, ?, ?)", (task, priority, due_date))
            self.conn.commit()
            self.load_tasks()

    def update_task(self):
        if hasattr(self, 'selected_task_id'):
            task = simpledialog.askstring("Task", "Enter new task description:")
            if task:
                priority = simpledialog.askstring("Priority", "Enter new task priority (High, Medium, Low):")
                due_date = simpledialog.askstring("Due Date", "Enter new due date (YYYY-MM-DD):")
                cursor = self.conn.cursor()
                cursor.execute("UPDATE tasks SET task = ?, priority = ?, due_date = ? WHERE id = ?",
                               (task, priority, due_date, self.selected_task_id))
                self.conn.commit()
                self.load_tasks()

    def delete_task(self):
        if hasattr(self, 'selected_task_id'):
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (self.selected_task_id,))
            self.conn.commit()
            self.load_tasks()

    def mark_complete(self):
        if hasattr(self, 'selected_task_id'):
            cursor = self.conn.cursor()
            cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (self.selected_task_id,))
            self.conn.commit()
            self.load_tasks()

    def filter_tasks(self):
        filter_option = simpledialog.askstring("Filter", "Enter filter option (priority: High/Medium/Low, due: YYYY-MM-DD, status: completed/pending):")
        if filter_option:
            if filter_option.startswith("priority:"):
                priority = filter_option.split(":")[1].strip()
                filter_query = f"SELECT id, task, priority, due_date, completed FROM tasks WHERE priority = '{priority}'"
            elif filter_option.startswith("due:"):
                due_date = filter_option.split(":")[1].strip()
                filter_query = f"SELECT id, task, priority, due_date, completed FROM tasks WHERE due_date = '{due_date}'"
            elif filter_option.startswith("status:"):
                status = filter_option.split(":")[1].strip().lower()
                completed = 1 if status == "completed" else 0
                filter_query = f"SELECT id, task, priority, due_date, completed FROM tasks WHERE completed = {completed}"
            else:
                messagebox.showerror("Error", "Invalid filter option")
                return

            self.load_tasks(filter_query)
        else:
            self.load_tasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()

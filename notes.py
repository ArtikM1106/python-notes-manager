import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from storage import load_notes, save_notes


class NotesWindow:
    def __init__(self, root, path):
        self.path = path
        self.notes = []
        self.index = None
        self.storage_ready = True
        root.title("Менеджер заметок")
        panel = ttk.Frame(root, padding=16)
        panel.grid()
        self.listbox = tk.Listbox(panel, width=25, height=12, exportselection=False)
        self.listbox.grid(row=0, column=0, padx=(0, 10))
        self.editor = tk.Text(panel, width=38, height=12, wrap="word")
        self.editor.grid(row=0, column=1)
        self.status = tk.StringVar()
        bar = ttk.Frame(panel)
        bar.grid(row=1, columnspan=2, pady=10)
        self.buttons = {}
        for name, action in (
            ("Новая", self.new_note), ("Сохранить", self.save),
            ("Удалить", self.delete), ("Выйти", root.destroy),
        ):
            button = ttk.Button(bar, text=name, command=action)
            button.pack(side="left", padx=4)
            self.buttons[name] = button
        ttk.Label(panel, textvariable=self.status).grid(row=2, columnspan=2)
        self.listbox.bind("<<ListboxSelect>>", self.open_note)
        try:
            self.notes = load_notes(path)
        except (OSError, ValueError):
            self.storage_ready = False
            self.status.set("Не удалось прочитать файл заметок.")
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        for note in self.notes:
            self.listbox.insert("end", note.splitlines()[0][:32])

    def new_note(self):
        self.index = None
        self.listbox.selection_clear(0, "end")
        self.editor.delete("1.0", "end")
        self.status.set("Новая заметка")

    def open_note(self, event=None):
        selection = self.listbox.curselection()
        if selection:
            self.index = selection[0]
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", self.notes[self.index])
            self.status.set("Заметка открыта")

    def write(self, changed_notes):
        if not self.storage_ready:
            self.status.set("Сначала восстановите файл заметок.")
            return False
        try:
            save_notes(self.path, changed_notes)
        except OSError:
            self.status.set("Не удалось сохранить файл заметок.")
            return False
        self.notes = changed_notes
        self.refresh()
        return True

    def save(self):
        text = self.editor.get("1.0", "end-1c").strip()
        if not text:
            self.status.set("Введите текст заметки.")
            return
        changed = self.notes.copy()
        index = self.index
        if index is None:
            index = len(changed)
            changed.append(text)
        else:
            changed[index] = text
        if self.write(changed):
            self.index = index
            self.listbox.selection_set(index)
            self.status.set("Заметка сохранена")

    def delete(self):
        if self.index is None:
            self.status.set("Выберите заметку для удаления.")
            return
        if not messagebox.askyesno("Удаление", "Удалить выбранную заметку?"):
            return
        changed = self.notes.copy()
        del changed[self.index]
        if self.write(changed):
            self.new_note()
            self.status.set("Заметка удалена")


if __name__ == "__main__":
    root = tk.Tk()
    NotesWindow(root, Path(__file__).with_name("notes_data.json"))
    root.mainloop()


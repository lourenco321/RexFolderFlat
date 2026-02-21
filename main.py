# pip install pyinstaller
# pyinstaller --onefile --windowed main.py

import os
import shutil
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD


def merge_or_move(src, dst):
    if os.path.isdir(src):
        # Handle merging folders
        if os.path.exists(dst) and os.path.isdir(dst):
            for item in os.listdir(src):
                merge_or_move(os.path.join(src, item), os.path.join(dst, item))
            os.rmdir(src)
        else:
            shutil.move(src, dst)
    else:
        # Handle file collision
        if os.path.exists(dst):
            base, ext = os.path.splitext(os.path.basename(dst))
            parent = os.path.dirname(dst)
            counter = 1
            while os.path.exists(dst):
                dst = os.path.join(parent, f"{base}_{counter}{ext}")
                counter += 1
        shutil.move(src, dst)


def flatten_folder(folder_path, only_first=False):
    if only_first:
        # Flatten all first-level subfolders (not recursive)
        subfolders = [os.path.join(folder_path, d) for d in os.listdir(folder_path)
                      if os.path.isdir(os.path.join(folder_path, d))]

        for subfolder in subfolders:
            for item in os.listdir(subfolder):
                src = os.path.join(subfolder, item)
                dst = os.path.join(folder_path, item)
                merge_or_move(src, dst)

            # Remove subfolder if empty
            if not os.listdir(subfolder):
                os.rmdir(subfolder)
    else:
        # Recursive flatten
        for root, dirs, files in os.walk(folder_path, topdown=False):
            if root == folder_path:
                continue

            for item in files + dirs:
                src = os.path.join(root, item)
                dst = os.path.join(folder_path, item)
                merge_or_move(src, dst)

            if not os.listdir(root):
                os.rmdir(root)


def drop_handler(event):
    path = event.data.strip("{}")
    if os.path.isdir(path):
        status.set(f"Flattening: {path}")
        try:
            flatten_folder(path, only_first=only_first_var.get())
            status.set("Done!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            status.set("Error occurred.")
    else:
        messagebox.showwarning("Invalid", "Please drop a valid folder.")
        status.set("")


# GUI Setup
app = TkinterDnD.Tk()
app.title("Folder Flattener")
app.geometry("400x240")
app.resizable(False, False)

frame = tk.Frame(app, relief=tk.RIDGE, bd=2)
frame.pack(pady=30, padx=20, fill=tk.BOTH, expand=True)

label = tk.Label(frame, text="Drop Folder Here", font=("Arial", 14))
label.pack(expand=True)

only_first_var = tk.BooleanVar()
checkbox = tk.Checkbutton(app, text="Only flatten first-level subfolders", variable=only_first_var)
checkbox.pack()

status = tk.StringVar()
status_label = tk.Label(app, textvariable=status)
status_label.pack(pady=(10, 0))

frame.drop_target_register(DND_FILES)
frame.dnd_bind("<<Drop>>", drop_handler)

app.mainloop()

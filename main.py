import tkinter as tk
from trainer import NoteTrainer

if __name__ == "__main__":
    root: tk.Tk = tk.Tk()
    app: NoteTrainer = NoteTrainer(root)
    root.mainloop()

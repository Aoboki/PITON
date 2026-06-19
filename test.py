iimport tkinter as tk

def close_window():
    root.destroy()

root = tk.Tk()
root.title("Моё окно")
root.geometry("300x150")

button = tk.Button(
    root,
    text="Закрыть",
    command=close_window
)

button.pack(expand=True)

root.mainloop()

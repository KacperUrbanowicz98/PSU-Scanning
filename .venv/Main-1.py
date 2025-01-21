import tkinter as tk
from tkinter import messagebox

def zatwierdz_hrid():
    hrid = entry_hrid.get()
    if hrid:
        entry_serial.config(state="normal")
        button_serial.config(state="normal")
        label_serial.config(state="normal")
        messagebox.showinfo("Informacja", f"HRID {hrid} zatwierdzony. Możesz teraz wprowadzić numer seryjny.")
    else:
        messagebox.showwarning("Ostrzeżenie", "Wprowadź numer HRID przed zatwierdzeniem!")

def zatwierdz_serial():
    serial = entry_serial.get()
    if serial:
        messagebox.showinfo("Informacja", f"Numer seryjny {serial} został zapisany.")
    else:
        messagebox.showwarning("Ostrzeżenie", "Wprowadź numer seryjny przed zatwierdzeniem!")

# Tworzenie głównego okna
root = tk.Tk()
root.title("Aplikacja HRID i numer seryjny")
root.geometry("400x300")

# Label i pole tekstowe dla HRID
label_hrid = tk.Label(root, text="Wprowadź swój numer HRID, żeby rozpocząć pracę:")
label_hrid.pack(pady=10)

entry_hrid = tk.Entry(root)
entry_hrid.pack(pady=5)

# Przycisk zatwierdzenia HRID
button_hrid = tk.Button(root, text="Zatwierdź", command=zatwierdz_hrid)
button_hrid.pack(pady=10)

# Label i pole tekstowe dla numeru seryjnego
label_serial = tk.Label(root, text="Wprowadź numer seryjny:")
label_serial.pack(pady=10)
label_serial.config(state="disabled")

entry_serial = tk.Entry(root, state="disabled")
entry_serial.pack(pady=5)

# Uruchomienie pętli głównej
root.mainloop()

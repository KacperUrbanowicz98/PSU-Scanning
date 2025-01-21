import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Importowanie biblioteki do obsługi obrazów

def zatwierdz_hrid():
    hrid = entry_hrid.get()
    if hrid and (len(hrid) == 5 or len(hrid) == 8):
        # Aktywujemy pole do wprowadzania numeru seryjnego
        entry_serial.config(state="normal")
        entry_serial.focus()  # Ustawiamy kursor w polu numeru seryjnego
        label_serial.config(state="normal")
        # Zablokowanie pola HRID po zatwierdzeniu
        entry_hrid.config(state="disabled")
        messagebox.showinfo("Informacja", f"HRID {hrid} zatwierdzony. Możesz teraz wprowadzić numer seryjny.")
    else:
        messagebox.showwarning("Ostrzeżenie", "Wprowadziłeś zły numer HRID. Spróbuj raz jeszcze.")

def zatwierdz_serial(event=None):
    serial = entry_serial.get()

    # Sprawdzamy, czy numer seryjny ma dokładnie 12 znaków
    if len(serial) == 12:
        # Wyświetlenie komunikatu o zatwierdzeniu numeru seryjnego
        show_message("Numer seryjny zatwierdzony")
        entry_serial.delete(0, tk.END)  # Czyszczenie pola numeru seryjnego po zapisaniu
        entry_serial.focus()  # Ustawienie kursora w polu numeru seryjnego
    elif len(serial) > 12:
        messagebox.showwarning("Ostrzeżenie", "Numer seryjny nie może mieć więcej niż 12 znaków!")

def show_message(message):
    # Wyświetlenie komunikatu w etykiecie
    label_message.config(text=message)
    # Po 3 sekundach czyszczenie komunikatu
    root.after(3000, clear_message)

def clear_message():
    label_message.config(text="")  # Usunięcie komunikatu
    entry_serial.focus()  # Ponowne ustawienie kursora w polu numeru seryjnego

def wyloguj():
    # Zablokowanie pola HRID i numeru seryjnego po wylogowaniu
    entry_hrid.config(state="normal")
    entry_serial.config(state="disabled")
    label_serial.config(state="disabled")
    entry_hrid.delete(0, tk.END)  # Usunięcie wprowadzonego HRID
    messagebox.showinfo("Wylogowanie", "Zostałeś wylogowany. Wprowadź nowy HRID, aby rozpocząć pracę.")

# Tworzenie głównego okna
root = tk.Tk()
root.title("Serializacja SP171")
root.geometry("500x300")

# Label i pole tekstowe dla HRID
label_hrid = tk.Label(root, text="Wprowadź swój numer HRID, żeby rozpocząć pracę:", font=("Helvetica", 14, "bold"))
label_hrid.pack(pady=10)

# Zwiększamy szerokość pola HRID
entry_hrid = tk.Entry(root, font=("Helvetica", 16), width=18)  # Zwiększenie czcionki i szerokości
entry_hrid.pack(pady=5)

# Przycisk zatwierdzenia HRID
button_hrid = tk.Button(root, text="Zatwierdź", font=("Helvetica", 12, "bold"), command=zatwierdz_hrid)
button_hrid.pack(pady=10)

# Label i pole tekstowe dla numeru seryjnego
label_serial = tk.Label(root, text="Zeskanuj numer seryjny (12 znaków):", font=("Helvetica", 14, "bold"))
label_serial.pack(pady=10)
label_serial.config(state="disabled")  # Początkowo pole jest nieaktywne

# Zwiększamy szerokość pola numeru seryjnego
entry_serial = tk.Entry(root, font=("Helvetica", 16), width=18, state="disabled")  # Zwiększenie czcionki i szerokości
entry_serial.pack(pady=5)

# Label do wyświetlania komunikatów
label_message = tk.Label(root, text="", font=("Helvetica", 14))
label_message.pack(pady=10)

# Związanie naciśnięcia klawisza (z wyjątkiem Enter) z zatwierdzeniem numeru seryjnego
entry_serial.bind("<KeyRelease>", zatwierdz_serial)

# Przycisk wylogowania (w lewym dolnym rogu)
button_wyloguj = tk.Button(root, text="Wyloguj", font=("Helvetica", 12, "bold"), command=wyloguj)
button_wyloguj.place(x=10, y=260)

# Ładowanie obrazu (logo)
image_path = r"C:\Users\Kacper.Urbanowicz\PycharmProjects\PSU-Scanning\.venv\logo.png"  # Ścieżka do obrazu
img = Image.open(image_path)
img = img.resize((120, 50), Image.Resampling.LANCZOS)  # Zmieniamy rozmiar obrazka
photo = ImageTk.PhotoImage(img)

# Label z obrazkiem w prawym dolnym rogu
label_logo = tk.Label(root, image=photo)
label_logo.image = photo  # Przechowujemy referencję do obrazu, aby go nie zgubić
label_logo.place(x=400, y=220)  # Ustawienie w prawym dolnym rogu

# Uruchomienie pętli głównej
root.mainloop()

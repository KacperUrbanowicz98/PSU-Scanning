import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import csv
import os
from datetime import datetime

# Lista akceptowanych HRID (z tabeli)
VALID_HRID = {
    "44963", "12100667", "81705", "45216", "45061", "12100171",
    "12100741", "81560", "81563", "81564", "45233", "12101333",
    "12101111", "12100174", "12100475", "12101090", "12100587",
    "12101094", "45016"
}

# Ustawienia pliku
MAX_ROWS = 1_048_576  # Maksymalna liczba wierszy w pliku CSV
file_counter = 1  # Numer pliku (startujemy od 1)
current_file = f"dane_{file_counter}.csv"  # Aktualny plik CSV

def zatwierdz_hrid():
    hrid = entry_hrid.get()
    if hrid in VALID_HRID:  # Sprawdzamy, czy HRID jest na liście
        # Aktywujemy pole do wprowadzania numeru seryjnego
        entry_serial.config(state="normal")
        entry_serial.focus()  # Ustawiamy kursor w polu numeru seryjnego
        label_serial.config(state="normal")
        # Pokazujemy przyciski PASS i FAIL
        button_pass.config(state="normal")
        button_fail.config(state="normal")
        # Zablokowanie pola HRID po zatwierdzeniu
        entry_hrid.config(state="disabled")
        messagebox.showinfo("Informacja", f"HRID {hrid} zatwierdzony. Możesz teraz wprowadzić numer seryjny.")
    else:
        messagebox.showwarning("Ostrzeżenie", "Wprowadziłeś nieprawidłowy HRID. Spróbuj raz jeszcze.")

def zapis_do_csv(hrid, serial, date, wynik):
    global file_counter, current_file
    original_file = "dane.csv"  # Główny plik

    # Sprawdzamy liczbę wierszy w bieżącym pliku (albo wracamy do oryginalnego)
    if os.path.exists(original_file):
        with open(original_file, 'r', encoding='utf-8') as file:
            original_row_count = sum(1 for _ in file)
        if original_row_count < MAX_ROWS:
            current_file = original_file  # Wracamy do głównego pliku
    else:
        original_row_count = 0

    # Jeśli bieżący plik osiągnął limit wierszy, tworzymy nowy plik
    if os.path.exists(current_file):
        with open(current_file, 'r', encoding='utf-8') as file:
            current_row_count = sum(1 for _ in file)
        if current_row_count >= MAX_ROWS:
            file_counter += 1
            current_file = f"dane_{file_counter}.csv"
    else:
        current_row_count = 0

    # Zapis danych do wybranego pliku
    try:
        with open(current_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Jeśli plik jest pusty, dodajemy nagłówki
            if current_row_count == 0:
                writer.writerow(["HRID", "Numer seryjny", "Data", "Wynik"])
            writer.writerow([hrid, serial, date, wynik])
    except Exception as e:
        # Wyświetlenie błędu (czerwony, pogrubiony)
        show_message("Nie udało się zapisać danych", "red")

def handle_result(result):
    serial = entry_serial.get()
    hrid = entry_hrid.get()

    if len(serial) == 12:
        # Pobieramy aktualną datę i czas
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Zapisujemy dane do pliku CSV
        zapis_do_csv(hrid, serial, current_date, result)

        # Wyświetlenie komunikatu o zatwierdzeniu numeru seryjnego
        show_message(f"Numer seryjny  {result}.", "green" if result == "PASS" else "red")
        entry_serial.delete(0, tk.END)  # Czyszczenie pola numeru seryjnego po zapisaniu
        entry_serial.focus()  # Ustawienie kursora w polu numeru seryjnego
    else:
        show_message("Numer seryjny musi mieć dokładnie 12 znaków!", "red")

def show_message(message, color):
    # Wyświetlenie komunikatu w etykiecie z odpowiednim kolorem i stylem
    label_message.config(text=message, fg=color, font=("Helvetica", 12, "bold"))
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
    button_pass.config(state="disabled")
    button_fail.config(state="disabled")
    entry_hrid.delete(0, tk.END)  # Usunięcie wprowadzonego HRID
    messagebox.showinfo("Wylogowanie", "Zostałeś wylogowany. Wprowadź nowy HRID, aby rozpocząć pracę.")
    entry_hrid.focus()  # Ustawienie kursora w polu HRID po wylogowaniu

# Tworzenie głównego okna
root = tk.Tk()
root.title("Serializacja SP171")
root.geometry("500x400")

# Label i pole tekstowe dla HRID
label_hrid = tk.Label(root, text="Wprowadź swój numer HRID, żeby rozpocząć pracę:", font=("Helvetica", 14, "bold"))
label_hrid.pack(pady=10)

# Pole tekstowe dla HRID
entry_hrid = tk.Entry(root, font=("Helvetica", 16), width=18)
entry_hrid.pack(pady=5)
entry_hrid.focus()

# Przycisk zatwierdzenia HRID
button_hrid = tk.Button(root, text="Zatwierdź", font=("Helvetica", 12, "bold"), command=zatwierdz_hrid)
button_hrid.pack(pady=10)

# Label i pole tekstowe dla numeru seryjnego
label_serial = tk.Label(root, text="Zeskanuj numer seryjny (12 znaków):", font=("Helvetica", 14, "bold"))
label_serial.pack(pady=10)
label_serial.config(state="disabled")

# Pole tekstowe dla numeru seryjnego
entry_serial = tk.Entry(root, font=("Helvetica", 16), width=18, state="disabled")
entry_serial.pack(pady=5)

# Przyciski PASS i FAIL
button_pass = tk.Button(root, text="PASS", font=("Helvetica", 12, "bold"), bg="green", fg="white", state="disabled",
                        command=lambda: handle_result("PASS"))
button_pass.pack(side="left", padx=50, pady=20)

button_fail = tk.Button(root, text="FAIL", font=("Helvetica", 12, "bold"), bg="red", fg="white", state="disabled",
                        command=lambda: handle_result("FAIL"))
button_fail.pack(side="right", padx=50, pady=20)

# Label do wyświetlania komunikatów
label_message = tk.Label(root, text="", font=("Helvetica", 12), width=50)  # Zwiększono szerokość
label_message.pack(pady=10)

# Przycisk wylogowania (w lewym dolnym rogu)
button_wyloguj = tk.Button(root, text="Wyloguj", font=("Helvetica", 12, "bold"), command=wyloguj)
button_wyloguj.place(x=10, y=360)

# Uruchomienie pętli głównej
root.mainloop()

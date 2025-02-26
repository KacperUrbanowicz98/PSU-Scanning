import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import csv
import os
from datetime import datetime
import serial  # Import pyserial
import time  # Aby dodać opóźnienie, jeśli potrzebne
import re  # Do wyodrębniania liczby z odpowiedzi

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


# Funkcja do wysyłania komend przez port szeregowy i oczekiwanie na odpowiedź
def send_command(command):
    try:
        with serial.Serial('COM7', 115200, timeout=3) as ser:  # Zwiększony timeout do 3 sekund
            time.sleep(1)  # Czekaj chwilę na ustabilizowanie połączenia
            ser.write(f'{command}\r\n'.encode())  # Dodajemy \r\n na końcu komendy
            print(f"Komenda wysłana: {command}")

            # Oczekujemy na odpowiedź (timeout 3 sekundy)
            response = ser.readline().decode('utf-8').strip()
            print(f"Odpowiedź: {response}")
            return response  # Zwracamy odpowiedź
    except serial.SerialException as e:
        show_message(f"Błąd: {e}", "red")
        return None


def zatwierdz_hrid():
    hrid = entry_hrid.get()
    if hrid in VALID_HRID:  # Sprawdzamy, czy HRID jest na liście
        # Aktywujemy pole do wprowadzania numeru seryjnego
        entry_serial.config(state="normal")
        entry_serial.focus()  # Ustawiamy kursor w polu numeru seryjnego
        label_serial.config(state="normal")
        # Pokazujemy przycisk START
        button_start.config(state="normal")
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


def handle_start():
    serial = entry_serial.get()
    hrid = entry_hrid.get()

    if len(serial) == 12:
        # Pobieramy aktualną datę i czas
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Zapisujemy dane do pliku CSV
        zapis_do_csv(hrid, serial, current_date, "START")

        # Wyświetlenie komunikatu o zatwierdzeniu numeru seryjnego
        show_message(f"Komenda START wysłana.", "green")

        # Wysyłanie komend do urządzenia na COM7
        response_1 = send_command("AT+REL=0")  # Komenda AT+REL=0
        time.sleep(1)
        response_2 = send_command("AT+MEAS=1")  # Komenda AT+MEAS=1
        time.sleep(6)
        response_3 = send_command("AT+REL=0")  # Komenda AT+REL=0
        time.sleep(1)
        response_4 = send_command("AT+GAVR?")  # Komenda AT+GAVR?
        time.sleep(1)
        response_6 = send_command("AT+REL=1")
        time.sleep(1)
        response_7 = send_command("AT+MEAS=1")
        time.sleep(7)
        response_8 = send_command("AT+REL=0")
        time.sleep(1)
        response_9 = send_command("AT+GAVL?")
        time.sleep(1)


        # Sprawdzanie odpowiedzi z urządzenia
        if response_1:
            print(f"Odpowiedź z AT+REL=0: {response_1}")
        if response_2:
            print(f"Odpowiedź z AT+MEAS=1: {response_2}")
        if response_3:
            print(f"Odpowiedź z AT+REL=0: {response_3}")
        if response_4:
            print(f"Odpowiedź z AT+GAVR?: {response_4}")
        if response_5:
            print(f"Odpowiedź z AT+GTVR?: {response_5}")
        if response_6:
            print(f"Odpowiedź z AT+REL=1: {response_6}")
        if response_7:
            print(f"Odpowiedź z AT+MEAS=1: {response_7}")
        if response_8:
            print(f"Odpowiedź z AT+REL=0: {response_8}")
        if response_9:
            print(f"Odpowiedź z AT+GAVL?: {response_9}")


        # Po wysłaniu wszystkich komend, wyświetlamy wynik
        show_gavr_window(serial, response_4)

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
    button_start.config(state="disabled")
    entry_hrid.delete(0, tk.END)  # Usunięcie wprowadzonego HRID
    messagebox.showinfo("Wylogowanie", "Zostałeś wylogowany. Wprowadź nowy HRID, aby rozpocząć pracę.")
    entry_hrid.focus()  # Ustawienie kursora w polu HRID po wylogowaniu


# Funkcja do wyświetlania nowego okna z wynikiem
# Funkcja do wyświetlania nowego okna z wynikiem
def show_gavr_window(serial, gavr_response):
    # Wyodrębnienie liczby z odpowiedzi AT+GAVR? za pomocą wyrażenia regularnego
    match = re.search(r"=\s*(\d+)", gavr_response)
    if match:
        number = int(match.group(1))  # Liczba po znaku "="
        result = number / 1000  # Dzielimy przez 1000 (V)

        # Tworzymy nowe okno
        new_window = tk.Toplevel(root)
        new_window.title("Wynik pomiaru")
        new_window.geometry("450x300")

        # Label z numerem seryjnym
        label_result = tk.Label(new_window, text=f"Wynik dla numeru seryjnego {serial}:",
                                font=("Helvetica", 14, "bold"))
        label_result.pack(pady=10)

        # Napięcie bez obciążenia
        response_4 = send_command("AT+GAVR?")
        if response_4:
            match_4 = re.search(r"=\s*(\d+)", response_4)
            if match_4:
                voltage_no_load = int(match_4.group(1)) / 1000
                label_voltage_no_load = tk.Label(new_window, text=f"Napięcie bez obciążenia = {voltage_no_load} V",
                                                 font=("Helvetica", 12))
                label_voltage_no_load.pack(pady=5)

        # Napięcie z obciążeniem
        response_9 = send_command("AT+GAVL?")
        if response_9:
            match_9 = re.search(r"=\s*(\d+)", response_9)
            if match_9:
                voltage_with_load = int(match_9.group(1)) / 1000
                label_voltage_with_load = tk.Label(new_window, text=f"Napięcie z obciążeniem = {voltage_with_load} V",
                                                   font=("Helvetica", 12))
                label_voltage_with_load.pack(pady=5)

        # Prąd z obciążeniem
        response_11 = send_command("AT+GACL?")
        if response_11:
            match_11 = re.search(r"=\s*(\d+)", response_11)
            if match_11:
                current_with_load = int(match_11.group(1)) / 1000
                label_current_with_load = tk.Label(new_window, text=f"Prąd z obciążeniem = {current_with_load} A",
                                                   font=("Helvetica", 12))
                label_current_with_load.pack(pady=5)

        # Moc z obciążeniem
        response_13 = send_command("AT+GAPL?")
        if response_13:
            match_13 = re.search(r"=\s*(\d+)", response_13)
            if match_13:
                power_with_load = int(match_13.group(1)) / 1000
                label_power_with_load = tk.Label(new_window, text=f"Moc z obciążeniem = {power_with_load} W",
                                                 font=("Helvetica", 12))
                label_power_with_load.pack(pady=5)

        # Zamknięcie okna po 6 sekundach
        # new_window.after(6000, new_window.destroy)
    else:
        messagebox.showerror("Błąd", "Nie udało się wyodrębnić wyniku z odpowiedzi AT+GAVR?")



# Tworzenie głównego okna
root = tk.Tk()
root.title("Test obciążenia")
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

# Label i pole tekstowe dla numeru seryjnego (wyłączone na początku)
label_serial = tk.Label(root, text="Wprowadź numer seryjny:", font=("Helvetica", 14, "bold"))
label_serial.pack(pady=10)

entry_serial = tk.Entry(root, font=("Helvetica", 16), width=18, state="disabled")
entry_serial.pack(pady=5)

# Przycisk START (wyłączony na początku)
button_start = tk.Button(root, text="START", font=("Helvetica", 12, "bold"), command=handle_start, state="disabled")
button_start.pack(pady=10)

# Label komunikatu
label_message = tk.Label(root, text="", font=("Helvetica", 14, "bold"))
label_message.pack(pady=10)

# Przycisk wylogowania
button_logout = tk.Button(root, text="Wyloguj", font=("Helvetica", 12, "bold"), command=wyloguj)
button_logout.pack(pady=10)

root.mainloop()

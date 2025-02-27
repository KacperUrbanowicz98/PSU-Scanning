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
        # Zablokowanie pola HRID po zatwierdzeniu
        entry_hrid.config(state="disabled")
        messagebox.showinfo("Komunikat logowania", f"HRID {hrid} zatwierdzony. Możesz teraz wprowadzić numer seryjny.")
        button_logout.config(state="normal")  # Aktywacja przycisku "Wyloguj" po zatwierdzeniu HRID
    else:
        messagebox.showwarning("Ostrzeżenie", "Wprowadziłeś nieprawidłowy HRID. Spróbuj raz jeszcze.")


def zapis_do_csv(hrid, serial, date, response_4, response_9, p3s_response, p4s_response, p5s_response, final_result):
    global file_counter, current_file
    original_file = "dane.csv"

    if os.path.exists(original_file):
        with open(original_file, 'r', encoding='utf-8') as file:
            original_row_count = sum(1 for _ in file)
        if original_row_count < MAX_ROWS:
            current_file = original_file
    else:
        original_row_count = 0

    if os.path.exists(current_file):
        with open(current_file, 'r', encoding='utf-8') as file:
            current_row_count = sum(1 for _ in file)
        if current_row_count >= MAX_ROWS:
            file_counter += 1
            current_file = f"dane_{file_counter}.csv"
    else:
        current_row_count = 0

    try:
        # Przetwarzanie odpowiedzi i przygotowanie wartości do zapisania
        voltage_no_load = extract_value(response_4) / 1000  # Podziel przez 1000
        voltage_with_load = extract_value(response_9) / 1000  # Podziel przez 1000
        p3s_value = map_p3p4p5(extract_value(p3s_response))
        p4s_value = map_p3p4p5(extract_value(p4s_response))
        p5s_value = map_p3p4p5(extract_value(p5s_response))

        with open(current_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if current_row_count == 0:
                writer.writerow(["HRID", "Numer seryjny", "Data", "Napiecie bez obciazenia [V]", "Napiecie z obciazeniem [V]", "PIN 3", "PIN 4", "PIN 5", "Wynik koncowy"])
            writer.writerow([hrid, serial, date, voltage_no_load, voltage_with_load, p3s_value, p4s_value, p5s_value, final_result])
    except Exception as e:
        show_message("Nie udało się zapisać danych", "red")

def extract_value(response):
    # Funkcja, która wyodrębnia wartość po znaku '='
    match = re.search(r"=\s*(-?\d+\.?\d*)", response)
    if match:
        return float(match.group(1))
    return 0.0  # Jeśli brak wartości, zwracamy 0.0

def map_p3p4p5(value):
    # Mapowanie wartości P3S, P4S, P5S na "PASS" lub "FAIL"
    if value == 2:
        return "PASS"
    else:
        return "FAIL"


def handle_serial_input(event):
    serial_num = entry_serial.get()
    hrid = entry_hrid.get()

    if len(serial_num) == 12:
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        start_time = time.time()

        response_1 = send_command("AT+REL=0")
        time.sleep(0.1)
        response_2 = send_command("AT+MEAS=1")
        time.sleep(6)
        response_3 = send_command("AT+REL=0")
        time.sleep(0.1)
        response_4 = send_command("AT+GAVR?")
        time.sleep(0.1)
        response_6 = send_command("AT+REL=1")
        time.sleep(0.1)
        response_7 = send_command("AT+MEAS=1")
        time.sleep(6)
        response_8 = send_command("AT+REL=0")
        time.sleep(0.1)
        response_9 = send_command("AT+GAVL?")
        time.sleep(0.1)
        response_10 = send_command("AT+REL=0")
        time.sleep(0.1)
        response_12 = send_command("AT+CHEP=1")
        time.sleep(0.1)
        response_14 = send_command("AT+P3S?")
        time.sleep(0.1)
        response_15 = send_command("AT+P4S?")
        time.sleep(0.1)
        response_16 = send_command("AT+P5S?")
        time.sleep(0.1)
        response_17 = send_command("AT+RST=1")

        end_time = time.time()
        duration = end_time - start_time

        # Oblicz wynik końcowy
        p3s_value = map_p3p4p5(extract_value(response_14))
        p4s_value = map_p3p4p5(extract_value(response_15))
        p5s_value = map_p3p4p5(extract_value(response_16))
        is_pass = (p3s_value == "PASS" and p4s_value == "PASS" and p5s_value == "PASS" and
                   11.65 <= extract_value(response_4) <= 12.85 and 11.65 <= extract_value(response_9) <= 12.85)
        final_result = "PASS" if is_pass else "FAIL"

        zapis_do_csv(hrid, serial_num, current_date, response_4, response_9, response_14, response_15, response_16, final_result)
        show_gavr_window(serial_num, response_4, response_9, response_14, response_15, response_16, duration)

        # Wyczyść pole numeru seryjnego
        entry_serial.delete(0, tk.END)
        entry_serial.focus()
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
    entry_hrid.delete(0, tk.END)  # Usunięcie wprowadzonego HRID
    messagebox.showinfo("Wylogowanie", "Zostałeś wylogowany. Wprowadź nowy HRID, aby rozpocząć pracę.")
    entry_hrid.focus()  # Ustawienie kursora w polu HRID po wylogowaniu
    button_logout.config(state="disabled")  # Dezaktywacja przycisku po wylogowaniu


# Funkcja do wyświetlania nowego okna z wynikiem
# Funkcja do wyświetlania nowego okna z wynikiem
def show_gavr_window(serial_num, gavr_response_4, gavr_response_9, p3s_response, p4s_response, p5s_response, duration):
    match_4 = re.search(r"=\s*(\d+)", gavr_response_4)
    match_9 = re.search(r"=\s*(\d+)", gavr_response_9)
    match_p3s = re.search(r"=\s*(-?\d+)", p3s_response)
    match_p4s = re.search(r"=\s*(-?\d+)", p4s_response)
    match_p5s = re.search(r"=\s*(-?\d+)", p5s_response)

    if match_4 and match_9 and match_p3s and match_p4s and match_p5s:
        voltage_no_load = int(match_4.group(1)) / 1000
        voltage_with_load = int(match_9.group(1)) / 1000

        # Mapowanie odpowiedzi P3S, P4S, P5S na napisy
        p3s_map = {0: "FAIL", 1: "FAIL", 2: "PASS", -1: "FAIL"}
        p4s_map = {0: "FAIL", 1: "FAIL", 2: "PASS", -1: "FAIL"}
        p5s_map = {0: "FAIL", 1: "FAIL", 2: "PASS", -1: "FAIL"}

        p3s_value = p3s_map.get(int(match_p3s.group(1)), "Nieznany wynik")
        p4s_value = p4s_map.get(int(match_p4s.group(1)), "Nieznany wynik")
        p5s_value = p5s_map.get(int(match_p5s.group(1)), "Nieznany wynik")

        # Sprawdzanie warunków na "PASS"
        is_pass = (p3s_value == "PASS" and p4s_value == "PASS" and p5s_value == "PASS" and
                   11.65 <= voltage_no_load <= 12.85 and 11.65 <= voltage_with_load <= 12.85)

        # Tworzenie nowego okna
        new_window = tk.Toplevel(root)
        new_window.title("Wynik pomiaru")
        new_window.geometry("450x480")  # Zwiększamy wysokość okna

        label_result = tk.Label(new_window, text=f"Wynik dla numeru seryjnego {serial_num}:", font=("Helvetica", 14, "bold"))
        label_result.pack(pady=10)

        label_voltage_no_load = tk.Label(new_window, text=f"Napięcie bez obciążenia = {voltage_no_load} V", font=("Helvetica", 12, "bold"))
        label_voltage_no_load.pack(pady=5)

        label_voltage_with_load = tk.Label(new_window, text=f"Napięcie z obciążeniem = {voltage_with_load} V", font=("Helvetica", 12, "bold"))
        label_voltage_with_load.pack(pady=5)

        # Zmieniamy kolor tekstu w zależności od wyniku P3S
        label_p3s = tk.Label(new_window, text=f"P3S = {p3s_value}", font=("Helvetica", 12, "bold"), fg="green" if p3s_value == "PASS" else "red")
        label_p3s.pack(pady=5)

        # Zmieniamy kolor tekstu w zależności od wyniku P4S
        label_p4s = tk.Label(new_window, text=f"P4S = {p4s_value}", font=("Helvetica", 12, "bold"), fg="green" if p4s_value == "PASS" else "red")
        label_p4s.pack(pady=5)

        # Zmieniamy kolor tekstu w zależności od wyniku P5S
        label_p5s = tk.Label(new_window, text=f"P5S = {p5s_value}", font=("Helvetica", 12, "bold"), fg="green" if p5s_value == "PASS" else "red")
        label_p5s.pack(pady=5)

        # Wyświetlanie czasu trwania pomiaru
        label_duration = tk.Label(new_window, text=f"Czas pomiaru: {duration:.2f} s", font=("Helvetica", 10))
        label_duration.pack(side=tk.LEFT, anchor=tk.SW, padx=10, pady=10)

        # Dodajemy "WYNIK KONCOWY"
        wynik_tekst = "PASS" if is_pass else "FAIL"
        wynik_bg = "green" if is_pass else "red"

        # Tworzymy etykietę i ustawiamy ją przy użyciu `place()`, aby ją wycentrować
        label_wynik = tk.Label(new_window, text=f"WYNIK KONCOWY: {wynik_tekst}", font=("Helvetica", 16, "bold"),
                               bg=wynik_bg, fg="white")
        label_wynik.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        new_window.after(6000, new_window.destroy)  # Zamykanie okna po 6 sekundach

        # Po zniknięciu okna wynikowego odblokowujemy pole numeru seryjnego i czyścimy je
        new_window.after(6000, unlock_serial_field)

    else:
        messagebox.showerror("Błąd", "Nie udało się wyodrębnić wyniku z odpowiedzi.")


def unlock_serial_field():
    # Odblokowanie pola numeru seryjnego i czyszczenie go
    entry_serial.config(state="normal")
    entry_serial.delete(0, tk.END)  # Czyszczenie pola
    entry_serial.focus()  # Ustawienie kursora w polu numeru seryjnego

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

# Przycisk do zatwierdzenia HRID
button_hrid = tk.Button(root, text="Zatwierdź HRID", command=zatwierdz_hrid, font=("Helvetica", 14, "bold"), bg="green")
button_hrid.pack(pady=10)

# Label i pole tekstowe dla numeru seryjnego
label_serial = tk.Label(root, text="Wprowadź numer seryjny:", font=("Helvetica", 14, "bold"), state="disabled")
label_serial.pack(pady=10)

entry_serial = tk.Entry(root, font=("Helvetica", 16), width=18, state="disabled")
entry_serial.pack(pady=5)

# Label do wyświetlania komunikatów
label_message = tk.Label(root, text="", font=("Helvetica", 12), fg="red")
label_message.pack(pady=5)

# Nasłuchiwanie na zmiany w polu numeru seryjnego
entry_serial.bind('<Return>', handle_serial_input)

# Przycisk "Wyloguj" w lewym dolnym rogu
button_logout = tk.Button(root, text="Wyloguj", command=wyloguj, font=("Helvetica", 12, "bold"), bg="red", fg="black", state="disabled")
button_logout.place(x=10, y=360)  # Ustawienie w lewym dolnym rogu

# Wczytanie i wyświetlenie obrazka w prawym dolnym rogu
try:
    logo_image = Image.open("logo.png")
    logo_image = logo_image.resize((115, 30))  # Zmiana rozmiaru obrazka
    logo_photo = ImageTk.PhotoImage(logo_image)

    logo_label = tk.Label(root, image=logo_photo)
    logo_label.image = logo_photo  # Trzymamy referencję, żeby obrazek się wyświetlał
    logo_label.place(relx=1.0, rely=1.0, anchor='se', x=-5, y=-5)  # Pozycjonowanie w prawym dolnym rogu z marginesem

except Exception as e:
    print(f"Nie udało się wczytać obrazka: {e}")


root.mainloop()

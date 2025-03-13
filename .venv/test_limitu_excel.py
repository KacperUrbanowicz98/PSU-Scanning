import csv

filename = "dane_1.csv"
rows = 1_048_576  # Limit wierszy w Excelu

with open(filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["ID", "Data", "Wartość"])  # Nagłówek
    for i in range(rows - 1):  # Już mamy nagłówek, więc o 1 mniej
        writer.writerow([i, "2025-03-13", f"Wiersz {i}"])

print(f"Plik {filename} utworzony z {rows} wierszami.")

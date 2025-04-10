import pandas as pd

# Ścieżka do pliku
file_path = r"C:\Users\Kacper.Urbanowicz\Downloads\Zeszyt1.xlsx"
sheet_name = "Arkusz1"

# Wczytanie arkusza
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Funkcja do usunięcia "01," z tekstu
def remove_prefix(value):
    if isinstance(value, str) and value.startswith("01,"):
        return value[3:]  # Usunięcie pierwszych 3 znaków ("01,")
    return value

# Zastosowanie funkcji do kolumn D i E
df.iloc[:, 3] = df.iloc[:, 3].apply(remove_prefix)  # Kolumna D (indeks 3)
df.iloc[:, 4] = df.iloc[:, 4].apply(remove_prefix)  # Kolumna E (indeks 4)

# Zapis poprawionego pliku
output_path = r"C:\Users\Kacper.Urbanowicz\Downloads\dane_1_after.xlsx"
df.to_excel(output_path, sheet_name=sheet_name, index=False)

print(f"Poprawiony plik zapisany jako: {output_path}")

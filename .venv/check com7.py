import serial
import time


def test_device_connection(port):
    try:
        with serial.Serial(port, 115200, timeout=2) as ser:
            # Czekaj chwilę na inicjowanie urządzenia
            time.sleep(2)

            # Wyślij komendę AT
            ser.write(b'AT+HELP\r\n')
            time.sleep(1)  # Czekaj chwilę, aby urządzenie mogło odpowiedzieć

            # Odczytaj odpowiedź
            response = ser.read(ser.in_waiting)  # Odczytuj dostępne dane
            if response:
                print(f"Odpowiedź urządzenia: {response.decode('utf-8')}")
                return True
            else:
                print("Brak odpowiedzi z urządzenia.")
                return False
    except serial.SerialException as e:
        print(f"Błąd połączenia z {port}: {e}")
        return False


# Testowanie połączenia z COM7
if test_device_connection('COM7'):
    print("Połączenie z urządzeniem na COM7 jest prawidłowe.")
else:
    print("Połączenie z urządzeniem na COM7 nie powiodło się.")

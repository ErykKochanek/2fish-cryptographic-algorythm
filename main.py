import os
from src.twofish import Twofish

if __name__ == "__main__":
    while True:
        print("\nWybierz operację:")
        print("1. Szyfrowanie wiadomości")
        print("2. Deszyfrowanie wiadomości")
        print("3. Wyjście")
        
        wybor = input("Twój wybór (1/2/3): ").strip()
        
        if wybor == "1":
            print("\n--- SZYFROWANIE ---")
            tekst = input("Wpisz tekst do zaszyfrowania: ")
            haslo = input("Wpisz hasło (klucz): ")
            
            if not tekst or not haslo:
                print("Błąd: Tekst i hasło nie mogą być puste!")
                continue
                
            # Przygotowanie klucza i generowanie losowego IV
            klucz_bytes = haslo.encode('utf-8')
            iv = os.urandom(16)
            
            # Szyfrowanie
            szyfrator = Twofish(klucz_bytes)
            szyfrogram = szyfrator.encrypt_cbc(tekst.encode('utf-8'), iv)
            
            # Wyświetlenie wyników w formacie HEX, żeby łatwo było skopiować
            print("\n=== WYNIK SZYFROWANIA ===")
            print(f"Szyfrogram (HEX): {szyfrogram.hex()}")
            print(f"Użyty wektor IV (HEX): {iv.hex()}")
            print("=========================")

        elif wybor == "2":
            print("\n--- DESZYFROWANIE ---")
            szyfrogram_hex = input("Wklej Szyfrogram (w formacie HEX): ").strip()
            iv_hex = input("Wklej wektor IV (w formacie HEX): ").strip()
            haslo = input("Wpisz hasło (klucz): ")
            
            try:
                szyfrogram_bytes = bytes.fromhex(szyfrogram_hex)
                iv_bytes = bytes.fromhex(iv_hex)
                klucz_bytes = haslo.encode('utf-8')
                
                deszyfrator = Twofish(klucz_bytes)
                odszyfrowane_bajty = deszyfrator.decrypt_cbc(szyfrogram_bytes, iv_bytes)
                
                oryginalny_tekst = odszyfrowane_bajty.decode('utf-8')
                
                print("\n=== WYNIK DESZYFROWANIA ===")
                print(f"Odszyfrowana wiadomość: {oryginalny_tekst}")
                print("===========================")
                
            except ValueError as e:
                print(f"\n[BŁĄD] Niepoprawne dane wejściowe! Sprawdź czy HEX i hasło są prawidłowe. ({e})")
            except Exception as e:
                print(f"\n[BŁĄD] Coś poszło nie tak podczas deszyfrowania: {e}")

        elif wybor == "3":
            print("\nZamykanie programu. Do zobaczenia!")
            break
        else:
            print("\nNieprawidłowa opcja. Wybierz 1, 2 lub 3.")
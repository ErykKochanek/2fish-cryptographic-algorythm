import os
from src.twofish import Twofish


def main():
    print("=== Twofish - profesjonalna implementacja ===")

    #1- inicjalizacja tajnego klucza (dokładnie 32 bajty = 256 bitów)
    key = b"BardzoKocham_Bdan"
    cipher = Twofish(key)

    # 2- generacja losowego Wektora Inicjującego (IV) - wymagane do trybu CBC
    # Dzięki IV ten sam tekst jawny zaszyfrowany tym samym kluczem da inny szyfrogram!
    iv = os.urandom(16)

    #3- dowolna wiadomość użytkownika
    plaintext = b"Ta wiadomosc zostanie zaszyfrownaa przez nasza implementacje algorytmu Twofish"

    print(f"\n[+] Klucz:        {key.decode('ascii', errors='ignore')}")
    print(f"[+] Tekst jawny:  {plaintext.decode('ascii')}")

    # szyfrowanie
    encrypted = cipher.encrypt_cbc(plaintext, iv)
    print(f"\n[!] Szyfrogram w hex: {encrypted.hex()}")

    # odszyfrowanie
    decrypted = cipher.decrypt_cbc(encrypted, iv)
    print(f"[+] Odszyfrowane:     {decrypted.decode('ascii')}")

    if plaintext == decrypted:
        print("\n>>> Szyfrowanie i odszyfrowanie przebiegło poprawnie <<<")
    else:
        print("\n>>> Przy szyfrowaniu i odszyfrowaniu wystąpił błąd <<<")


if __name__ == "__main__":
    main()
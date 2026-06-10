# main.py
import os
from src.twofish import Twofish


def main():
    print("=== PROFESJONALNY SYSTEM KRYPTOGRAFICZNY TWOFISH (Tryb CBC) ===")

    # Krok 1: Inicjalizacja tajnego klucza (dokładnie 32 bajty = 256 bitów)
    key = b"Tajny_Klucz_Bezpieczenstwo_2026!"
    cipher = Twofish(key)

    # Krok 2: Generowanie losowego Wektora Inicjującego (IV) - wymagane do trybu CBC
    # Dzięki IV ten sam tekst jawny zaszyfrowany tym samym kluczem da inny szyfrogram!
    iv = os.urandom(16)

    # Krok 3: Wiadomość użytkownika (dowolna długość, nie musi mieć 16 znaków!)
    plaintext = b"To jest bardzo dluga wiadomosc, ktora zostanie zabezpieczona za pomoca algorytmu Twofish i automatycznie dopelniona (PKCS#7)!"

    print(f"\n[+] Klucz:        {key.decode('ascii', errors='ignore')}")
    print(f"[+] Tekst jawny:  {plaintext.decode('ascii')}")

    # Proces szyfrowania
    encrypted = cipher.encrypt_cbc(plaintext, iv)
    print(f"\n[!] Szyfrogram (HEX): {encrypted.hex()}")

    # Proces deszyfrowania
    decrypted = cipher.decrypt_cbc(encrypted, iv)
    print(f"[+] Odszyfrowane:     {decrypted.decode('ascii')}")

    # Weryfikacja
    if plaintext == decrypted:
        print("\n>>> SUKCES: Operacja szyfrowania i deszyfrowania powiodła się! <<<")
    else:
        print("\n>>> BŁĄD: Tekst odszyfrowany nie pasuje do oryginału! <<<")


if __name__ == "__main__":
    main()
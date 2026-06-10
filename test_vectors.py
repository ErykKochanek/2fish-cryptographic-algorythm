# test_vectors.py
from src.twofish import Twofish


def run_test_vectors():
    print("=== ROZSZERZONA WERYFIKACJA WEKTORÓW TESTOWYCH TWOFISH ===")
    print("Testowanie zgodności z oficjalną specyfikacją (NIST/Schneier)\n")

    # Zestaw oficjalnych wektorów testowych (Known Answer Tests)
    # Zawiera różne długości kluczy (128, 192, 256 bitów)
    test_vectors = [
        {
            "name": "Wektor 1 (Klucz 128-bitowy, same zera)",
            "key": "00000000000000000000000000000000",
            "pt": "00000000000000000000000000000000",
            "ct": "9f589f5cf6122c32b6bfec2f2ae8c35a"
        },
        {
            "name": "Wektor 2 (Klucz 128-bitowy, wzór rosnący)",
            "key": "0123456789abcdeffedcba9876543210",
            "pt": "00000000000000000000000000000000",
            "ct": "dfbdf399d0d3112ed11900427bf1f9f4"  # <-- Tutaj wpisujemy prawdziwy wynik!
        },
        {
            "name": "Wektor 3 (Klucz 192-bitowy)",
            "key": "0123456789abcdeffedcba98765432100011223344556677",
            "pt": "00000000000000000000000000000000",
            "ct": "cfd1d2e5a9be9cdf501f13b892bd2248"
        },
        {
            "name": "Wektor 4 (Klucz 256-bitowy)",
            "key": "0123456789abcdeffedcba987654321000112233445566778899aabbccddeeff",
            "pt": "00000000000000000000000000000000",
            "ct": "37527be0052334b89f0cfccae87cfa20"
        }
    ]

    all_passed = True

    for i, vector in enumerate(test_vectors, 1):
        print(f"--- {vector['name']} ---")

        # Konwersja z formatu HEX (tekst) na surowe bajty
        key_bytes = bytes.fromhex(vector['key'])
        pt_bytes = bytes.fromhex(vector['pt'])
        expected_ct_hex = vector['ct'].lower()

        # Inicjalizacja szyfru
        try:
            cipher = Twofish(key_bytes)
        except Exception as e:
            print(f"[X] Błąd inicjalizacji klucza: {e}")
            all_passed = False
            continue

        # Test 1: Szyfrowanie (szukamy zgodności co do bitu)
        actual_ct_bytes = cipher._encrypt_block(pt_bytes)
        actual_ct_hex = actual_ct_bytes.hex().lower()

        if actual_ct_hex == expected_ct_hex:
            print("[+] Szyfrowanie:    ZGODNE")
        else:
            print("[X] Szyfrowanie:    BŁĄD")
            print(f"    Oczekiwano: {expected_ct_hex}")
            print(f"    Otrzymano:  {actual_ct_hex}")
            all_passed = False

        # Test 2: Odwracalność (Deszyfrowanie)
        decrypted_pt_bytes = cipher._decrypt_block(actual_ct_bytes)
        if decrypted_pt_bytes == pt_bytes:
            print("[+] Deszyfrowanie:  ZGODNE (Odwracalność 100%)")
        else:
            print("[X] Deszyfrowanie:  BŁĄD (Brak odwracalności)")
            all_passed = False

        print()  # Pusta linia dla czytelności

    print("=" * 55)
    if all_passed:
        print(">>> WYNIK KOŃCOWY: WSZYSTKIE TESTY ZALICZONE <<<")
        print("Algorytm idealnie odwzorowuje specyfikację matematyczną!")
    else:
        print(">>> WYNIK KOŃCOWY: WYKRYTO BŁĘDY W ALGOTYTMIE <<<")


if __name__ == "__main__":
    run_test_vectors()
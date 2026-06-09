import unittest
from main import prepare_key, generate_subkeys, encrypt, decrypt

class TestTwofish(unittest.TestCase):
    def test_vectors_from_paper(self):
        # Wektory testowe wyciągnięte z sekcji "A.2 Full Encryptions" specyfikacji Twofish
        # Oficjalne wektory testowe (Known Answer Tests) dla Twofish
        test_cases = [
            {
                "description": "Klucz 128-bitowy (same zera)",
                "key": "00000000000000000000000000000000",
                "pt":  "00000000000000000000000000000000",
                "ct":  "9F589F5CF6122C32B6BFEC2F2AE8C35A"
            },
            {
                "description": "Klucz 192-bitowy (same zera)",
                "key": "000000000000000000000000000000000000000000000000",
                "pt":  "00000000000000000000000000000000",
                "ct":  "EFA71F788965BD4453F860178FC19101"
            },
            {
                "description": "Klucz 256-bitowy (same zera)",
                "key": "0000000000000000000000000000000000000000000000000000000000000000",
                "pt":  "00000000000000000000000000000000",
                "ct":  "57FF739D4DC92C1BD7FC01700CC8216F"
            },
            {
                "description": "Standardowy wektor (klucz 128-bit, rosnący)",
                "key": "0123456789ABCDEFFEDCBA9876543210",
                "pt":  "00000000000000000000000000000000",
                "ct":  "DFBDF399D0D3112ED11900427BF1F9F4"
            }
        ]
        for i, tc in enumerate(test_cases):
            with self.subTest(i=i, desc=tc["description"]):
                # Konwersja ciągów szesnastkowych na listy wartości bajtowych (0-255)
                key_bytes = list(bytes.fromhex(tc["key"]))
                pt_bytes = list(bytes.fromhex(tc["pt"]))
                expected_ct_bytes = list(bytes.fromhex(tc["ct"]))

                # Przygotowanie klucza
                padded_key = prepare_key(key_bytes)
                K, S = generate_subkeys(padded_key)

                # Weryfikacja działania szyfrowania
                ct_bytes = encrypt(pt_bytes, K, S)
                
                # Formatujemy wynik z powrotem do HEX by w razie błędu łatwiej było go czytać
                ct_hex = bytes(ct_bytes).hex().upper()
                expected_ct_hex = tc["ct"].upper()
                
                self.assertEqual(
                    ct_hex, 
                    expected_ct_hex, 
                    f"Błąd szyfrowania dla wektora {i}. Otrzymano: {ct_hex}"
                )

                # Weryfikacja działania deszyfrowania
                decrypted_pt_bytes = decrypt(ct_bytes, K, S)
                
                decrypted_pt_hex = bytes(decrypted_pt_bytes).hex().upper()
                expected_pt_hex = tc["pt"].upper()
                
                self.assertEqual(
                    decrypted_pt_hex, 
                    expected_pt_hex, 
                    f"Błąd deszyfrowania dla wektora {i}. Otrzymano: {decrypted_pt_hex}"
                )

if __name__ == '__main__':
    unittest.main(verbosity=2)
import os

# ==========================================
#  Tabele i zmienne, wszystko z góry ustalone przez twórców algorytmu
# ==============================-============
mds = [
    [0x01, 0xEF, 0x5B, 0x5B],
    [0x5B, 0xEF, 0xEF, 0x01],
    [0xEF, 0x5B, 0x01, 0xEF],
    [0xEF, 0x01, 0xEF, 0x5B]
]

rs = [
    [0x01, 0xA4, 0x55, 0x87, 0x5A, 0x58, 0xDB, 0x9E],
    [0xA4, 0x56, 0x82, 0xF3, 0x1E, 0xC6, 0x68, 0xE5],
    [0x02, 0xA1, 0xFC, 0xC1, 0x47, 0xAE, 0x3D, 0x19],
    [0xA4, 0x55, 0x87, 0x5A, 0x58, 0xDB, 0x9E, 0x03]
]

#0xFFFFFFFF jest ogólnie po to żeby sie upewnić że liczba jest max 32 bitowa

#przesunieca bitowe w lewo

def rol(number, shift, bitLength=32):
    shift %= bitLength
    return ((number << shift) | (number >> (bitLength - shift))) & 0xFFFFFFFF


#przesuniecie bitowe w prawo
def ror(number, shift, bitLength=32):
    shift %= bitLength
    return ((number >> shift) | (number << (bitLength - shift))) & 0xFFFFFFFF

#przesuniecie o 1 w prawo, dla wartości 4 bitowych, używane tylko do budowania Q
def ror4(x):
    return ((x >> 1) | (x << 3)) & 0xF


#stworzenie Q0 i Q1
def _build_q(t0, t1, t2, t3):
    table = []
    #dla każdej licby 0-256 wykonują sie ustalone operacje matematyczne
    for x in range(256):
        a0 = x >> 4
        b0 = x & 0xF
        a1 = a0 ^ b0
        b1 = (a0 ^ ror4(b0) ^ ((8 * a0) & 0xF)) & 0xF
        a2, b2 = t0[a1], t1[b1]
        a3 = a2 ^ b2
        b3 = (a2 ^ ror4(b2) ^ ((8 * a2) & 0xF)) & 0xF
        a4, b4 = t2[a3], t3[b3]
        table.append((b4 << 4) | a4)
    return table


Q0 = _build_q(
    [0x8, 0x1, 0x7, 0xD, 0x6, 0xF, 0x3, 0x2, 0x0, 0xB, 0x5, 0x9, 0xE, 0xC, 0xA, 0x4],
    [0xE, 0xC, 0xB, 0x8, 0x1, 0x2, 0x3, 0x5, 0xF, 0x4, 0xA, 0x6, 0x7, 0x0, 0x9, 0xD],
    [0xB, 0xA, 0x5, 0xE, 0x6, 0xD, 0x9, 0x0, 0xC, 0x8, 0xF, 0x3, 0x2, 0x4, 0x7, 0x1],
    [0xD, 0x7, 0xF, 0x4, 0x1, 0x2, 0x6, 0xE, 0x9, 0xB, 0x3, 0x0, 0x8, 0x5, 0xC, 0xA]
)

Q1 = _build_q(
    [0x2, 0x8, 0xB, 0xD, 0xF, 0x7, 0x6, 0xE, 0x3, 0x1, 0x9, 0x4, 0x0, 0xA, 0xC, 0x5],
    [0x1, 0xE, 0x2, 0xB, 0x4, 0xC, 0x3, 0x7, 0x6, 0xD, 0xA, 0x5, 0xF, 0x9, 0x0, 0x8],
    [0x4, 0xC, 0x7, 0x5, 0x1, 0x6, 0x9, 0xA, 0x0, 0xE, 0xD, 0x8, 0x2, 0xB, 0x3, 0xF],
    [0xB, 0x9, 0x5, 0x1, 0xC, 0x3, 0xD, 0xE, 0x6, 0x4, 0x7, 0xF, 0x2, 0x0, 0x8, 0xA]
)


#mnożenie w ciele GF(2^8)
#poly jest do xorowania wyniku jak jest za duzy
def gf_mult(a, b, poly):
    res = 0
    while a and b:
        if b & 1: res ^= a
        a <<= 1
        if a & 0x100: a ^= poly
        b >>= 1
    return res


#mnożenie macierzy przez wektor, używane do dyfuzji
def matrix_mult(matrix, vector, poly):
    result = []
    for row in matrix:
        val = 0
        for mat_byte, vec_byte in zip(row, vector):
            val ^= gf_mult(mat_byte, vec_byte, poly)
        result.append(val)
    return result


#funkcja h, używana i do szyfrowania danych i do generacji kluczy
def h(X, L):
    k = len(L)
    y = [(X >> (8 * i)) & 0xFF for i in range(4)]
    l = []
    for i in range(k):
        key_word = L[i]
        word_bytes = []
        
        for j in range(4):
            current_byte = (key_word >> (8 * j)) & 0xFF
            word_bytes.append(current_byte)
            
        l.append(word_bytes)

    if k == 4:
        y[0], y[1], y[2], y[3] = Q1[y[0]] ^ l[3][0], Q0[y[1]] ^ l[3][1], Q0[y[2]] ^ l[3][2], Q1[y[3]] ^ l[3][3]
    if k >= 3:
        y[0], y[1], y[2], y[3] = Q1[y[0]] ^ l[2][0], Q1[y[1]] ^ l[2][1], Q0[y[2]] ^ l[2][2], Q0[y[3]] ^ l[2][3]

    y[0] = Q1[Q0[Q0[y[0]] ^ l[1][0]] ^ l[0][0]]
    y[1] = Q0[Q0[Q1[y[1]] ^ l[1][1]] ^ l[0][1]]
    y[2] = Q1[Q1[Q0[y[2]] ^ l[1][2]] ^ l[0][2]]
    y[3] = Q0[Q1[Q1[y[3]] ^ l[1][3]] ^ l[0][3]]

    z = matrix_mult(mds, y, 0x169)
    return z[0] | (z[1] << 8) | (z[2] << 16) | (z[3] << 24)


# ==========================================
# Główna klasa algorytmu
# ==========================================
class Twofish:
        #inicjalizacja, bierze klucz jako bajty
    def __init__(self, key: bytes):
        """
        Inicjalizacja szyfru.
        Automatycznie dopasowuje i uzupełnia klucz zerami do 16, 24 lub 32 bajtów.
        """
        key_bytes = list(key)
        length = len(key_bytes)

        # integracja logiki dopasowania klucza (padding klucza zerami)
        if length <= 16:
            padded_key = key_bytes + [0] * (16 - length)
        elif length <= 24:
            padded_key = key_bytes + [0] * (24 - length)
        elif length <= 32:
            padded_key = key_bytes + [0] * (32 - length)
        else:
            raise ValueError("Klucz nie może być dłuższy niż 32 bajty (256 bitów).")

        self.K, self.S = self._generate_subkeys(padded_key)


    #generacja podkluczy
    def _generate_subkeys(self, M_bytes):
        k = len(M_bytes) // 8
        #dzielenie klucza na slowa wybranej długości
        #me-parzyste, mo - nieparzyste
        Me, Mo = [], []
        for i in range(k):
            Me.append(
                M_bytes[8 * i] | (M_bytes[8 * i + 1] << 8) | (M_bytes[8 * i + 2] << 16) | (M_bytes[8 * i + 3] << 24))
            Mo.append(M_bytes[8 * i + 4] | (M_bytes[8 * i + 5] << 8) | (M_bytes[8 * i + 6] << 16) | (
                        M_bytes[8 * i + 7] << 24))

        S = []
        for i in range(k):
            m_slice = M_bytes[8 * i: 8 * i + 8]
            r = matrix_mult(rs, m_slice, 0x14D)
            S.append(r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24))
        S = S[::-1]

        K = []
        rho = 0x01010101
        for i in range(20):
            Ai = h((2 * i * rho) % (2 ** 32), Me)
            Bi = rol(h(((2 * i + 1) * rho) % (2 ** 32), Mo), 8)
            K.append((Ai + Bi) % (2 ** 32))
            K.append(rol((Ai + 2 * Bi) % (2 ** 32), 9))

        return K, S

    def _F(self, R0, R1, r):
        #wyznaczenie wartości słów
        T0 = h(R0, self.S)
        T1 = h(rol(R1, 8), self.S)
        F0 = (T0 + T1 + self.K[2 * r + 8]) % (2 ** 32)
        F1 = (T0 + 2 * T1 + self.K[2 * r + 9]) % (2 ** 32)
        return F0, F1

    #szyfrowanie jednego bloku o długości 16 bajtów
    def _encrypt_block(self, plaintext_bytes: bytes) -> bytes:
        P = []
        for i in range(0, 16, 4):
            b0 = plaintext_bytes[i]
            b1 = plaintext_bytes[i + 1]
            b2 = plaintext_bytes[i + 2]
            b3 = plaintext_bytes[i + 3]

            word = b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)
            P.append(word)

        R = []
        for i in range(4):
            xor = P[i] ^ self.K[i]
            R.append(xor)

        for r in range(16):
            F0, F1 = self._F(R[0], R[1], r)
            R_next_0 = ror(R[2] ^ F0, 1)
            R_next_1 = rol(R[3], 1) ^ F1
            R[2], R[3] = R[0], R[1]
            R[0], R[1] = R_next_0, R_next_1

        R[0], R[1], R[2], R[3] = R[2], R[3], R[0], R[1]
        C = [(R[i] ^ self.K[i + 4]) for i in range(4)]

        ciphertext_list = []
        for word in C:
            b0 = word & 0xFF
            b1 = (word >> 8) & 0xFF
            b2 = (word >> 16) & 0xFF
            b3 = (word >> 24) & 0xFF
            
            # Dodajemy je po kolei do naszej listy wynikowej
            ciphertext_list.extend([b0, b1, b2, b3])

        return bytes(ciphertext_list)

    #odszyfrowanie, idzie od tyłu, 2fish symetryczny
    def _decrypt_block(self, ciphertext_bytes: bytes) -> bytes:
        C = []
        for i in range(0, 16, 4):
            b0 = ciphertext_bytes[i]
            b1 = ciphertext_bytes[i + 1]
            b2 = ciphertext_bytes[i + 2]
            b3 = ciphertext_bytes[i + 3]
            
            word = b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)
            C.append(word)

        R = [0] * 4
        R[2] = C[0] ^ self.K[4]
        R[3] = C[1] ^ self.K[5]
        R[0] = C[2] ^ self.K[6]
        R[1] = C[3] ^ self.K[7]

        for r in range(15, -1, -1):
            R_in_0, R_in_1 = R[2], R[3]
            F0, F1 = self._F(R_in_0, R_in_1, r)
            R_in_2 = rol(R[0], 1) ^ F0
            R_in_3 = ror(R[1] ^ F1, 1)
            R[0], R[1], R[2], R[3] = R_in_0, R_in_1, R_in_2, R_in_3

        P = []
        for i in range(4):
            xor = R[i] ^ self.K[i]
            P.append(xor)

        plaintext_list = []
        for word in P:
            b0 = word & 0xFF
            b1 = (word >> 8) & 0xFF
            b2 = (word >> 16) & 0xFF
            b3 = (word >> 24) & 0xFF
            plaintext_list.extend([b0, b1, b2, b3])

        return bytes(plaintext_list)

    # ==========================================
    # Warstwa użytkowa -  padding,  CBC
    # ==========================================
    #padding
    #dopełnia bajty do 16, wypełnia to liczbą oryginalnie brakujących bajtów
    def _pad(self, data: bytes) -> bytes:
        """Dopełnianie PKCS#7 do wielokrotności 16 bajtów."""
        padding_len = 16 - (len(data) % 16)
        return data + bytes([padding_len] * padding_len)

    #odpadowanie, patrzu na ostatnią liczbe zapadowanego słowa i usuwa tyle bajtów ile jest w ostatniej liczbie
    def _unpad(self, data: bytes) -> bytes:
        """Usuwanie dopełnienia PKCS#7."""
        padding_len = data[-1]
        return data[:-padding_len]

    #CBC (cypher block chaining), szyfrowanie tekstu dowolnej dlugości bo CBC jest bezpieczne
    #zmiana szyfrowanego bloku przy użyciu poprzedniego
    def encrypt_cbc(self, plaintext: bytes, iv: bytes) -> bytes:
        """Szyfrowanie danych o DOWOLNEJ długości w bezpiecznym trybie CBC."""
        if len(iv) != 16: raise ValueError("IV musi mieć dokładnie 16 bajtów.")
        padded_data = self._pad(plaintext)
        ciphertext = b''
        prev_block = iv

        for i in range(0, len(padded_data), 16):
            block = padded_data[i:i + 16]
            xored_block = bytes(a ^ b for a, b in zip(block, prev_block))
            encrypted_block = self._encrypt_block(xored_block)
            ciphertext += encrypted_block
            prev_block = encrypted_block

        return ciphertext

    def decrypt_cbc(self, ciphertext: bytes, iv: bytes) -> bytes:
        """Deszyfrowanie danych w trybie CBC i automatyczne usuwanie paddingu."""
        if len(iv) != 16: raise ValueError("IV musi mieć dokładnie 16 bajtów.")
        if len(ciphertext) % 16 != 0: raise ValueError("Szyfrogram musi być wielokrotnością 16 bajtów.")

        padded_plaintext = b''
        prev_block = iv

        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i + 16]
            decrypted_block = self._decrypt_block(block)
            xored_block = bytes(a ^ b for a, b in zip(decrypted_block, prev_block))
            padded_plaintext += xored_block
            prev_block = block

        return self._unpad(padded_plaintext)
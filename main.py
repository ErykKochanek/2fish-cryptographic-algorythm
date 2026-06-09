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

def rol(number, shift, bitLength=32):
    shift %= bitLength
    mask = (1 << bitLength) - 1
    return ((number << shift) | (number >> (bitLength - shift))) & mask

def ror(number, shift, bitLength=32):
    shift %= bitLength
    mask = (1 << bitLength) - 1
    return ((number >> shift) | (number << (bitLength - shift))) & mask

def ror4(x):
    return ((x >> 1) | (x << 3)) & 0xF

def _build_q(t0, t1, t2, t3):
    table = []
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
    [0x8,0x1,0x7,0xD,0x6,0xF,0x3,0x2,0x0,0xB,0x5,0x9,0xE,0xC,0xA,0x4],
    [0xE,0xC,0xB,0x8,0x1,0x2,0x3,0x5,0xF,0x4,0xA,0x6,0x7,0x0,0x9,0xD],
    [0xB,0xA,0x5,0xE,0x6,0xD,0x9,0x0,0xC,0x8,0xF,0x3,0x2,0x4,0x7,0x1],
    [0xD,0x7,0xF,0x4,0x1,0x2,0x6,0xE,0x9,0xB,0x3,0x0,0x8,0x5,0xC,0xA]
)

Q1 = _build_q(
    [0x2,0x8,0xB,0xD,0xF,0x7,0x6,0xE,0x3,0x1,0x9,0x4,0x0,0xA,0xC,0x5],
    [0x1,0xE,0x2,0xB,0x4,0xC,0x3,0x7,0x6,0xD,0xA,0x5,0xF,0x9,0x0,0x8],
    [0x4,0xC,0x7,0x5,0x1,0x6,0x9,0xA,0x0,0xE,0xD,0x8,0x2,0xB,0x3,0xF],
    [0xB,0x9,0x5,0x1,0xC,0x3,0xD,0xE,0x6,0x4,0x7,0xF,0x2,0x0,0x8,0xA]
)

def gf_mult(a, b, poly):
    res = 0
    while a and b:
        if b & 1:
            res ^= a
        a <<= 1
        if a & 0x100:
            a ^= poly
        b >>= 1
    return res

def matrix_mult(matrix, vector, poly):
    result = []
    for row in matrix:
        val = 0
        for mat_byte, vec_byte in zip(row, vector):
            val ^= gf_mult(mat_byte, vec_byte, poly)
        result.append(val)
    return result

def h(X, L):
    k = len(L)
    # Rozdzielenie X na 4 bajty (little-endian)
    y = [(X >> (8 * i)) & 0xFF for i in range(4)]
    
    # Rozdzielenie każdego słowa z L na bajty
    l = [[(L[i] >> (8 * j)) & 0xFF for j in range(4)] for i in range(k)]
    
    if k == 4: # dla klucza 256-bitowego
        y[0] = Q1[y[0]] ^ l[3][0]
        y[1] = Q0[y[1]] ^ l[3][1]
        y[2] = Q0[y[2]] ^ l[3][2]
        y[3] = Q1[y[3]] ^ l[3][3]
    if k >= 3: # dla kluczy 192 i 256-bitowych
        y[0] = Q1[y[0]] ^ l[2][0]
        y[1] = Q1[y[1]] ^ l[2][1]
        y[2] = Q0[y[2]] ^ l[2][2]
        y[3] = Q0[y[3]] ^ l[2][3]
        
    # Zawsze dla klucza >= 128 bitów (k >= 2)
    y[0] = Q1[Q0[Q0[y[0]] ^ l[1][0]] ^ l[0][0]]
    y[1] = Q0[Q0[Q1[y[1]] ^ l[1][1]] ^ l[0][1]]
    y[2] = Q1[Q1[Q0[y[2]] ^ l[1][2]] ^ l[0][2]]
    y[3] = Q0[Q1[Q1[y[3]] ^ l[1][3]] ^ l[0][3]]
    
    # Mnożenie przez macierz MDS używając wielomianu 0x169
    z = matrix_mult(mds, y, 0x169)
    
    # Złożenie z powrotem w 32-bitowe słowo
    return z[0] | (z[1] << 8) | (z[2] << 16) | (z[3] << 24)

def generate_subkeys(M_bytes):
    k = len(M_bytes) // 8
    Me, Mo = [], []
    for i in range(k):
        # Konwersja do słów 32-bitowych (little-endian)
        Me.append(M_bytes[8*i] | (M_bytes[8*i+1]<<8) | (M_bytes[8*i+2]<<16) | (M_bytes[8*i+3]<<24))
        Mo.append(M_bytes[8*i+4] | (M_bytes[8*i+5]<<8) | (M_bytes[8*i+6]<<16) | (M_bytes[8*i+7]<<24))
        
    # Wektor S wyliczany przy użyciu macierzy RS i wielomianu 0x14D
    S = []
    for i in range(k):
        m_slice = M_bytes[8*i : 8*i+8]
        r = matrix_mult(rs, m_slice, 0x14D)
        S.append(r[0] | (r[1]<<8) | (r[2]<<16) | (r[3]<<24))
    S = S[::-1] # Zgodnie z dokumetacją "S lists the words in 'reverse' order"

    K = []
    rho = 0x01010101
    for i in range(20):
        # PHT i wyznaczanie Ai, Bi
        Ai = h((2 * i * rho) % (2**32), Me)
        Bi = rol(h(((2 * i + 1) * rho) % (2**32), Mo), 8)
        K.append((Ai + Bi) % (2**32))
        K.append(rol((Ai + 2 * Bi) % (2**32), 9))
        
    return K, S

def g(X, S):
    # s_i jest formowane z mapowania w funkcji h gdzie lista L jest równa wektorowi S
    return h(X, S)

def F(R0, R1, r, K, S):
    # R1 jest rotowane w lewo o 8 bitów
    T0 = g(R0, S)
    T1 = g(rol(R1, 8), S)
    
    # Łączenie w PHT i dodawanie podkluczy
    F0 = (T0 + T1 + K[2 * r + 8]) % (2**32)
    F1 = (T0 + 2 * T1 + K[2 * r + 9]) % (2**32)
    return F0, F1

def encrypt(plaintext_bytes, K, S):
    # plaintext to 16 bajtów dzielonych na 4 słowa
    P = [sum([plaintext_bytes[4*i + j] << (8*j) for j in range(4)]) for i in range(4)]
    
    R = [0] * 4
    # Input whitening (XOR z pierwszymi podkluczami)
    for i in range(4):
        R[i] = P[i] ^ K[i]
        
    # 16 rund Feistela [cite: 1357, 1415]
    for r in range(16):
        F0, F1 = F(R[0], R[1], r, K, S)
        
        # Rotacja trzeciego słowa w prawo i XOR z F0
        R_next_0 = ror(R[2] ^ F0, 1)
        # Rotacja czwartego słowa w lewo i XOR z F1
        R_next_1 = rol(R[3], 1) ^ F1
        
        # Zamiana połówek miejscami (swap) dla kolejnej rundy
        R[2], R[3] = R[0], R[1]
        R[0], R[1] = R_next_0, R_next_1

    # Odwrócenie swapu z ostatniej rundy
    R[0], R[1], R[2], R[3] = R[2], R[3], R[0], R[1]
    
    # Output whitening
    C = [(R[i] ^ K[i + 4]) for i in range(4)]
    
    # Konwersja na bajty ułożone w little-endian
    ciphertext = []
    for word in C:
        ciphertext.extend([(word >> (8 * j)) & 0xFF for j in range(4)])
        
    return ciphertext

def decrypt(ciphertext_bytes, K, S):
    # ciphertext to 16 bajtów dzielonych na 4 słowa (little-endian)
    C = [sum([ciphertext_bytes[4*i + j] << (8*j) for j in range(4)]) for i in range(4)]
    
    R = [0] * 4
    # Odwrócenie output whitening i odwrócenie ostatniego swapu z szyfrowania
    # W szyfrowaniu ostatnie zamienione wartości R stały się wartościami C
    R[2] = C[0] ^ K[4]
    R[3] = C[1] ^ K[5]
    R[0] = C[2] ^ K[6]
    R[1] = C[3] ^ K[7]
    
    # 16 rund Feistela wstecz (od rundy 15 do 0)
    for r in range(15, -1, -1):
        # W deszyfrowaniu obecne R[2] i R[3] były wejściami do funkcji F
        R_in_0 = R[2]
        R_in_1 = R[3]
        
        # Wyliczenie funkcji F za pomocą tych samych podkluczy
        F0, F1 = F(R_in_0, R_in_1, r, K, S)
        
        # Odwrócenie operacji z końca rundy z szyfrowania
        R_in_2 = rol(R[0], 1) ^ F0
        R_in_3 = ror(R[1] ^ F1, 1)
        
        # Przywrócenie pierwotnego stanu tablicy R na potrzebę kolejnej (wstecznej) rundy
        R[0], R[1], R[2], R[3] = R_in_0, R_in_1, R_in_2, R_in_3
        
    # Odwrócenie input whitening (XOR z pierwszymi podkluczami)
    P = [(R[i] ^ K[i]) for i in range(4)]
    
    # Konwersja z powrotem na bajty w formacie little-endian
    plaintext = []
    for word in P:
        plaintext.extend([(word >> (8 * j)) & 0xFF for j in range(4)])
        
    return plaintext

def prepare_key(key_bytes):
    length = len(key_bytes)
    if length <= 16:
        return key_bytes + [0] * (16 - length)
    elif length <= 24:
        return key_bytes + [0] * (24 - length)
    elif length <= 32:
        return key_bytes + [0] * (32 - length)
    else:
        raise ValueError("Klucz nie może być dłuższy niż 32 bajty (256 bitów).")
    
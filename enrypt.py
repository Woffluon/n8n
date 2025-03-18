from sympy import symbols
import json
import random
import base64

# DNA eşlemesi
DNA_MAP = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}

def polynomial_iteration(seed, degree=3):
    x = symbols('x')
    return [x**i + seed for i in range(degree)]

def lagrange_interpolation(points):
    x = symbols('x')
    n = len(points)
    polynomial = 0
    for i in range(n):
        xi, yi = points[i]
        term = yi
        for j in range(n):
            if i != j:
                xj = points[j][0]
                term *= (x - xj) / (xi - xj)
        polynomial += term
    return polynomial

def to_base_4(value):
    result = ""
    while value > 0:
        result = str(value % 4) + result
        value //= 4
    return result.zfill(4)

def generate_key(open_key):
    seed = sum(ord(char) for char in open_key)
    polynomials = polynomial_iteration(seed)
    points = [(i, p.subs('x', i)) for i, p in enumerate(polynomials)]
    interpolation = lagrange_interpolation(points)
    ascii_values = [ord(char) for char in open_key]
    base_4_values = [to_base_4(value) for value in ascii_values]
    dna_sequence = ''.join(DNA_MAP[int(digit)] for value in base_4_values for digit in value)
    codons = [dna_sequence[i:i+3] for i in range(0, len(dna_sequence), 3)]
    return [sum(ord(char) for char in codon) % 100 for codon in codons]

def generate_iv(length=16):
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=length))

def encrypt(plaintext, key):
    iv = generate_iv(16)
    encrypted = ''.join(chr(ord(char) ^ key[i % len(key)] ^ ord(iv[i % len(iv)])) 
                        for i, char in enumerate(plaintext))
    encrypted_data = f"{iv}{encrypted}"
    return base64.urlsafe_b64encode(encrypted_data.encode()).decode()

# n8n için ana fonksiyon
def main():
    # n8n'den gelen input'u alıyoruz (items[0] genellikle giriş verisini içerir)
    input_data = items[0]['json']
    
    # Girdileri al
    open_key = input_data.get('open_key', '')
    text_to_encrypt = input_data.get('text_to_encrypt', '')
    
    # Şifreleme işlemi
    key = generate_key(open_key)
    encrypted_text = encrypt(text_to_encrypt, key)
    
    # n8n'in beklediği formatta çıktı döndür
    return [{'json': {'encrypted_text': encrypted_text}}]

# n8n Function Node bu değişkeni çalıştırır
items = main()

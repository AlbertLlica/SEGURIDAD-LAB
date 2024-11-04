from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from unidecode import unidecode
import re
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CipherRequest(BaseModel):
    text: str
    key: str = ""
    cipher_type: str
    mode: str  # "encrypt" o "decrypt"

def clean_text(text):
    text = unidecode(text)
    return re.sub(r'[^A-Za-z]', '', text).upper()


# Funciones de cifrado y descifrado
def caesar_cipher(text, shift, mode='encrypt'):
    result = []
    shift = int(shift) if mode == 'encrypt' else -int(shift)
    for char in text:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            result.append(chr((ord(char) - shift_base + shift) % 26 + shift_base))
        else:
            result.append(char)
    return ''.join(result)

def atbash_cipher(text):
    result = []
    for char in text:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            result.append(chr(shift_base + (25 - (ord(char) - shift_base))))
        else:
            result.append(char)
    return ''.join(result)

def playfair_cipher(text, key, mode='encrypt'):
    key = ''.join(sorted(set(key), key=key.index)).replace("J", "I").upper()
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    grid = []
    for char in key + alphabet:
        if char not in grid:
            grid.append(char)

    def create_digraphs(text):
        digraphs = []
        i = 0
        while i < len(text):
            a = text[i].upper()
            i += 1
            b = text[i].upper() if i < len(text) else 'X'
            if a == b:
                b = 'X'
                i -= 1
            digraphs.append((a, b))
            i += 1
        return digraphs

    def find_position(char):
        index = grid.index(char)
        return index // 5, index % 5

    result = []
    digraphs = create_digraphs(text.replace("J", "I").upper())

    for a, b in digraphs:
        row_a, col_a = find_position(a)
        row_b, col_b = find_position(b)

        if row_a == row_b:
            result.append(grid[row_a * 5 + (col_a + (1 if mode == 'encrypt' else -1)) % 5])
            result.append(grid[row_b * 5 + (col_b + (1 if mode == 'encrypt' else -1)) % 5])
        elif col_a == col_b:
            result.append(grid[((row_a + (1 if mode == 'encrypt' else -1)) % 5) * 5 + col_a])
            result.append(grid[((row_b + (1 if mode == 'encrypt' else -1)) % 5) * 5 + col_b])
        else:
            result.append(grid[row_a * 5 + col_b])
            result.append(grid[row_b * 5 + col_a])

    return ''.join(result)

def polybios_cipher(text, mode='encrypt'):
    polybios_square = {
        'A': '11', 'B': '12', 'C': '13', 'D': '14', 'E': '15',
        'F': '21', 'G': '22', 'H': '23', 'I': '24', 'K': '25',
        'L': '31', 'M': '32', 'N': '33', 'O': '34', 'P': '35',
        'Q': '41', 'R': '42', 'S': '43', 'T': '44', 'U': '45',
        'V': '51', 'W': '52', 'X': '53', 'Y': '54', 'Z': '55'
    }
    if mode == 'encrypt':
        return ''.join([polybios_square.get(char.upper(), char) for char in text])
    else:
        reverse_square = {v: k for k, v in polybios_square.items()}
        return ''.join([reverse_square.get(text[i:i + 2], '?') for i in range(0, len(text), 2)])
    

def amsco_cipher(text, key, mode='encrypt'):
    key = [int(digit) for digit in str(key)]

    if mode == 'encrypt':

        bloques = []
        alterna = True
        i = 0

        while i < len(text):
            tamanio = 1 if alterna else 2
            bloques.append(text[i:i+tamanio])
            i += tamanio
            alterna = not alterna

        num_columnas = len(key)
        columnas = [[] for _ in range(num_columnas)]

        for idx, bloque in enumerate(bloques):
            columna = idx % num_columnas
            columnas[columna].append(bloque)

        columnas_ordenadas = [None] * num_columnas
        for idx, pos in enumerate(sorted(range(num_columnas), key=lambda k: key[k] - 1)):
            columnas_ordenadas[idx] = ''.join(columnas[pos])

        # Crear el mensaje cifrado
        return ''.join(columnas_ordenadas)

    elif mode == 'decrypt':
        num_columnas = len(key)
        longitud_columnas = [0] * num_columnas
        i = 0
        alterna = True

        # Calcular la longitud de los bloques
        while i < len(text):
            tamanio = 1 if alterna else 2
            longitud_columnas[i % num_columnas] += tamanio
            i += tamanio
            alterna = not alterna

        # Llenar las columnas con los bloques cifrados
        columnas = []
        pos = 0
        for longitud in sorted(range(num_columnas), key=lambda k: key[k] - 1):
            columnas.append(text[pos:pos + longitud_columnas[longitud]])
            pos += longitud_columnas[longitud]

        # Ordenar las columnas según la clave
        columnas_ordenadas = [None] * num_columnas
        for idx, pos in enumerate(sorted(range(num_columnas), key=lambda k: key[k] - 1)):
            columnas_ordenadas[pos] = columnas[idx]

        # Reconstruir el mensaje descifrado
        mensaje_descifrado = ''
        i = 0
        alterna = True

        while i < len(text):
            for columna in columnas_ordenadas:
                if len(columna) == 0:
                    continue
                tamanio = 1 if alterna else 2
                mensaje_descifrado += columna[:tamanio]
                columnas_ordenadas[columnas_ordenadas.index(columna)] = columna[tamanio:]
                i += tamanio
                alterna = not alterna

        return mensaje_descifrado


def route_cipher(text="", mode='encrypt', step_size=4):

    if mode == 'encrypt':
        idx = 0
        matrix_representation = []
        encrypted_text = ""

        
        for i in range(math.ceil(len(text) / step_size)):
            matrix_row = []
            for j in range(step_size):
                if i * step_size + j < len(text):
                    matrix_row.append(text[i * step_size + j])
                else:
                    matrix_row.append("-")  
            matrix_representation.append(matrix_row)

        matrix_width = len(matrix_representation[0])
        matrix_height = len(matrix_representation)
        allowed_depth = min(matrix_width, matrix_height) // 2

       
        for i in range(allowed_depth):
          
            for j in range(i, matrix_height - i - 1):
                encrypted_text += matrix_representation[j][matrix_width - i - 1]
            for j in range(matrix_width - i - 1, i, -1):
                encrypted_text += matrix_representation[matrix_height - i - 1][j]
            for j in range(matrix_height - i - 1, i, -1):
                encrypted_text += matrix_representation[j][i]
            for j in range(i, matrix_width - i - 1):
                encrypted_text += matrix_representation[i][j]

        return encrypted_text

    elif mode == 'decrypt':
        idx = 0
        plain_text = ""
        matrix_width = step_size
        matrix_height = math.ceil(len(text) / step_size)

        allowed_depth = min(matrix_width, matrix_height) // 2
        plain_text_matrix = [[' ' for _ in range(matrix_width)] for _ in range(matrix_height)]
    
        for i in range(allowed_depth):
                
            for j in range(i, matrix_height - i - 1):
                    plain_text_matrix[j][matrix_width - i - 1] = text[idx]
                    idx += 1
            for j in range(matrix_width - i - 1, i, -1):
                    plain_text_matrix[matrix_height - i - 1][j] = text[idx]
                    idx += 1
            for j in range(matrix_height - i - 1, i, -1):
                    plain_text_matrix[j][i] = text[idx]
                    idx += 1
            for j in range(i, matrix_width - i - 1):
                    plain_text_matrix[i][j] = text[idx]
                    idx += 1

        for i in range(matrix_height):
            for j in range(matrix_width):
                plain_text += plain_text_matrix[i][j]
       
        return plain_text.replace("-", "").strip()
       

@app.post("/cipher/")
async def cipher(request: CipherRequest):
    text = clean_text(request.text)
    key = request.key
    cipher_type = request.cipher_type
    mode = request.mode

    if cipher_type == "caesar":
        return {"result": caesar_cipher(text, key, mode)}
    elif cipher_type == "atbash":
        return {"result": atbash_cipher(text)}
    elif cipher_type == "playfair":
        return {"result": playfair_cipher(text, key, mode)}
    elif cipher_type == "polybius":
        return {"result": polybios_cipher(text, mode)}
    elif cipher_type == "amsco":
        return {"result": amsco_cipher(text, key, mode)}
    elif cipher_type == "route":
        return {"result": route_cipher(text, mode)}
    else:
        raise HTTPException(status_code=400, detail="Invalid cipher type")

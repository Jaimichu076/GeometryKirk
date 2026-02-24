# fix_bosss_math.py
import os
import re

FILES = [f for f in os.listdir('.') if re.match(r'boss\\d+\\.py', f)]
if not FILES:
    print("No se encontraron archivos bossN.py en el directorio actual.")
else:
    for fname in FILES:
        with open(fname, 'r', encoding='utf-8') as f:
            text = f.read()
        new_text = text
        # Reemplazos simples
        new_text = new_text.replace('pygame.math.sin', 'math.sin')
        new_text = new_text.replace('pygame.math.cos', 'math.cos')
        new_text = new_text.replace('pygame.math.tan', 'math.tan')
        # Añadir import math si no existe
        if 'import math' not in new_text:
            # intentar insertar después de otros imports
            new_text = new_text.replace('import pygame', 'import pygame\\nimport math', 1)
        if new_text != text:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(new_text)
            print(f"Corregido: {fname}")
        else:
            print(f"Sin cambios: {fname}")
    print("Parche completado.")

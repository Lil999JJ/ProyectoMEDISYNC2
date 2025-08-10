#!/usr/bin/env python3
"""
Script para estandarizar todos los colores de botones en MEDISYNC
Cambia todos los colores de botones a #0B5394 (azul estándar)
"""

import re

def fix_button_colors():
    """Función para arreglar todos los colores de botones"""
    
    # Leer el archivo
    with open('MEDISYNC.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrones de colores a reemplazar en botones
    color_patterns = [
        r"bg='#16A085'",  # Verde
        r"bg='#E67E22'",  # Naranja
        r"bg='#C0392B'",  # Rojo
        r"bg='#64748B'",  # Gris
        r"bg='#059669'",  # Verde oscuro
        r"bg='#229954'",  # Verde más oscuro
        r'bg="#16A085"',  # Verde con comillas dobles
        r'bg="#E67E22"',  # Naranja con comillas dobles
        r'bg="#C0392B"',  # Rojo con comillas dobles
        r'bg="#64748B"',  # Gris con comillas dobles
        r'bg="#059669"',  # Verde oscuro con comillas dobles
        r'bg="#229954"',  # Verde más oscuro con comillas dobles
    ]
    
    # Reemplazar todos los colores con el azul estándar
    for pattern in color_patterns:
        content = re.sub(pattern, "bg='#0B5394'", content)
    
    # También buscar patrones donde el color está en una variable
    # y reemplazar solo en contexto de botones tk.Button
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        # Si es una línea que contiene tk.Button y tiene bg= con un color diferente al estándar
        if 'tk.Button' in line and 'bg=' in line:
            # Reemplazar cualquier bg='#XXXXXX' que no sea el color estándar
            line = re.sub(r"bg='#[0-9A-Fa-f]{6}'", "bg='#0B5394'", line)
            line = re.sub(r'bg="#[0-9A-Fa-f]{6}"', "bg='#0B5394'", line)
        updated_lines.append(line)
    
    content = '\n'.join(updated_lines)
    
    # Escribir el archivo actualizado
    with open('MEDISYNC.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Todos los colores de botones han sido estandarizados a #0B5394")
    print("🔵 Color azul médico aplicado a todos los botones del sistema")

if __name__ == "__main__":
    fix_button_colors()

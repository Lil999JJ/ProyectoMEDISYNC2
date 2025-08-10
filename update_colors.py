#!/usr/bin/env python3
"""
Script para actualizar la paleta de colores de MEDISYNC
"""

def update_colors():
    with open('MEDISYNC.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Diccionario de colores a reemplazar
    color_map = {
        '#2ecc71': '#059669',  # Verde éxito
        '#27ae60': '#16A085',  # Verde secundario  
        '#e67e22': '#E67E22',  # Naranja
        '#c0392b': '#C0392B',  # Rojo error
        "'#2ecc71'": "'#059669'",
        "'#27ae60'": "'#16A085'",
        "'#e67e22'": "'#E67E22'",
        "'#c0392b'": "'#C0392B'",
        '"#2ecc71"': '"#059669"',
        '"#27ae60"': '"#16A085"',
        '"#e67e22"': '"#E67E22"',
        '"#c0392b"': '"#C0392B"'
    }
    
    # Aplicar reemplazos
    for old_color, new_color in color_map.items():
        content = content.replace(old_color, new_color)
    
    # Guardar archivo actualizado
    with open('MEDISYNC.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Paleta de colores actualizada completamente")
    
    # Mostrar resumen de la nueva paleta
    print("\n🎨 Nueva Paleta de Colores MEDISYNC:")
    print("=" * 50)
    print("PRIMARIOS:")
    print("  • #0B5394 - Azul médico principal")
    print("  • #FFFFFF - Blanco puro") 
    print("  • #1E3A8A - Azul oscuro (headers)")
    print("\nSECUNDARIOS:")
    print("  • #16A085 - Verde médico (confirmaciones)")
    print("  • #E67E22 - Naranja médico (advertencias)")
    print("  • #C0392B - Rojo médico (errores)")
    print("\nNEUTROS:")
    print("  • #F8FAFC - Fondo claro")
    print("  • #E2E8F0 - Fondo medio")
    print("  • #CBD5E1 - Bordes/separadores")
    print("  • #64748B - Texto secundario")
    print("  • #1E293B - Texto principal")
    print("\nESTADOS:")
    print("  • #059669 - Verde estado activo")
    print("  • #DC2626 - Rojo estado inactivo")
    print("  • #F59E0B - Amarillo pendiente")

if __name__ == "__main__":
    update_colors()

#!/usr/bin/env python3
"""
RUN_MEDISYNC - Launcher para el Sistema MEDISYNC
Verificación de dependencias y ejecución del sistema
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Verificar versión de Python"""
    print("🐍 Verificando versión de Python...")
    if sys.version_info < (3, 7):
        print("❌ Se requiere Python 3.7 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Verificar dependencias del proyecto"""
    print("\n📦 Verificando dependencias...")
    
    required_modules = {
        'tkinter': 'Interfaz gráfica (incluido con Python)',
        'sqlite3': 'Base de datos (incluido con Python)',
        'hashlib': 'Seguridad (incluido con Python)',
        'datetime': 'Fechas y tiempo (incluido con Python)',
        'dataclasses': 'Estructuras de datos (incluido con Python)',
        'typing': 'Tipos de datos (incluido con Python)',
        'json': 'Manejo de JSON (incluido con Python)',
        'os': 'Sistema operativo (incluido con Python)',
        'subprocess': 'Procesos (incluido con Python)'
    }
    
    optional_modules = {
        'tkcalendar': 'Calendario avanzado - pip install tkcalendar',
        'reportlab': 'Generación de PDFs - pip install reportlab',
        'pillow': 'Procesamiento de imágenes - pip install pillow'
    }
    
    missing_required = []
    
    # Verificar módulos requeridos
    for module, description in required_modules.items():
        try:
            importlib.import_module(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"❌ {module}: {description}")
            missing_required.append(module)
    
    # Verificar módulos opcionales
    print("\n📦 Módulos opcionales:")
    for module, description in optional_modules.items():
        try:
            importlib.import_module(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"⚠️  {module}: {description}")
    
    return len(missing_required) == 0

def check_project_files():
    """Verificar archivos del proyecto"""
    print("\n📁 Verificando archivos del proyecto...")
    
    required_files = [
        'MEDISYNC.py',
        'simple_database_manager.py',
        'database_manager.py',
        'patient_registration_form.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    # Verificar directorio de base de datos
    if os.path.exists('database'):
        print("✅ Directorio database/")
    else:
        print("⚠️  Directorio database/ (se creará automáticamente)")
        
    # Verificar archivos de configuración
    optional_files = [
        'requirements.txt',
        'README.md',
        'pyproject.toml',
        'pytest.ini'
    ]
    
    print("\n📄 Archivos de configuración:")
    for file in optional_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"⚠️  {file}")
    
    return len(missing_files) == 0

def create_database_directory():
    """Crear directorio de base de datos si no existe"""
    if not os.path.exists('database'):
        os.makedirs('database')
        print("✅ Directorio database/ creado")

def run_medisync():
    """Ejecutar MEDISYNC"""
    print("\n🚀 Iniciando MEDISYNC...")
    print("=" * 50)
    
    try:
        # Cambiar al directorio del script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Importar y ejecutar MEDISYNC
        from MEDISYNC import MedisyncApp
        app = MedisyncApp()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("   Verifique que todos los archivos estén presentes")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    return True

def install_dependencies():
    """Instalar dependencias opcionales"""
    print("\n📦 ¿Desea instalar las dependencias opcionales? (y/n): ", end="")
    
    try:
        response = input().lower().strip()
        if response in ['y', 'yes', 's', 'si']:
            print("\n📦 Instalando dependencias opcionales...")
            
            optional_packages = ['tkcalendar', 'reportlab', 'pillow']
            
            for package in optional_packages:
                try:
                    print(f"Instalando {package}...")
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    print(f"✅ {package} instalado")
                except subprocess.CalledProcessError:
                    print(f"❌ Error instalando {package}")
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            print("✅ Instalación de dependencias completada")
        else:
            print("⏭️  Saltando instalación de dependencias opcionales")
    except KeyboardInterrupt:
        print("\n⏹️  Operación cancelada por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🏥 MEDISYNC - Sistema Integral de Gestión Médica")
    print("=" * 50)
    print("🔧 Verificando sistema...")
    
    # Verificar Python
    if not check_python_version():
        print("\n❌ Error crítico: Versión de Python incompatible")
        print("   Instale Python 3.7 o superior y vuelva a intentar")
        input("\nPresione Enter para salir...")
        return
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ Error crítico: Dependencias faltantes")
        print("   Instale Python correctamente y vuelva a intentar")
        input("\nPresione Enter para salir...")
        return
    
    # Verificar archivos del proyecto
    if not check_project_files():
        print("\n❌ Error crítico: Archivos del proyecto faltantes")
        print("   Verifique que todos los archivos estén presentes")
        input("\nPresione Enter para salir...")
        return
    
    # Crear directorio de base de datos
    create_database_directory()
    
    # Ofrecer instalación de dependencias opcionales
    install_dependencies()
    
    print("\n✅ Verificación completada exitosamente")
    print("🚀 Iniciando MEDISYNC...")
    print("=" * 50)
    
    # Ejecutar MEDISYNC
    try:
        run_medisync()
    except KeyboardInterrupt:
        print("\n⏹️  MEDISYNC cerrado por el usuario")
    except Exception as e:
        print(f"\n❌ Error ejecutando MEDISYNC: {e}")
        print("   Contacte al soporte técnico")
    finally:
        print("\n👋 ¡Gracias por usar MEDISYNC!")
        input("Presione Enter para salir...")

if __name__ == "__main__":
    main()
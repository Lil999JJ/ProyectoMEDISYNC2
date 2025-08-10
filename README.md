# 🏥 MEDISYNC - Sistema Integral de Gestión Médica

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green.svg)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com)

## 📋 Descripción

**MEDISYNC** es un sistema integral de gestión médica desarrollado en Python con interfaz gráfica Tkinter. Diseñado para consultorios médicos, clínicas y hospitales pequeños, proporciona una solución completa para la administración de pacientes, citas, historiales médicos y facturación.

## ✨ Características Principales

### 🔐 Sistema de Autenticación
- Login seguro con diferentes roles de usuario
- Gestión de permisos por tipo de usuario
- Encriptación de contraseñas con SHA256

### 👥 Gestión de Usuarios
- **Administradores**: Control total del sistema
- **Doctores**: Gestión de citas y historiales médicos
- **Secretarias**: Administración de citas y facturación
- **Pacientes**: Acceso a información personal y citas

### 🤒 Gestión de Pacientes
- Registro completo de pacientes
- Información médica detallada
- Gestión de seguros médicos
- Contactos de emergencia
- Números de expediente únicos

### 👨‍⚕️ Gestión de Doctores
- Perfiles médicos completos
- Especialidades y cédulas profesionales
- Horarios de atención
- Tarifas de consulta
- Aceptación de seguros médicos

### 📅 Sistema de Citas
- Programación de citas médicas
- Gestión de horarios
- Estados de citas (programada, completada, cancelada)
- Búsqueda y filtrado avanzado

### 💰 Sistema de Facturación
- Generación automática de facturas
- Gestión de pagos y métodos de pago
- Aplicación de descuentos por seguros médicos
- Control de facturas pendientes
- Reportes de ingresos

### 📊 Reportes y Estadísticas
- Dashboard con estadísticas en tiempo real
- Reportes de ingresos mensuales
- Estadísticas de usuarios y citas
- Exportación a PDF (opcional)

## 🚀 Instalación y Configuración

### Requisitos del Sistema

- **Python 3.7 o superior**
- **Sistema Operativo**: Windows, Linux, o macOS
- **RAM**: Mínimo 4GB recomendado
- **Espacio en disco**: 100MB mínimo

### Instalación Rápida

1. **Clonar o descargar el proyecto**:
   ```bash
   git clone https://github.com/tu-usuario/medisync.git
   cd medisync
   ```

2. **Ejecutar el launcher**:
   ```bash
   python RUN_MEDISYNC.py
   ```

3. **El launcher verificará automáticamente**:
   - Versión de Python
   - Dependencias requeridas
   - Archivos del proyecto
   - Creará la base de datos si es necesario

### Instalación Manual

1. **Instalar dependencias opcionales**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar directamente**:
   ```bash
   python MEDISYNC.py
   ```

## 👤 Usuarios de Prueba

El sistema incluye usuarios predefinidos para pruebas:

| Rol | Email | Contraseña | Descripción |
|-----|-------|------------|-------------|
| 🛡️ **Administrador** | `admin@medisync.com` | `admin123` | Acceso completo al sistema |
| 👨‍⚕️ **Doctor** | `carlos@medisync.com` | `doctor123` | Gestión de citas y historiales |
| 👩‍💼 **Secretaria** | `maria@medisync.com` | `secretaria123` | Administración de citas |
| 🤒 **Paciente** | `pedro@medisync.com` | `paciente123` | Acceso a información personal |

## 📁 Estructura del Proyecto

```
ProyectoMEDISYNC/
├── 📄 MEDISYNC.py                    # Aplicación principal
├── 📄 simple_database_manager.py    # Gestor de base de datos simplificado
├── 📄 database_manager.py           # Gestor de base de datos completo
├── 📄 patient_registration_form.py  # Formulario de registro de pacientes
├── 📄 RUN_MEDISYNC.py              # Launcher del sistema
├── 📄 reset_passwords.py           # Utilidad para resetear contraseñas
├── 📄 requirements.txt             # Dependencias del proyecto
├── 📄 README.md                    # Documentación
├── 📄 pyproject.toml              # Configuración del proyecto
├── 📄 pytest.ini                  # Configuración de tests
├── 📁 database/                   # Base de datos SQLite
│   └── 📄 medisync.db
├── 📁 facturas_pdf/              # PDFs de facturas generadas
├── 📁 __pycache__/               # Cache de Python
└── 📁 .venv/                     # Entorno virtual (opcional)
```

## 🖥️ Capturas de Pantalla

### Login del Sistema
![Login](docs/screenshots/login.png)

### Dashboard Principal
![Dashboard](docs/screenshots/dashboard.png)

### Gestión de Usuarios
![Usuarios](docs/screenshots/usuarios.png)

### Sistema de Citas
![Citas](docs/screenshots/citas.png)

## ⚙️ Configuración Avanzada

### Base de Datos

El sistema utiliza **SQLite** por defecto, almacenado en `database/medisync.db`. La base de datos se crea automáticamente al primer uso.

### Seguros Médicos

El sistema incluye seguros médicos predefinidos:
- **ARS Senasa** (15% descuento)
- **ARS Humano** (20% descuento)
- **Universal** (10% descuento)
- **Sin Seguro** (0% descuento)

### Personalización

- **Tarifas**: Configurables por doctor
- **Horarios**: Personalizables por médico
- **Seguros**: Añadir nuevos seguros desde la base de datos
- **Temas**: Interfaz personalizable

## 🔧 Solución de Problemas

### Problema: "ModuleNotFoundError"
**Solución**: Ejecutar `python RUN_MEDISYNC.py` para verificar dependencias

### Problema: Error de base de datos
**Solución**: Eliminar `database/medisync.db` y reiniciar la aplicación

### Problema: Interfaz no responde
**Solución**: Verificar que tkinter esté instalado correctamente

### Problema: No se pueden generar PDFs
**Solución**: Instalar reportlab: `pip install reportlab`

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama para nueva característica (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

- **Documentación**: [Wiki del proyecto](https://github.com/tu-usuario/medisync/wiki)
- **Issues**: [Reportar problemas](https://github.com/tu-usuario/medisync/issues)
- **Discusiones**: [Foro de la comunidad](https://github.com/tu-usuario/medisync/discussions)

## 🏆 Reconocimientos

- Desarrollado con ❤️ para la comunidad médica
- Interfaz construida con Python Tkinter
- Base de datos SQLite para simplicidad y portabilidad
- Iconos y diseño inspirados en Material Design

## 📈 Roadmap

### Version 2.1 (Próxima)
- [ ] Integración con APIs de seguros médicos
- [ ] Notificaciones por email
- [ ] Respaldo automático en la nube
- [ ] Aplicación móvil companion

### Version 2.2 (Futuro)
- [ ] Integración con equipos médicos
- [ ] Análisis predictivo
- [ ] Telemedicina básica
- [ ] Multi-idioma

---

**© 2025 MEDISYNC - Sistema Integral de Gestión Médica**

*Hecho con ❤️ para mejorar la atención médica*
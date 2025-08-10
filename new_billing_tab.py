    def create_billing_tab(self, parent):
        """Sistema de Facturación Completo Integrado - REEMPLAZADO CON SISTEMA COMPLETO"""
        # Importar y usar sistema completo
        try:
            # Crear frame principal
            main_frame = tk.Frame(parent, bg='#f8f9fa')
            main_frame.pack(fill='both', expand=True)
            
            # Header ultra moderno
            header_frame = tk.Frame(main_frame, bg='#1a252f', height=120)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            # Contenido del header
            header_content = tk.Frame(header_frame, bg='#1a252f')
            header_content.pack(expand=True, fill='both', padx=30, pady=20)
            
            # Título
            title_row = tk.Frame(header_content, bg='#1a252f')
            title_row.pack(anchor='w')
            
            tk.Label(title_row, text="💰", font=('Arial', 28), bg='#1a252f', fg='#f39c12').pack(side='left')
            tk.Label(title_row, text="SISTEMA DE FACTURACIÓN COMPLETO", 
                    font=('Arial', 20, 'bold'), bg='#1a252f', fg='white').pack(side='left', padx=(15, 0))
            
            subtitle_row = tk.Frame(header_content, bg='#1a252f')
            subtitle_row.pack(anchor='w', pady=(8, 0))
            
            tk.Label(subtitle_row, text="🧾 PDFs Automáticos | 💳 Pagos Completos | 📊 Reportes Avanzados | 🏥 Sistema Integrado", 
                    font=('Arial', 13), bg='#1a252f', fg='#bdc3c7').pack(side='left')
            
            # Botones de acción principales
            right_header = tk.Frame(header_content, bg='#1a252f')
            right_header.pack(side='right')
            
            # Botón Sistema Completo Integrado
            system_btn = tk.Button(
                right_header,
                text="🚀 SISTEMA COMPLETO INTEGRADO",
                command=self.open_integrated_billing_system,
                bg='#27ae60',
                fg='white',
                font=('Arial', 16, 'bold'),
                padx=30,
                pady=15,
                relief='flat',
                cursor='hand2'
            )
            system_btn.pack(pady=(0, 10))
            
            # Mensaje de reemplazo exitoso
            success_frame = tk.Frame(main_frame, bg='#d4edda')
            success_frame.pack(fill='x', padx=20, pady=20)
            
            tk.Label(success_frame, 
                    text="✅ SISTEMA BÁSICO ELIMINADO Y REEMPLAZADO CON SISTEMA COMPLETO",
                    font=('Arial', 16, 'bold'), bg='#d4edda', fg='#155724').pack(pady=20)
            
            tk.Label(success_frame, 
                    text="🎯 Haga clic en 'SISTEMA COMPLETO INTEGRADO' para acceder a todas las funcionalidades avanzadas",
                    font=('Arial', 12), bg='#d4edda', fg='#155724').pack(pady=(0, 20))
            
            # Panel de características
            features_frame = tk.LabelFrame(main_frame, text="🚀 CARACTERÍSTICAS DEL SISTEMA COMPLETO", 
                                         font=('Arial', 14, 'bold'), bg='#f8f9fa', fg='#2c3e50',
                                         padx=20, pady=20)
            features_frame.pack(fill='x', padx=20, pady=20)
            
            features_text = """
🧾 FACTURACIÓN AVANZADA:
   • Generación automática de PDFs profesionales
   • Numeración automática de facturas
   • Integración con citas médicas
   
💳 SISTEMA DE PAGOS COMPLETO:
   • Cálculo automático de cambio/faltante
   • Múltiples métodos de pago
   • Control de descuentos por seguro
   
📊 REPORTES Y ANÁLISIS:
   • Reportes financieros automáticos  
   • Estadísticas en tiempo real
   • Exportación a PDF

🏥 GESTIÓN MÉDICA INTEGRADA:
   • Servicios médicos catalogados
   • Integración con expedientes
   • Control de inventario básico
            """
            
            tk.Label(features_frame, text=features_text, font=('Arial', 11), 
                    justify='left', bg='#f8f9fa', fg='#2c3e50').pack(anchor='w')
            
        except Exception as e:
            # Fallback si hay error
            messagebox.showerror("Error", f"Error cargando sistema completo: {str(e)}")
            
            # Crear interfaz básica de error
            error_frame = tk.Frame(parent, bg='#f8d7da')
            error_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            tk.Label(error_frame, text="❌ ERROR CARGANDO SISTEMA COMPLETO", 
                    font=('Arial', 16, 'bold'), bg='#f8d7da', fg='#721c24').pack(pady=20)
    
    def open_integrated_billing_system(self):
        """Abrir sistema completo de facturación integrado"""
        try:
            # Instalar dependencias primero
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "qrcode[pil]", "pillow"])
            
            # Crear ventana del sistema completo
            billing_window = tk.Toplevel(self.root)
            billing_window.title("🏥 MEDISYNC - SISTEMA DE FACTURACIÓN COMPLETO")
            billing_window.geometry("1600x1000")
            billing_window.configure(bg='#f8f9fa')
            
            # Maximizar ventana
            try:
                billing_window.state('zoomed')  # Windows
            except:
                billing_window.attributes('-zoomed', True)  # Linux
            
            # Ejecutar el sistema completo
            command = f'python "{self.get_project_path()}/billing_system_final.py"'
            subprocess.Popen(command, shell=True)
            
            # Cerrar ventana placeholder
            billing_window.destroy()
            
            messagebox.showinfo("Sistema Completo", 
                              "✅ Sistema de Facturación Completo iniciado!\n\n" +
                              "🧾 Todas las funciones avanzadas están disponibles:\n" +
                              "• PDFs automáticos\n• Pagos completos\n• Reportes avanzados\n• Gestión integral")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando sistema completo:\n{str(e)}")
            print(f"Error detallado: {e}")
    
    def get_project_path(self):
        """Obtener ruta del proyecto"""
        import os
        return os.path.dirname(os.path.abspath(__file__))

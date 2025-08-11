"""
MEDISYNC UI Theme
Unifica colores, fuentes y estilos ttk según estándares.
"""
from tkinter import ttk

THEME = {
    'primary': '#0B5394',
    'background': '#F8FAFC',
    'surface': '#FFFFFF',
    'text_primary': '#1E293B',
    'text_secondary': '#64748B',
    'border': '#CBD5E1',
    'header_text_on_primary': '#FFFFFF',
}


def _lighten(hex_color: str, factor: float = 0.15) -> str:
    """Aclarar color HEX en porcentaje factor (0-1)."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f"#{r:02X}{g:02X}{b:02X}"


def apply_theme(root=None):
    """Aplicar estilos modernos ttk: Notebook, Buttons, Treeview."""
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass

    primary = THEME['primary']
    primary_hover = _lighten(primary, 0.12)

    # Notebook
    style.configure('TNotebook', background=THEME['background'], borderwidth=0)
    style.configure(
        'TNotebook.Tab',
        padding=(12, 8),
        background=THEME['surface'],
        foreground=THEME['text_primary'],
        font=('Arial', 10, 'bold')
    )
    style.map(
        'TNotebook.Tab',
        background=[('selected', primary)],
        foreground=[('selected', THEME['header_text_on_primary'])]
    )

    # Primary button style for ttk
    style.configure(
        'Primary.TButton',
        background=primary,
        foreground='#FFFFFF',
        font=('Arial', 10, 'bold'),
        padding=(12, 6),
        borderwidth=0,
        focusthickness=0
    )
    style.map('Primary.TButton', background=[('active', primary_hover)])

    # Treeview
    style.configure(
        'Treeview',
        background=THEME['surface'],
        fieldbackground=THEME['surface'],
        foreground=THEME['text_primary'],
        rowheight=26,
        bordercolor=THEME['border'],
        borderwidth=1
    )
    style.configure(
        'Treeview.Heading',
        background=_lighten(primary, 0.75),
        foreground=THEME['text_primary'],
        font=('Arial', 10, 'bold')
    )
    style.map('Treeview.Heading', background=[('active', _lighten(primary, 0.65))])

    return style

# Modüllere özel soft pastel renk paletleri
TEMALAR = {
    "mavi":    {"ana": "#2B6CB0", "acik": "#EBF8FF", "hover": "#90CDF4", "kenar": "#BEE3F8"},
    "turuncu": {"ana": "#C05621", "acik": "#FFFAF0", "hover": "#FBD38D", "kenar": "#FEEBC8"},
    "mor":     {"ana": "#553C9A", "acik": "#FAF5FF", "hover": "#D6BCFA", "kenar": "#E9D8FD"},
    "kirmizi": {"ana": "#C53030", "acik": "#FFF5F5", "hover": "#FEB2B2", "kenar": "#FED7D7"},
    "turkuaz": {"ana": "#234E52", "acik": "#E6FFFA", "hover": "#81E6D9", "kenar": "#B2F5EA"},
    "yesil":   {"ana": "#276749", "acik": "#F0FAF4", "hover": "#9AE6B4", "kenar": "#C6F6D5"}
}

def get_stil(tema):
    ana = tema["ana"]
    acik = tema["acik"]
    hover = tema["hover"]
    kenar = tema["kenar"]

    return f"""
    QMainWindow, QDialog {{
        background-color: {acik};
        color: #1C3A2A;
        font-family: 'Segoe UI', sans-serif;
    }}

    QGroupBox {{
        background-color: #FFFFFF;
        border: 1px solid {kenar};
        border-radius: 12px;
        margin-top: 18px;
        font-weight: bold;
        color: {ana};
        padding: 12px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 8px;
        color: {ana};
    }}

    /* Genel buton */
    QPushButton {{
        background-color: #FFFFFF;
        color: {ana};
        border-radius: 9px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 12px;
        border: 1px solid {kenar};
    }}
    QPushButton:hover {{
        background-color: {acik};
        border: 1.5px solid {ana};
    }}

    /* İŞLEVE ÖZEL BUTONLAR (Renkleri Sabit Bırakıldı) */
    QPushButton#onay_btn {{ background-color: #C6F6D5; color: #22543D; border: 1px solid #68D391; }}
    QPushButton#onay_btn:hover {{ background-color: #9AE6B4; border: 1px solid #38A169; }}

    QPushButton#red_btn {{ background-color: #FFF5F5; color: #9B2C2C; border: 1px solid #FEB2B2; }}
    QPushButton#red_btn:hover {{ background-color: #FED7D7; border: 1px solid #FC8181; }}

    QPushButton#primary_btn {{ background-color: #276749; color: #FFFFFF; border: 1px solid #276749; }}
    QPushButton#primary_btn:hover {{ background-color: #22543D; border: 1px solid #22543D; }}

    QPushButton#warn_btn {{ background-color: #FEFCBF; color: #744210; border: 1px solid #F6E05E; }}
    QPushButton#warn_btn:hover {{ background-color: #FAF089; border: 1px solid #ECC94B; }}

    QLineEdit, QComboBox, QSpinBox, QDateEdit, QTextEdit {{
        background-color: #FFFFFF;
        border: 1.5px solid {kenar};
        border-radius: 7px;
        padding: 7px 10px;
        color: #1C3A2A;
        font-size: 12px;
        selection-background-color: {hover};
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
    QDateEdit:focus, QTextEdit:focus {{
        border: 1.5px solid {ana};
    }}
    QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {{
        background-color: {acik};
        color: #A0AEC0;
    }}
    
    QComboBox::drop-down {{ border: none; width: 30px; }}
    QComboBox QAbstractItemView {{
        border: 1px solid {kenar};
        selection-background-color: {acik};
        selection-color: #1A202C;
        background-color: white;
        border-radius: 4px;
    }}

    QTableWidget, QTreeWidget, QListWidget {{
        background-color: #FFFFFF;
        alternate-background-color: {acik};
        border: 1px solid {kenar};
        gridline-color: {acik};
        border-radius: 8px;
        color: #1C3A2A;
        font-size: 12px;
    }}
    QHeaderView::section {{
        background-color: {kenar};
        color: {ana};
        padding: 8px;
        border: none;
        font-weight: bold;
        font-size: 12px;
    }}
    QTableWidget::item:selected, QTreeWidget::item:selected,
    QListWidget::item:selected {{
        background-color: {hover};
        color: #1C3A2A;
    }}

    QTabWidget::pane {{
        border: 1px solid {kenar};
        background: #FFFFFF;
        border-radius: 6px;
    }}
    QTabBar::tab {{
        background: {acik};
        color: {ana};
        padding: 8px 18px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-size: 12px;
    }}
    QTabBar::tab:selected {{
        background: #FFFFFF;
        color: {ana};
        font-weight: bold;
        border: 1px solid {kenar};
        border-bottom: none;
    }}

    QScrollBar:vertical {{
        background: {acik};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {hover};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """
STIL_KODU = """
    QMainWindow, QDialog, QWidget {
        background-color: #F7FAFC;
        color: #2D3748;
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    }
    QGroupBox {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        margin-top: 15px;
        font-size: 14px;
        font-weight: bold;
        color: #2C5282;
        padding: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: #2B6CB0;
    }
    QPushButton {
        background-color: #FFFFFF;
        color: #2C5282;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 13px;
        border: 1px solid #BEE3F8;
    }
    QPushButton:hover { background-color: #EBF8FF; border-color: #90CDF4; }
    QPushButton:pressed { background-color: #BEE3F8; }
    QPushButton#primary_btn { background-color: #3182CE; color: white; border: none; }
    QPushButton#primary_btn:hover { background-color: #2B6CB0; }
    QPushButton#onay_btn { background-color: #F0FFF4; color: #276749; border: 1px solid #C6F6D5; }
    QPushButton#onay_btn:hover { background-color: #C6F6D5; border-color: #9AE6B4; }
    QPushButton#red_btn { background-color: #FFF5F5; color: #C53030; border: 1px solid #FEB2B2; }
    QPushButton#red_btn:hover { background-color: #FED7D7; border-color: #FC8181; }
    QLineEdit, QComboBox, QSpinBox, QDateEdit, QTextEdit {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E0;
        border-radius: 6px;
        padding: 8px;
        color: #2D3748;
        font-size: 13px;
        selection-background-color: #BEE3F8;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
        border: 2px solid #63B3ED;
        background-color: #F7FAFC;
    }
    QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {
        background-color: #EDF2F7;
        color: #A0AEC0;
        border: 1px solid #E2E8F0;
    }
    QComboBox::drop-down { border: none; width: 30px; }
    QComboBox QAbstractItemView {
        border: 1px solid #CBD5E0;
        selection-background-color: #EBF8FF;
        selection-color: #2D3748;
        background-color: white;
        border-radius: 4px;
    }
    QTableWidget, QTreeWidget, QListWidget {
        background-color: #FFFFFF;
        alternate-background-color: #F7FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        color: #2D3748;
        font-size: 13px;
        gridline-color: #EDF2F7;
        outline: none;
    }
    QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
        background-color: #EBF8FF;
        color: #2B6CB0;
        font-weight: bold;
    }
    QHeaderView::section {
        background-color: #EDF2F7;
        color: #4A5568;
        padding: 8px;
        border: none;
        border-bottom: 2px solid #CBD5E0;
        font-weight: bold;
        font-size: 13px;
    }
    QScrollBar:vertical { border: none; background: #F7FAFC; width: 8px; border-radius: 4px; margin: 0px; }
    QScrollBar::handle:vertical { background: #CBD5E0; min-height: 20px; border-radius: 4px; }
    QScrollBar::handle:vertical:hover { background: #A0AEC0; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
    QScrollBar:horizontal { border: none; background: #F7FAFC; height: 8px; border-radius: 4px; margin: 0px; }
    QScrollBar::handle:horizontal { background: #CBD5E0; min-width: 20px; border-radius: 4px; }
    QScrollBar::handle:horizontal:hover { background: #A0AEC0; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }
"""
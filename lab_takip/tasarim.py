STIL_KODU = """
    QMainWindow, QDialog, QWidget {
        background-color: #F4FAF6;
        color: #1A2E22;
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    }
    QGroupBox {
        background-color: #FFFFFF;
        border: 1px solid #C3E6CB;
        border-radius: 10px;
        margin-top: 18px;
        font-size: 13px;
        font-weight: bold;
        color: #276749;
        padding: 12px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 6px;
        color: #276749;
    }
    QPushButton {
        background-color: #FFFFFF;
        color: #276749;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 13px;
        border: 2px solid #9AE6B4;
    }
    QPushButton:hover { background-color: #F0FFF4; border-color: #68D391; }
    QPushButton:pressed { background-color: #C6F6D5; }

    QPushButton#primary_btn { background-color: #38A169; color: white; border: none; }
    QPushButton#primary_btn:hover { background-color: #2F855A; }

    QPushButton#onay_btn { background-color: #EBF8FF; color: #2B6CB0; border: 2px solid #90CDF4; }
    QPushButton#onay_btn:hover { background-color: #BEE3F8; border-color: #63B3ED; }

    QPushButton#red_btn { background-color: #FFF5F5; color: #C53030; border: 2px solid #FEB2B2; }
    QPushButton#red_btn:hover { background-color: #FED7D7; border-color: #FC8181; }

    QLineEdit, QComboBox, QSpinBox, QDateEdit, QTextEdit {
        background-color: #FFFFFF;
        border: 1.5px solid #9AE6B4;
        border-radius: 6px;
        padding: 7px;
        color: #1A2E22;
        font-size: 13px;
        selection-background-color: #9AE6B4;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {
        border: 2px solid #38A169;
        background-color: #F0FFF4;
    }
    QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {
        background-color: #EDF2F7;
        color: #A0AEC0;
        border: 1px solid #C3E6CB;
    }
    QComboBox::drop-down { border: none; width: 28px; }
    QComboBox QAbstractItemView {
        border: 1px solid #9AE6B4;
        selection-background-color: #C6F6D5;
        selection-color: #1A2E22;
        background-color: white;
        border-radius: 4px;
    }
    QTableWidget, QTreeWidget, QListWidget {
        background-color: #FFFFFF;
        alternate-background-color: #F4FAF6;
        border: 1px solid #C3E6CB;
        border-radius: 8px;
        color: #1A2E22;
        font-size: 13px;
        gridline-color: #E2F0E6;
        outline: none;
    }
    QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
        background-color: #C6F6D5;
        color: #1A2E22;
    }
    QHeaderView::section {
        background-color: #F0FFF4;
        color: #276749;
        padding: 8px;
        border: none;
        border-bottom: 2px solid #9AE6B4;
        font-weight: bold;
        font-size: 13px;
    }
    QScrollBar:vertical { border:none; background:#F4FAF6; width:8px; border-radius:4px; margin:0; }
    QScrollBar::handle:vertical { background:#9AE6B4; min-height:20px; border-radius:4px; }
    QScrollBar::handle:vertical:hover { background:#68D391; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border:none; background:none; }
    QScrollBar:horizontal { border:none; background:#F4FAF6; height:8px; border-radius:4px; margin:0; }
    QScrollBar::handle:horizontal { background:#9AE6B4; min-width:20px; border-radius:4px; }
    QScrollBar::handle:horizontal:hover { background:#68D391; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border:none; background:none; }
"""
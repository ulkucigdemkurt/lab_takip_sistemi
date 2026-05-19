
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem

def tablo_doldur(tablo, veriler, sutunlar):
    tablo.setSortingEnabled(False); tablo.setRowCount(len(veriler))
    for r, veri in enumerate(veriler):
        v = dict(veri)
        for c, s in enumerate(sutunlar):
            d = v.get(s); item = QTableWidgetItem()
            item.setData(Qt.EditRole, d if isinstance(d, (int, float)) else ("" if d is None else str(d)))
            item.setTextAlignment(Qt.AlignCenter); tablo.setItem(r, c, item)
    tablo.setSortingEnabled(True)

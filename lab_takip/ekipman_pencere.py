
import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QLabel,
    QPushButton, QLineEdit, QComboBox, QSpinBox, QTableWidget, QHeaderView,
    QMessageBox
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
from tasarim import STIL_KODU
from yardimcilar import tablo_doldur

class EkipmanPencere(QDialog):
    KATS = ["Sarf Malzeme","Mikrodenetleyici","Demirbaş Cihaz","El Aleti","Sensörler","Kablo ve Bağlantı"]
    DURUMLAR = ["Müsait","Arızalı","Tamirde","Kalibrasyonda","Pil Değişimi Gerekli"]
    DURUM_RENK = {"Müsait":"#276749","Arızalı":"#C53030","Tamirde":"#C05621","Kalibrasyonda":"#2B6CB0","Pil Değişimi Gerekli":"#744210"}

    def __init__(self, db):
        super().__init__(); self.db = db; self.sid = None
        self.setWindowTitle("Envanter Yönetimi"); self.setGeometry(150,100,1200,620); self.setStyleSheet(STIL_KODU)
        lay = QHBoxLayout(self)
        sol = QGroupBox("Ekipman Bilgileri"); f = QFormLayout(sol)
        self.seri, self.isim = QLineEdit(), QLineEdit()
        self.kat = QComboBox(); self.kat.addItems(self.KATS)
        self.adet = QSpinBox(); self.adet.setRange(1,1000)
        self.durum_combo = QComboBox(); self.durum_combo.addItems(self.DURUMLAR)
        f.addRow("Seri No:", self.seri); f.addRow("İsim:", self.isim); f.addRow("Kategori:", self.kat); f.addRow("Adet:", self.adet)
        f.addRow("Bakım Durumu:", self.durum_combo)
        for lbl, fn in [("Ekle",self._ekle),("Güncelle",self._guncelle)]:
            b = QPushButton(lbl); b.clicked.connect(fn); f.addRow(b)
        hb = QHBoxLayout(); bs = QPushButton("Sil"); bs.setObjectName("red_btn"); bs.clicked.connect(self._sil)
        bt = QPushButton("Temizle"); bt.clicked.connect(self._temizle); hb.addWidget(bs); hb.addWidget(bt); f.addRow(hb)
        lay.addWidget(sol, 1)
        sag = QVBoxLayout(); ust = QHBoxLayout()
        self.ara = QLineEdit(); self.ara.setPlaceholderText("Ara..."); self.ara.textChanged.connect(self._listele)
        self.filtre = QComboBox(); self.filtre.addItems(["Tümü"]+self.KATS); self.filtre.currentTextChanged.connect(self._listele)
        ust.addWidget(QLabel("Ara:")); ust.addWidget(self.ara,2); ust.addWidget(QLabel("Kategori:")); ust.addWidget(self.filtre)
        self.tablo = QTableWidget(); self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels(["ID","Seri No","İsim","Kategori","Toplam","Müsait","Bakım Durumu"]); self.tablo.setColumnHidden(0,True)
        h = self.tablo.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(6, QHeaderView.Fixed); self.tablo.setColumnWidth(6, 200)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows); self.tablo.setEditTriggers(QTableWidget.NoEditTriggers); self.tablo.clicked.connect(self._sec)
        sag.addLayout(ust); sag.addWidget(self.tablo); lay.addLayout(sag,2); self._listele()

    def _listele(self):
        veriler = self.db.ekipmanlari_getir(self.ara.text(), self.filtre.currentText())
        tablo_doldur(self.tablo, veriler, ["id","seri_no","isim","kategori","toplam_adet","musait_adet","bakim_durumu"])
        for r in range(self.tablo.rowCount()):
            item = self.tablo.item(r,6)
            if item:
                renk = self.DURUM_RENK.get(item.text(), "#1A202C")
                item.setForeground(QColor(renk)); item.setFont(QFont("Segoe UI",10,QFont.Bold))

    def _sec(self):
        r = self.tablo.currentRow()
        if r >= 0:
            self.sid=int(self.tablo.item(r,0).text()); self.seri.setText(self.tablo.item(r,1).text())
            self.isim.setText(self.tablo.item(r,2).text()); self.kat.setCurrentText(self.tablo.item(r,3).text())
            self.adet.setValue(int(self.tablo.item(r,4).text()))
            d = self.tablo.item(r,6).text() if self.tablo.item(r,6) else "Müsait"
            self.durum_combo.setCurrentText(d if d in self.DURUMLAR else "Müsait")

    def _ekle(self):
        if not self.seri.text() or not self.isim.text(): return
        try: self.db.ekipman_ekle(self.seri.text(),self.isim.text(),self.kat.currentText(),self.adet.value()); self._temizle(); self._listele()
        except sqlite3.IntegrityError: QMessageBox.critical(self,"Hata","Bu Seri No mevcut!")

    def _guncelle(self):
        if not self.sid: return
        try:
            self.db.ekipman_guncelle(self.sid,self.isim.text(),self.kat.currentText(),self.adet.value())
            self.db.ekipman_durum_guncelle(self.sid, self.durum_combo.currentText())
        except ValueError as hata:
            return QMessageBox.warning(self,"Hata",str(hata))
        self._temizle(); self._listele()

    def _sil(self):
        if not self.sid: return
        if self.db.zimmet_var_mi_ekipman(self.sid): return QMessageBox.warning(self,"Hata","Cihaz zimmetli, önce iade alın.")
        if QMessageBox.question(self,"Sil","Pasife al?") == QMessageBox.Yes: self.db.ekipman_sil(self.sid); self._temizle(); self._listele()

    def _temizle(self): self.sid=None; self.seri.clear(); self.isim.clear(); self.adet.setValue(1); self.durum_combo.setCurrentIndex(0)

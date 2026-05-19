
import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QHeaderView, QMessageBox
)
from tasarim import STIL_KODU
from yardimcilar import tablo_doldur

class KullaniciPencere(QDialog):
    def __init__(self, db):
        super().__init__(); self.db = db; self.sid = None
        self.setWindowTitle("Kullanıcı Yönetimi"); self.setGeometry(200,150,900,500); self.setStyleSheet(STIL_KODU)
        lay = QHBoxLayout(self)
        sol = QGroupBox("Kullanıcı Bilgileri"); f = QFormLayout(sol)
        self.ad, self.soyad, self.no = QLineEdit(), QLineEdit(), QLineEdit()
        self.rol = QComboBox(); self.rol.addItems(["Öğrenci","Öğretmen"])
        f.addRow("Ad:",self.ad); f.addRow("Soyad:",self.soyad); f.addRow("Numara:",self.no); f.addRow("Rol:",self.rol)
        for lbl,fn in [("Ekle",self._ekle),("Güncelle",self._guncelle)]:
            b = QPushButton(lbl); b.clicked.connect(fn); f.addRow(b)
        hb = QHBoxLayout(); bs = QPushButton("Sil"); bs.setObjectName("red_btn"); bs.clicked.connect(self._sil)
        bt = QPushButton("Temizle"); bt.clicked.connect(self._temizle); hb.addWidget(bs); hb.addWidget(bt); f.addRow(hb)
        lay.addWidget(sol,1)
        sag = QVBoxLayout(); ust = QHBoxLayout()
        self.ara = QLineEdit(); self.ara.setPlaceholderText("Ara..."); self.ara.textChanged.connect(self._listele)
        ust.addWidget(QLabel("Ara:")); ust.addWidget(self.ara)
        self.tablo = QTableWidget(); self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["ID","Ad","Soyad","Numara","Rol"]); self.tablo.setColumnHidden(0,True)
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows); self.tablo.setEditTriggers(QTableWidget.NoEditTriggers); self.tablo.clicked.connect(self._sec)
        sag.addLayout(ust); sag.addWidget(self.tablo); lay.addLayout(sag,2); self._listele()

    def _listele(self): tablo_doldur(self.tablo, self.db.kullanicilari_getir(self.ara.text()), ["id","ad","soyad","ogrenci_no","rol"])
    def _sec(self):
        r = self.tablo.currentRow()
        if r >= 0: self.sid=int(self.tablo.item(r,0).text()); self.ad.setText(self.tablo.item(r,1).text()); self.soyad.setText(self.tablo.item(r,2).text()); self.no.setText(self.tablo.item(r,3).text()); self.rol.setCurrentText(self.tablo.item(r,4).text())
    def _ekle(self):
        if not self.ad.text() or not self.no.text(): return
        try: self.db.kullanici_ekle(self.ad.text(),self.soyad.text(),self.no.text(),self.rol.currentText()); self._temizle(); self._listele()
        except sqlite3.IntegrityError: QMessageBox.critical(self,"Hata","Bu numara mevcut!")
    def _guncelle(self):
        if self.sid: self.db.kullanici_guncelle(self.sid,self.ad.text(),self.soyad.text(),self.no.text(),self.rol.currentText()); self._temizle(); self._listele()
    def _sil(self):
        if not self.sid: return
        if self.db.zimmet_var_mi_kullanici(self.sid): return QMessageBox.warning(self,"Hata","Üzerinde aktif zimmet var, önce iade alın.")
        if QMessageBox.question(self,"Sil","Pasife al?") == QMessageBox.Yes: self.db.kullanici_sil(self.sid); self._temizle(); self._listele()
    def _temizle(self): self.sid=None; self.ad.clear(); self.soyad.clear(); self.no.clear()

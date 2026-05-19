
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QFormLayout, QGroupBox, QPushButton, QLineEdit,
    QComboBox, QListWidget, QListWidgetItem, QTableWidget, QHeaderView,
    QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt
from tasarim import STIL_KODU
from yardimcilar import tablo_doldur

class ProjePencere(QDialog):
    def __init__(self, db):
        super().__init__(); self.db = db; self.sid = None
        self.setWindowTitle("Proje Yönetimi"); self.setGeometry(200,150,1000,560); self.setStyleSheet(STIL_KODU)
        lay = QHBoxLayout(self)
        sol = QGroupBox("Proje Bilgileri"); f = QFormLayout(sol)
        self.proje_adi = QLineEdit(); self.proje_adi.setPlaceholderText("Proje veya Ders Adı...")
        self.danisman = QComboBox(); self.danisman.addItem("Seçiniz...", None)
        self.ogrenciler = QListWidget(); self.ogrenciler.setSelectionMode(QAbstractItemView.MultiSelection)
        for k in self.db.kullanicilari_getir():
            k = dict(k)
            if k['rol'] == 'Öğretmen': self.danisman.addItem(f"{k['ad']} {k['soyad']}", k['id'])
            else:
                item = QListWidgetItem(f"{k['ad']} {k['soyad']} ({k['ogrenci_no']})"); item.setData(Qt.UserRole, k['id']); self.ogrenciler.addItem(item)
        f.addRow("Proje Adı:", self.proje_adi); f.addRow("Danışman:", self.danisman); f.addRow("Üyeler:", self.ogrenciler)
        for lbl,fn in [("Ekle",self._ekle),("Güncelle",self._guncelle)]:
            b = QPushButton(lbl); b.clicked.connect(fn); f.addRow(b)
        hb = QHBoxLayout(); bs = QPushButton("Sil"); bs.setObjectName("red_btn"); bs.clicked.connect(self._sil)
        bt = QPushButton("Temizle"); bt.clicked.connect(self._temizle); hb.addWidget(bs); hb.addWidget(bt); f.addRow(hb)
        lay.addWidget(sol,1)
        sag = QVBoxLayout()
        self.tablo = QTableWidget(); self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["ID","Proje / Ders Adı","Danışman","Laboratuvar","Üyeler"]); self.tablo.setColumnHidden(0,True)
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows); self.tablo.setEditTriggers(QTableWidget.NoEditTriggers); self.tablo.clicked.connect(self._sec)
        sag.addWidget(self.tablo); lay.addLayout(sag,2); self._listele()

    def _listele(self): tablo_doldur(self.tablo, self.db.projeleri_getir(), ['id','proje_adi','danisman_adi','laboratuvar','ogrenciler']); self.tablo.resizeRowsToContents()
    def _sec(self):
        r = self.tablo.currentRow()
        if r < 0: return
        self.sid=int(self.tablo.item(r,0).text()); p=self.db.proje_bilgisi(self.sid); self.proje_adi.setText(p['isim'])
        idx=self.danisman.findData(p.get('danisman_id'))
        if idx >= 0: self.danisman.setCurrentIndex(idx)
        self.ogrenciler.clearSelection(); ids=[dict(o)['id'] for o in self.db.proje_ogrencileri(self.sid)]
        for i in range(self.ogrenciler.count()):
            if self.ogrenciler.item(i).data(Qt.UserRole) in ids: self.ogrenciler.item(i).setSelected(True)
    def _ekle(self):
        isim, d = self.proje_adi.text().strip(), self.danisman.currentData()
        if not isim or not d: return QMessageBox.warning(self,"Hata","Ad ve Danışman zorunlu.")
        self.db.proje_ekle(isim, d, [i.data(Qt.UserRole) for i in self.ogrenciler.selectedItems()]); self._temizle(); self._listele()
    def _guncelle(self):
        if not self.sid: return QMessageBox.warning(self,"Hata","Güncellemek için proje seçin.")
        isim, d = self.proje_adi.text().strip(), self.danisman.currentData()
        if not isim or not d: return
        self.db.proje_guncelle(self.sid, isim, d, [i.data(Qt.UserRole) for i in self.ogrenciler.selectedItems()]); self._listele()
    def _sil(self):
        if not self.sid: return
        if self.db.zimmet_var_mi_proje(self.sid): return QMessageBox.warning(self,"Hata","Projede zimmetli cihaz var, önce iade alın.")
        if QMessageBox.question(self,"Sil","Pasife al?") == QMessageBox.Yes: self.db.proje_sil(self.sid); self._temizle(); self._listele()
    def _temizle(self): self.sid=None; self.proje_adi.clear(); self.danisman.setCurrentIndex(0); self.ogrenciler.clearSelection()

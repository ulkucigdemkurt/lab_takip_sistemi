
import csv
from datetime import date
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QDateEdit, QTableWidget, QHeaderView, QTreeWidget,
    QTreeWidgetItem, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QColor, QFont
from tasarim import STIL_KODU
from yardimcilar import tablo_doldur

class ZimmetVerPenceresi(QDialog):
    def __init__(self, db):
        super().__init__(); self.db = db
        self.setWindowTitle("Zimmet Ver"); self.setGeometry(100,100,1050,620); self.setStyleSheet(STIL_KODU)
        lay = QVBoxLayout(self); ust = QHBoxLayout()
        sol = QVBoxLayout(); self.agac = QTreeWidget(); self.agac.setHeaderHidden(True); self.agac.itemSelectionChanged.connect(self._cihaz_sec)
        sol.addWidget(QLabel("Cihaz Listesi:")); sol.addWidget(self.agac); ust.addLayout(sol,1)
        sag = QFormLayout()
        self.lbl = QLabel("Ağaçtan seçin..."); self.lbl.setStyleSheet("color:#2B6CB0;font-weight:bold;")
        self.kullanici = QComboBox(); self.proje = QComboBox(); self.adet = QSpinBox(); self.adet.setMinimum(1); self.adet.setEnabled(False)
        self.tarih = QDateEdit(); self.tarih.setCalendarPopup(True); self.tarih.setDate(QDate.currentDate().addDays(7))
        sag.addRow("Seçili:", self.lbl); sag.addRow("Kullanıcı:", self.kullanici); sag.addRow("Proje:", self.proje); sag.addRow("Adet:", self.adet); sag.addRow("İade:", self.tarih)
        btn = QPushButton("📤 Zimmetle"); btn.clicked.connect(self._zimmetle); sag.addRow(btn)
        ust.addLayout(sag,1); lay.addLayout(ust)
        self.tablo = QTableWidget(); self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels(["ID","CihazID","Kullanıcı","Cihaz","Adet","Veriliş","İade"])
        self.tablo.setColumnHidden(0,True); self.tablo.setColumnHidden(1,True)
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows); self.tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self.tablo); self._yukle()

    def _yukle(self):
        self.kullanici.clear(); self.proje.clear(); self.proje.addItem("Yok", None)
        for k in self.db.kullanicilari_getir(): k=dict(k); self.kullanici.addItem(f"{k['ad']} {k['soyad']}", k['id'])
        for p in self.db.projeleri_getir(): p=dict(p); self.proje.addItem(p['proje_adi'], p['id'])
        self.agac.clear(); kats = {}
        for e in self.db.ekipmanlari_getir():
            e = dict(e)
            if e['musait_adet'] > 0 and e['bakim_durumu'] == "Müsait": kats.setdefault(e['kategori'],[]).append(e)
        for kat, liste in kats.items():
            ust = QTreeWidgetItem([kat]); ust.setFont(0,QFont("Segoe UI",10,QFont.Bold))
            for e in liste:
                alt = QTreeWidgetItem([e['isim']]); alt.setData(0,Qt.UserRole,e['id']); ust.addChild(alt)
            self.agac.addTopLevelItem(ust)
        tablo_doldur(self.tablo, self.db.aktif_zimmetler(), ["zimmet_id","ekipman_id","kullanici_isim","ekipman_isim","adet","verilis_tarihi","iade_tarihi"])
        bugun = str(date.today())
        for r in range(self.tablo.rowCount()):
            item = self.tablo.item(r,6)
            if item and item.text() < bugun: item.setForeground(QColor("#E53E3E")); item.setFont(QFont("Segoe UI",10,QFont.Bold))

    def _cihaz_sec(self):
        sec = self.agac.selectedItems()
        if not sec or sec[0].childCount() > 0: self.adet.setEnabled(False); return
        e = self.db.ekipman_bilgisi(sec[0].data(0,Qt.UserRole))
        if not e:
            self.adet.setEnabled(False); return QMessageBox.warning(self,"Hata","Cihaz bulunamadi.")
        self.lbl.setText(f"{e['isim']} (Stok: {e['musait_adet']})")
        if e['musait_adet'] > 0 and e['bakim_durumu'] == "Müsait": self.adet.setEnabled(True); self.adet.setMaximum(e['musait_adet'])
        else: self.adet.setEnabled(False); self.adet.setValue(1)

    def _zimmetle(self):
        if not self.agac.selectedItems() or self.agac.selectedItems()[0].childCount() > 0: return QMessageBox.warning(self,"Hata","Cihaz seçin.")
        if self.kullanici.count() == 0: return QMessageBox.warning(self,"Hata","Kayıtlı kullanıcı yok.")
        e_id = self.agac.selectedItems()[0].data(0,Qt.UserRole); e = self.db.ekipman_bilgisi(e_id)
        if not e: return QMessageBox.critical(self,"Hata","Cihaz bulunamadi.")
        if e['bakim_durumu'] != "Müsait": return QMessageBox.critical(self,"Hata",f"Cihaz zimmetlenemez. Bakim durumu: {e['bakim_durumu']}")
        if e['musait_adet'] < self.adet.value(): return QMessageBox.critical(self,"Hata",f"Stok yetersiz! (Kalan: {e['musait_adet']})")
        try:
            self.db.zimmet_ekle(e_id, self.kullanici.currentData(), self.adet.value(), self.tarih.date().toString("yyyy-MM-dd"), self.proje.currentData())
        except ValueError as hata:
            return QMessageBox.critical(self,"Hata",str(hata))
        QMessageBox.information(self,"Başarılı","Zimmetlendi."); self._yukle()

class GecmisPenceresi(QDialog):
    def __init__(self, db):
        super().__init__(); self.db = db
        self.setWindowTitle("Zimmet Geçmişi ve İade"); self.setGeometry(200,150,1000,500); self.setStyleSheet(STIL_KODU)
        lay = QVBoxLayout(self); ust = QHBoxLayout()
        self.ara = QLineEdit(); self.ara.setPlaceholderText("Kullanıcı, cihaz veya proje ara..."); self.ara.textChanged.connect(self._filtrele)
        btn_iade = QPushButton("✅ Seçili Cihazı İade Al"); btn_iade.setObjectName("onay_btn"); btn_iade.clicked.connect(self._iade)
        btn_csv = QPushButton("📥 Excel'e Aktar"); btn_csv.clicked.connect(self._csv)
        ust.addWidget(QLabel("🔍")); ust.addWidget(self.ara); ust.addWidget(btn_iade); ust.addWidget(btn_csv); lay.addLayout(ust)
        self.tablo = QTableWidget(); self.tablo.setColumnCount(10)
        self.tablo.setHorizontalHeaderLabels(["ID","EkipmanID","Cihaz","Adet","Kullanıcı","Proje","Veriliş","İade","Gerçek İade","Durum"])
        self.tablo.setColumnHidden(0,True); self.tablo.setColumnHidden(1,True)
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows); self.tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self.tablo); self._doldur()

    def _doldur(self):
        tablo_doldur(self.tablo, self.db.zimmet_gecmisi(), ["id","ekipman_id","ekipman_isim","adet","kullanici_isim","proje_isim","verilis_tarihi","iade_tarihi","gercek_iade_tarihi","durum"])
        for r in range(self.tablo.rowCount()):
            if self.tablo.item(r,8) and not self.tablo.item(r,8).text(): self.tablo.item(r,8).setText("-")
            if self.tablo.item(r,9) and self.tablo.item(r,9).text() == "İade Edildi": self.tablo.item(r,9).setForeground(QColor("#276749"))

    def _iade(self):
        r = self.tablo.currentRow()
        if r < 0: return QMessageBox.warning(self,"Hata","Kayıt seçin.")
        if self.tablo.item(r,9).text() != "Aktif": return QMessageBox.warning(self,"Uyarı","Zaten iade edilmiş.")
        try:
            self.db.iade_al(int(self.tablo.item(r,0).text()), int(self.tablo.item(r,1).text()), int(self.tablo.item(r,3).text()))
        except ValueError as hata:
            return QMessageBox.critical(self,"Hata",str(hata))
        QMessageBox.information(self,"Başarılı","Cihaz teslim alındı."); self._doldur()

    def _filtrele(self, text):
        t = text.lower()
        for r in range(self.tablo.rowCount()):
            self.tablo.setRowHidden(r, not any(t in (self.tablo.item(r,c).text().lower() if self.tablo.item(r,c) else "") for c in range(self.tablo.columnCount())))

    def _csv(self):
        yol, _ = QFileDialog.getSaveFileName(self,"Dışa Aktar","zimmet_gecmisi.csv","CSV (*.csv)")
        if not yol: return
        try:
            with open(yol,'w',newline='',encoding='utf-8-sig') as f:
                w = csv.writer(f, delimiter=';')
                w.writerow([self.tablo.horizontalHeaderItem(i).text() for i in range(self.tablo.columnCount()) if not self.tablo.isColumnHidden(i)])
                for r in range(self.tablo.rowCount()):
                    if not self.tablo.isRowHidden(r):
                        w.writerow([self.tablo.item(r,c).text() if self.tablo.item(r,c) else "" for c in range(self.tablo.columnCount()) if not self.tablo.isColumnHidden(c)])
            QMessageBox.information(self,"Başarılı","Dışa aktarıldı.")
        except Exception as e: QMessageBox.critical(self,"Hata",str(e))

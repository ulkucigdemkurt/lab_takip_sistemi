import sys, sqlite3, os, csv
from datetime import date
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QGroupBox, QLabel, QPushButton, QLineEdit, QComboBox,
    QSpinBox, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QMessageBox, QGridLayout, QSizePolicy, QAbstractItemView, QFileDialog
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QColor, QFont
from tasarim import STIL_KODU

def tablo_doldur(tablo, veriler, sutunlar):
    tablo.setSortingEnabled(False); tablo.setRowCount(len(veriler))
    for r, veri in enumerate(veriler):
        v = dict(veri)
        for c, s in enumerate(sutunlar):
            d = v.get(s); item = QTableWidgetItem()
            item.setData(Qt.EditRole, d if isinstance(d, (int, float)) else ("" if d is None else str(d)))
            item.setTextAlignment(Qt.AlignCenter); tablo.setItem(r, c, item)
    tablo.setSortingEnabled(True)

class DB:
    def __init__(self):
        self.dosya = os.path.join(os.path.dirname(os.path.abspath(__file__)), "veri_tabani.db")

    def _q(self, sql, p=()):
        with sqlite3.connect(self.dosya) as b:
            b.row_factory = sqlite3.Row; return b.execute(sql, p).fetchall()

    def _r(self, sql, p=()):
        with sqlite3.connect(self.dosya) as b:
            c = b.execute(sql, p); b.commit(); return c.lastrowid

    def ekipmanlari_getir(self, ara="", kat=""):
        sql, p = "SELECT * FROM ekipmanlar WHERE is_active=1", []
        if ara: sql += " AND (isim LIKE ? OR seri_no LIKE ?)"; p += [f"%{ara}%", f"%{ara}%"]
        if kat and kat != "Tümü": sql += " AND kategori=?"; p.append(kat)
        return self._q(sql + " ORDER BY kategori, isim", tuple(p))
    def ekipman_bilgisi(self, id_):
        r = self._q("SELECT * FROM ekipmanlar WHERE id=?", (id_,))
        return r[0] if r else None
    def ekipman_ekle(self, s, i, k, a): self._r("INSERT INTO ekipmanlar (seri_no,isim,kategori,toplam_adet,musait_adet,bakim_durumu) VALUES (?,?,?,?,?,'Müsait')", (s,i,k,a,a))
    def ekipman_guncelle(self, id_, i, k, a):
        with sqlite3.connect(self.dosya) as b:
            b.row_factory = sqlite3.Row
            aktif = b.execute("SELECT COALESCE(SUM(adet),0) c FROM zimmetler WHERE ekipman_id=? AND durum='Aktif'", (id_,)).fetchone()['c']
            if a < aktif:
                raise ValueError(f"Toplam adet aktif zimmetten az olamaz. Aktif zimmet: {aktif}")
            b.execute("UPDATE ekipmanlar SET isim=?,kategori=?,toplam_adet=?,musait_adet=? WHERE id=?", (i,k,a,a-aktif,id_))
    def ekipman_durum_guncelle(self, id_, durum): self._r("UPDATE ekipmanlar SET bakim_durumu=? WHERE id=?", (durum,id_))
    def ekipman_sil(self, id_): self._r("UPDATE ekipmanlar SET is_active=0 WHERE id=?", (id_,))
    def zimmet_var_mi_ekipman(self, id_): return bool(self._q("SELECT 1 FROM zimmetler WHERE ekipman_id=? AND durum='Aktif'", (id_,)))

    def kullanicilari_getir(self, ara=""):
        sql, p = "SELECT * FROM kullanicilar WHERE is_active=1 ", ()
        if ara: sql += "AND (ad LIKE ? OR soyad LIKE ? OR ogrenci_no LIKE ?)"; p = (f"%{ara}%",)*3
        return self._q(sql + "ORDER BY ad", p)
    def kullanici_ekle(self, a, s, o, r): self._r("INSERT INTO kullanicilar (ad,soyad,ogrenci_no,rol) VALUES (?,?,?,?)", (a,s,o,r))
    def kullanici_guncelle(self, id_, a, s, o, r): self._r("UPDATE kullanicilar SET ad=?,soyad=?,ogrenci_no=?,rol=? WHERE id=?", (a,s,o,r,id_))
    def kullanici_sil(self, id_): self._r("UPDATE kullanicilar SET is_active=0 WHERE id=?", (id_,))
    def zimmet_var_mi_kullanici(self, id_): return bool(self._q("SELECT 1 FROM zimmetler WHERE kullanici_id=? AND durum='Aktif'", (id_,)))

    def projeleri_getir(self):
        return self._q("""SELECT p.id, p.isim AS proje_adi, d.ad||' '||d.soyad AS danisman_adi,
            COALESCE(l.isim,'Atanmadı') AS laboratuvar, p.lab_id,
            COALESCE((SELECT GROUP_CONCAT(k2.ad||' '||k2.soyad, char(10)) FROM proje_ogrencileri po
                JOIN kullanicilar k2 ON po.ogrenci_id=k2.id WHERE po.proje_id=p.id AND k2.is_active=1),'-') AS ogrenciler
            FROM projeler p LEFT JOIN kullanicilar d ON p.danisman_id=d.id
            LEFT JOIN laboratuvarlar l ON p.lab_id=l.id WHERE p.is_active=1 ORDER BY p.isim""")
    def proje_bilgisi(self, id_):
        r = self._q("SELECT * FROM projeler WHERE id=?", (id_,)); return dict(r[0]) if r else None
    def proje_ogrencileri(self, id_):
        return self._q("SELECT k.* FROM proje_ogrencileri po JOIN kullanicilar k ON po.ogrenci_id=k.id WHERE po.proje_id=? AND k.is_active=1", (id_,))
    def proje_ekle(self, i, d, ogrs):
        with sqlite3.connect(self.dosya) as b:
            c = b.execute("INSERT INTO projeler (isim,danisman_id) VALUES (?,?)", (i,d))
            pid = c.lastrowid
            b.executemany("INSERT INTO proje_ogrencileri (proje_id,ogrenci_id) VALUES (?,?)", [(pid,o) for o in ogrs])
    def proje_guncelle(self, id_, i, d, ogrs):
        with sqlite3.connect(self.dosya) as b:
            b.execute("UPDATE projeler SET isim=?,danisman_id=? WHERE id=?", (i,d,id_))
            b.execute("DELETE FROM proje_ogrencileri WHERE proje_id=?", (id_,))
            b.executemany("INSERT INTO proje_ogrencileri (proje_id,ogrenci_id) VALUES (?,?)", [(id_,o) for o in ogrs])
    def proje_sil(self, id_): self._r("UPDATE projeler SET is_active=0 WHERE id=?", (id_,))
    def zimmet_var_mi_proje(self, id_): return bool(self._q("SELECT 1 FROM zimmetler WHERE proje_id=? AND durum='Aktif'", (id_,)))

    def aktif_zimmetler(self):
        return self._q("""SELECT z.id AS zimmet_id, z.ekipman_id, e.isim AS ekipman_isim, z.adet,
            k.ad||' '||k.soyad AS kullanici_isim, COALESCE(p.isim,'-') AS proje_isim, z.verilis_tarihi, z.iade_tarihi
            FROM zimmetler z JOIN ekipmanlar e ON z.ekipman_id=e.id JOIN kullanicilar k ON z.kullanici_id=k.id
            LEFT JOIN projeler p ON z.proje_id=p.id WHERE z.durum='Aktif' ORDER BY z.iade_tarihi""")
    def zimmet_gecmisi(self):
        return self._q("""SELECT z.id, z.ekipman_id, e.isim AS ekipman_isim, z.adet,
            k.ad||' '||k.soyad AS kullanici_isim, COALESCE(p.isim,'-') AS proje_isim,
            z.verilis_tarihi, z.iade_tarihi, z.gercek_iade_tarihi, z.durum
            FROM zimmetler z JOIN ekipmanlar e ON z.ekipman_id=e.id JOIN kullanicilar k ON z.kullanici_id=k.id
            LEFT JOIN projeler p ON z.proje_id=p.id ORDER BY z.verilis_tarihi DESC""")
    def zimmet_ekle(self, e_id, k_id, adet, iade, proje_id=None):
        with sqlite3.connect(self.dosya) as b:
            b.row_factory = sqlite3.Row
            e = b.execute("SELECT musait_adet,bakim_durumu,is_active FROM ekipmanlar WHERE id=?", (e_id,)).fetchone()
            if not e or not e['is_active']:
                raise ValueError("Cihaz bulunamadi.")
            if e['bakim_durumu'] != "Müsait":
                raise ValueError(f"Cihaz zimmetlenemez. Bakim durumu: {e['bakim_durumu']}")
            if e['musait_adet'] < adet:
                raise ValueError(f"Stok yetersiz! (Kalan: {e['musait_adet']})")
            b.execute("INSERT INTO zimmetler (ekipman_id,kullanici_id,proje_id,adet,verilis_tarihi,iade_tarihi) VALUES (?,?,?,?,?,?)", (e_id,k_id,proje_id,adet,str(date.today()),iade))
            b.execute("UPDATE ekipmanlar SET musait_adet=musait_adet-? WHERE id=?", (adet,e_id))
    def iade_al(self, z_id, e_id, adet):
        with sqlite3.connect(self.dosya) as b:
            b.row_factory = sqlite3.Row
            z = b.execute("SELECT ekipman_id,adet,durum FROM zimmetler WHERE id=?", (z_id,)).fetchone()
            if not z:
                raise ValueError("Zimmet kaydi bulunamadi.")
            if z['durum'] != "Aktif":
                raise ValueError("Bu cihaz zaten iade edilmis.")
            if z['ekipman_id'] != e_id or z['adet'] != adet:
                raise ValueError("Secili zimmet bilgisi guncel degil.")
            b.execute("UPDATE zimmetler SET durum='\u0130ade Edildi',gercek_iade_tarihi=? WHERE id=?", (str(date.today()),z_id))
            b.execute("UPDATE ekipmanlar SET musait_adet=musait_adet+? WHERE id=?", (adet,e_id))
    def istatistik(self):
        return {"ekipman": self._q("SELECT COUNT(*) c FROM ekipmanlar WHERE is_active=1")[0]['c'],
                "zimmet":  self._q("SELECT COUNT(*) c FROM zimmetler WHERE durum='Aktif'")[0]['c']}

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

class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__(); self.db = DB()
        self.setWindowTitle("BAUN Laboratuvar Takip Sistemi"); self.setGeometry(100,100,1100,680); self.setStyleSheet(STIL_KODU)
        w = QWidget(); self.setCentralWidget(w); lay = QVBoxLayout(w); lay.setSpacing(16); lay.setContentsMargins(20,16,20,16)

        lay.addWidget(QLabel("🔬  <b>BAUN Laboratuvar Takip Sistemi</b>", styleSheet="font-size:18px;color:#22543D;padding:4px 0;"))

        kart_lay = QHBoxLayout(); kart_lay.setSpacing(15); self.kart = {}
        for key, baslik, ikon, renk in [("ekipman","Laboratuvar Envanteri","📦","#3182CE"),("zimmet","Aktif Zimmet Sayısı","🔗","#DD6B20")]:
            g = QGroupBox()
            g.setStyleSheet(f"QGroupBox{{border: 1px solid #E2E8F0; border-top: 4px solid {renk}; border-radius: 8px; background: #FFFFFF; margin-top: 0; padding: 10px;}}")
            hl = QHBoxLayout(g)
            ikon_lbl = QLabel(ikon); ikon_lbl.setStyleSheet("font-size:28px;"); ikon_lbl.setFixedWidth(44)
            sag = QVBoxLayout()
            baslik_lbl = QLabel(baslik); baslik_lbl.setStyleSheet(f"font-size:12px;color:#718096;font-weight:bold;")
            sayi_lbl = QLabel("0"); sayi_lbl.setStyleSheet(f"font-size:28px;font-weight:bold;color:{renk};")
            sag.addWidget(baslik_lbl); sag.addWidget(sayi_lbl)
            hl.addWidget(ikon_lbl); hl.addLayout(sag)
            self.kart[key] = sayi_lbl; kart_lay.addWidget(g)
        lay.addLayout(kart_lay)

        MENU = [
            ("📦","Zimmet Ver",self._zimmet_ac),
            ("📜","Geçmiş ve İade",self._gecmis_ac),
            ("🔧","Envanter",self._ekipman_ac),
            ("👤","Kullanıcılar",self._kullanici_ac),
            ("📂","Projeler",self._proje_ac),
        ]
        menu = QGridLayout(); menu.setSpacing(15)
        for i,(ikon,metin,fn) in enumerate(MENU):
            b = QPushButton(f"{ikon}\n{metin}")
            b.setFixedHeight(85)
            b.setStyleSheet("QPushButton{font-size:13px; font-weight:bold; padding:8px; border: 1px solid #CBD5E0; border-radius: 8px; background-color: #FFFFFF; color: #2D3748;} QPushButton:hover{background-color:#F7FAFC; border: 1px solid #A0AEC0;}")
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.clicked.connect(fn); menu.addWidget(b,0,i)
        lay.addLayout(menu)
        lay.addStretch()
        self._guncelle()

    def _guncelle(self):
        s = self.db.istatistik(); self.kart['ekipman'].setText(str(s['ekipman'])); self.kart['zimmet'].setText(str(s['zimmet']))

    def _zimmet_ac(self): ZimmetVerPenceresi(self.db).exec_(); self._guncelle()
    def _gecmis_ac(self): GecmisPenceresi(self.db).exec_(); self._guncelle()
    def _ekipman_ac(self): EkipmanPencere(self.db).exec_(); self._guncelle()
    def _kullanici_ac(self): KullaniciPencere(self.db).exec_(); self._guncelle()
    def _proje_ac(self): ProjePencere(self.db).exec_(); self._guncelle()

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    w = AnaPencere(); w.show(); sys.exit(app.exec_())
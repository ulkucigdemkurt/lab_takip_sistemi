import sys, sqlite3, os, csv, io
from datetime import date
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QGroupBox, QLabel, QPushButton, QLineEdit, QComboBox,
    QSpinBox, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QMessageBox, QGridLayout, QSizePolicy, QAbstractItemView, QFileDialog
)
from PyQt5.QtCore import QDate, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QPixmap, QImage
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import reportlab.lib.pagesizes as pgsz
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image, Paragraph
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

TEMALAR = {
    "mavi":    {"ana": "#2B6CB0", "acik": "#EBF8FF", "hover": "#90CDF4", "kenar": "#BEE3F8"},
    "turuncu": {"ana": "#C05621", "acik": "#FFFAF0", "hover": "#FBD38D", "kenar": "#FEEBC8"},
    "mor":     {"ana": "#553C9A", "acik": "#FAF5FF", "hover": "#D6BCFA", "kenar": "#E9D8FD"},
    "kirmizi": {"ana": "#C53030", "acik": "#FFF5F5", "hover": "#FEB2B2", "kenar": "#FED7D7"},
    "turkuaz": {"ana": "#234E52", "acik": "#E6FFFA", "hover": "#81E6D9", "kenar": "#B2F5EA"},
    "yesil":   {"ana": "#276749", "acik": "#F0FAF4", "hover": "#9AE6B4", "kenar": "#C6F6D5"}
}

def get_stil(tema):
    ana = tema["ana"]; acik = tema["acik"]; hover = tema["hover"]; kenar = tema["kenar"]
    return f"""
    QMainWindow, QDialog {{ background-color: {acik}; color: #1C3A2A; font-family: 'Segoe UI', sans-serif; }}
    QGroupBox {{ background-color: #FFFFFF; border: 1px solid {kenar}; border-radius: 12px; margin-top: 18px; font-weight: bold; color: {ana}; padding: 12px; }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 16px; padding: 0 8px; color: {ana}; }}
    QPushButton {{ background-color: #FFFFFF; color: {ana}; border-radius: 9px; padding: 8px 16px; font-weight: bold; font-size: 12px; border: 1px solid {kenar}; }}
    QPushButton:hover {{ background-color: {acik}; border: 1.5px solid {ana}; }}
    
    QPushButton#onay_btn {{ background-color: #C6F6D5; color: #22543D; border: 1px solid #68D391; }}
    QPushButton#onay_btn:hover {{ background-color: #9AE6B4; border: 1px solid #38A169; }}
    QPushButton#red_btn {{ background-color: #FFF5F5; color: #9B2C2C; border: 1px solid #FEB2B2; }}
    QPushButton#red_btn:hover {{ background-color: #FED7D7; border: 1px solid #FC8181; }}
    QPushButton#primary_btn {{ background-color: #276749; color: #FFFFFF; border: 1px solid #276749; }}
    QPushButton#primary_btn:hover {{ background-color: #22543D; border: 1px solid #22543D; }}
    QPushButton#warn_btn {{ background-color: #FEFCBF; color: #744210; border: 1px solid #F6E05E; }}
    QPushButton#warn_btn:hover {{ background-color: #FAF089; border: 1px solid #ECC94B; }}
    
    QLineEdit, QComboBox, QSpinBox, QDateEdit, QTextEdit {{ background-color: #FFFFFF; border: 1.5px solid {kenar}; border-radius: 7px; padding: 7px 10px; color: #1C3A2A; font-size: 12px; selection-background-color: {hover}; }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QTextEdit:focus {{ border: 1.5px solid {ana}; }}
    QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {{ background-color: {acik}; color: #A0AEC0; }}
    QComboBox::drop-down {{ border: none; width: 30px; }}
    QComboBox QAbstractItemView {{ border: 1px solid {kenar}; selection-background-color: {acik}; selection-color: #1A202C; background-color: white; border-radius: 4px; }}
    QTableWidget, QTreeWidget, QListWidget {{ background-color: #FFFFFF; alternate-background-color: {acik}; border: 1px solid {kenar}; gridline-color: {acik}; border-radius: 8px; color: #1C3A2A; font-size: 12px; }}
    QHeaderView::section {{ background-color: {kenar}; color: {ana}; padding: 8px; border: none; font-weight: bold; font-size: 12px; }}
    QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {{ background-color: {hover}; color: #1C3A2A; }}
    QTabWidget::pane {{ border: 1px solid {kenar}; background: #FFFFFF; border-radius: 6px; }}
    QTabBar::tab {{ background: {acik}; color: {ana}; padding: 8px 18px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-size: 12px; }}
    QTabBar::tab:selected {{ background: #FFFFFF; color: {ana}; font-weight: bold; border: 1px solid {kenar}; border-bottom: none; }}
    QScrollBar:vertical {{ background: {acik}; width: 8px; border-radius: 4px; }}
    QScrollBar::handle:vertical {{ background: {hover}; border-radius: 4px; min-height: 20px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """

def _font_kaydet():
    adaylar = [
        ("C:/Windows/Fonts/arial.ttf",    "C:/Windows/Fonts/arialbd.ttf"),
        ("C:/Windows/Fonts/calibri.ttf",  "C:/Windows/Fonts/calibrib.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    for normal, kalin in adaylar:
        if os.path.exists(normal):
            pdfmetrics.registerFont(TTFont('TRFont', normal))
            pdfmetrics.registerFont(TTFont('TRFont-Bold', kalin if os.path.exists(kalin) else normal))
            return True
    return False
_FONT_OK = _font_kaydet()

def _pdf_stiller():
    st = getSampleStyleSheet()
    fn = 'TRFont' if _FONT_OK else 'Helvetica'
    fb = 'TRFont-Bold' if _FONT_OK else 'Helvetica-Bold'
    # Koyu Lacivert ve Gri tonları (Kurumsal Rapor Görünümü)
    st.add(ParagraphStyle('Baslik', fontName=fb, fontSize=16, alignment=TA_CENTER, textColor=colors.HexColor('#2C5282'), spaceAfter=4))
    st.add(ParagraphStyle('AltBaslik', fontName=fb, fontSize=11, textColor=colors.HexColor('#2B6CB0'), spaceBefore=8, spaceAfter=4))
    st.add(ParagraphStyle('Kucuk', fontName=fn, fontSize=9, textColor=colors.HexColor('#718096')))
    return st

def _pdf_tablo_stili():
    fb = 'TRFont-Bold' if _FONT_OK else 'Helvetica-Bold'
    fn = 'TRFont' if _FONT_OK else 'Helvetica'
    return TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#BEE3F8')), 
        ('TEXTCOLOR',     (0,0), (-1,0), colors.HexColor('#2C5282')), 
        ('FONTNAME',      (0,0), (-1,0), fb),
        ('FONTNAME',      (0,1), (-1,-1), fn),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]), 
        ('GRID',          (0,0), (-1,-1), 0.5, colors.HexColor('#90CDF4')), 
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ])

def tablo_doldur(tablo, veriler, sutunlar):
    tablo.setSortingEnabled(False); tablo.setRowCount(len(veriler))
    for r, veri in enumerate(veriler):
        v = dict(veri)
        for c, s in enumerate(sutunlar):
            d = v.get(s); item = QTableWidgetItem()
            item.setData(Qt.EditRole, d if isinstance(d, (int, float)) else ("" if d is None else str(d)))
            item.setTextAlignment(Qt.AlignCenter); tablo.setItem(r, c, item)
    tablo.setSortingEnabled(True)

# ── VERİTABANI ───────────────────────────────────────────────────────────────
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
        r = self._q("SELECT * FROM ekipmanlar WHERE id=?", (id_,)); return r[0] if r else None
    def ekipman_ekle(self, s, i, k, a): self._r("INSERT INTO ekipmanlar (seri_no,isim,kategori,toplam_adet,musait_adet,bakim_durumu) VALUES (?,?,?,?,?,'Müsait')", (s,i,k,a,a))
    def ekipman_guncelle(self, id_, i, k, a):
        with sqlite3.connect(self.dosya) as b:
            b.row_factory = sqlite3.Row
            aktif = b.execute("SELECT COALESCE(SUM(adet),0) c FROM zimmetler WHERE ekipman_id=? AND durum='Aktif'", (id_,)).fetchone()['c']
            if a < aktif: raise ValueError(f"Toplam adet aktif zimmetten az olamaz. Aktif zimmet: {aktif}")
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
            pid = b.execute("INSERT INTO projeler (isim,danisman_id) VALUES (?,?)", (i,d)).lastrowid
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
            if not e or not e['is_active']: raise ValueError("Cihaz bulunamadı.")
            if e['bakim_durumu'] != "Müsait": raise ValueError(f"Cihaz zimmetlenemez. Bakım durumu: {e['bakim_durumu']}")
            if e['musait_adet'] < adet: raise ValueError(f"Stok yetersiz! (Kalan: {e['musait_adet']})")
            b.execute("INSERT INTO zimmetler (ekipman_id,kullanici_id,proje_id,adet,verilis_tarihi,iade_tarihi) VALUES (?,?,?,?,?,?)", (e_id,k_id,proje_id,adet,str(date.today()),iade))
            b.execute("UPDATE ekipmanlar SET musait_adet=musait_adet-? WHERE id=?", (adet,e_id))
    def iade_al(self, z_id, e_id, adet):
        with sqlite3.connect(self.dosya) as b:
            b.row_factory = sqlite3.Row
            z = b.execute("SELECT ekipman_id,adet,durum FROM zimmetler WHERE id=?", (z_id,)).fetchone()
            if not z: raise ValueError("Zimmet kaydı bulunamadı.")
            if z['durum'] != "Aktif": raise ValueError("Bu cihaz zaten iade edilmiş.")
            if z['ekipman_id'] != e_id or z['adet'] != adet: raise ValueError("Seçili zimmet bilgisi güncel değil.")
            b.execute("UPDATE zimmetler SET durum='İade Edildi',gercek_iade_tarihi=? WHERE id=?", (str(date.today()),z_id))
            b.execute("UPDATE ekipmanlar SET musait_adet=musait_adet+? WHERE id=?", (adet,e_id))
    def kategori_istatistik(self):
        return self._q("SELECT kategori, SUM(musait_adet) m, SUM(toplam_adet-musait_adet) o, SUM(toplam_adet) t FROM ekipmanlar WHERE is_active=1 GROUP BY kategori ORDER BY kategori")
    def en_cok_zimmetlenen(self, n=5):
        return self._q("SELECT e.isim, COUNT(*) say, SUM(z.adet) adet FROM zimmetler z JOIN ekipmanlar e ON z.ekipman_id=e.id GROUP BY z.ekipman_id ORDER BY say DESC LIMIT ?", (n,))
    def istatistik(self):
        return {"ekipman": self._q("SELECT COUNT(*) c FROM ekipmanlar WHERE is_active=1")[0]['c'],
                "zimmet":  self._q("SELECT COUNT(*) c FROM zimmetler WHERE durum='Aktif'")[0]['c']}

# ── EKIPMAN ──────────────────────────────────────────────────────────────────
class EkipmanPencere(QDialog):
    KATS = ["Sarf Malzeme","Mikrodenetleyici","Demirbaş Cihaz","El Aleti","Sensörler","Kablo ve Bağlantı"]
    DURUMLAR = ["Müsait","Arızalı","Tamirde","Kalibrasyonda","Pil Değişimi Gerekli"]
    
    def __init__(self, db, tema):
        super().__init__(); self.db = db; self.sid = None; self.tema = tema
        self.setWindowTitle("Envanter Yönetimi"); self.setGeometry(150,100,1200,620)
        self.setStyleSheet(get_stil(tema))
        lay = QHBoxLayout(self)
        sol = QGroupBox("Ekipman Bilgileri"); f = QFormLayout(sol)
        self.seri, self.isim = QLineEdit(), QLineEdit()
        self.kat = QComboBox(); self.kat.addItems(self.KATS)
        self.adet = QSpinBox(); self.adet.setRange(1,1000)
        self.durum_combo = QComboBox(); self.durum_combo.addItems(self.DURUMLAR)
        f.addRow("Seri No:", self.seri); f.addRow("İsim:", self.isim); f.addRow("Kategori:", self.kat)
        f.addRow("Adet:", self.adet); f.addRow("Bakım Durumu:", self.durum_combo)
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
        h = self.tablo.horizontalHeader(); h.setSectionResizeMode(QHeaderView.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeToContents); h.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.ResizeToContents); h.setSectionResizeMode(6, QHeaderView.Fixed); self.tablo.setColumnWidth(6, 200)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows); self.tablo.setEditTriggers(QTableWidget.NoEditTriggers); self.tablo.clicked.connect(self._sec)
        sag.addLayout(ust); sag.addWidget(self.tablo); lay.addLayout(sag,2); self._listele()

    def _listele(self):
        tablo_doldur(self.tablo, self.db.ekipmanlari_getir(self.ara.text(), self.filtre.currentText()), ["id","seri_no","isim","kategori","toplam_adet","musait_adet","bakim_durumu"])
        durum_renk = {"Müsait":"#276749","Arızalı":"#C53030","Tamirde":"#C05621","Kalibrasyonda":"#2B6CB0","Pil Değişimi Gerekli":"#744210"}
        for r in range(self.tablo.rowCount()):
            item = self.tablo.item(r,6)
            if item: item.setForeground(QColor(durum_renk.get(item.text(),"#1A202C"))); item.setFont(QFont("Segoe UI",10,QFont.Bold))
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
        try: self.db.ekipman_guncelle(self.sid,self.isim.text(),self.kat.currentText(),self.adet.value()); self.db.ekipman_durum_guncelle(self.sid,self.durum_combo.currentText())
        except ValueError as e: return QMessageBox.warning(self,"Hata",str(e))
        self._temizle(); self._listele()
    def _sil(self):
        if not self.sid: return
        if self.db.zimmet_var_mi_ekipman(self.sid): return QMessageBox.warning(self,"Hata","Cihaz zimmetli, önce iade alın.")
        if QMessageBox.question(self,"Sil","Pasife al?") == QMessageBox.Yes: self.db.ekipman_sil(self.sid); self._temizle(); self._listele()
    def _temizle(self): self.sid=None; self.seri.clear(); self.isim.clear(); self.adet.setValue(1); self.durum_combo.setCurrentIndex(0)

# ── KULLANICI ─────────────────────────────────────────────────────────────────
class KullaniciPencere(QDialog):
    def __init__(self, db, tema):
        super().__init__(); self.db = db; self.sid = None
        self.setWindowTitle("Kullanıcı Yönetimi"); self.setGeometry(200,150,900,500)
        self.setStyleSheet(get_stil(tema))
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

# ── PROJE ─────────────────────────────────────────────────────────────────────
class ProjePencere(QDialog):
    def __init__(self, db, tema):
        super().__init__(); self.db = db; self.sid = None
        self.setWindowTitle("Proje Yönetimi"); self.setGeometry(200,150,1000,560)
        self.setStyleSheet(get_stil(tema))
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

# ── ZİMMET VER ────────────────────────────────────────────────────────────────
class ZimmetVerPenceresi(QDialog):
    def __init__(self, db, tema):
        super().__init__(); self.db = db
        self.setWindowTitle("Zimmet Ver"); self.setGeometry(100,100,1050,620)
        self.setStyleSheet(get_stil(tema))
        lay = QVBoxLayout(self); ust = QHBoxLayout()
        sol = QVBoxLayout(); self.agac = QTreeWidget(); self.agac.setHeaderHidden(True); self.agac.itemSelectionChanged.connect(self._cihaz_sec)
        sol.addWidget(QLabel("Cihaz Listesi:")); sol.addWidget(self.agac); ust.addLayout(sol,1)
        sag = QFormLayout()
        self.lbl = QLabel("Ağaçtan seçin..."); self.lbl.setStyleSheet(f"color:{tema['ana']};font-weight:bold;")
        self.kullanici = QComboBox(); self.proje = QComboBox(); self.adet = QSpinBox(); self.adet.setMinimum(1); self.adet.setEnabled(False)
        self.tarih = QDateEdit(); self.tarih.setCalendarPopup(True); self.tarih.setDate(QDate.currentDate().addDays(7))
        sag.addRow("Seçili:", self.lbl); sag.addRow("Kullanıcı:", self.kullanici); sag.addRow("Proje:", self.proje)
        sag.addRow("Adet:", self.adet); sag.addRow("İade:", self.tarih)
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
        if not e: self.adet.setEnabled(False); return
        self.lbl.setText(f"{e['isim']} (Stok: {e['musait_adet']})")
        if e['musait_adet'] > 0 and e['bakim_durumu'] == "Müsait": self.adet.setEnabled(True); self.adet.setMaximum(e['musait_adet'])
        else: self.adet.setEnabled(False); self.adet.setValue(1)

    def _zimmetle(self):
        if not self.agac.selectedItems() or self.agac.selectedItems()[0].childCount() > 0: return QMessageBox.warning(self,"Hata","Cihaz seçin.")
        if self.kullanici.count() == 0: return QMessageBox.warning(self,"Hata","Kayıtlı kullanıcı yok.")
        e_id = self.agac.selectedItems()[0].data(0,Qt.UserRole)
        try: self.db.zimmet_ekle(e_id, self.kullanici.currentData(), self.adet.value(), self.tarih.date().toString("yyyy-MM-dd"), self.proje.currentData())
        except ValueError as e: return QMessageBox.critical(self,"Hata",str(e))
        QMessageBox.information(self,"Başarılı","Zimmetlendi."); self._yukle()

# ── GEÇMİŞ VE İADE ───────────────────────────────────────────────────────────
class GecmisPenceresi(QDialog):
    def __init__(self, db, tema):
        super().__init__(); self.db = db
        self.setWindowTitle("Zimmet Geçmişi ve İade"); self.setGeometry(200,150,1000,500)
        self.setStyleSheet(get_stil(tema))
        lay = QVBoxLayout(self); ust = QHBoxLayout()
        self.ara = QLineEdit(); self.ara.setPlaceholderText("Kullanıcı, cihaz veya proje ara..."); self.ara.textChanged.connect(self._filtrele)
        btn_iade = QPushButton("✅ Seçili Cihazı İade Al"); btn_iade.setObjectName("onay_btn"); btn_iade.clicked.connect(self._iade)
        btn_csv = QPushButton("📥 Excel'e Aktar"); btn_csv.clicked.connect(self._csv)
        btn_pdf = QPushButton("📄 PDF Raporu"); btn_pdf.clicked.connect(self._pdf)
        ust.addWidget(QLabel("🔍")); ust.addWidget(self.ara); ust.addWidget(btn_iade); ust.addWidget(btn_csv); ust.addWidget(btn_pdf); lay.addLayout(ust)
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
        try: self.db.iade_al(int(self.tablo.item(r,0).text()), int(self.tablo.item(r,1).text()), int(self.tablo.item(r,3).text()))
        except ValueError as e: return QMessageBox.critical(self,"Hata",str(e))
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

    def _pdf(self):
        yol, _ = QFileDialog.getSaveFileName(self,"PDF Kaydet","lab_raporu.pdf","PDF (*.pdf)")
        if not yol: return
        try:
            doc = SimpleDocTemplate(yol, pagesize=pgsz.A4, topMargin=1.5*cm, bottomMargin=1.5*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)
            st = _pdf_stiller(); ts = _pdf_tablo_stili(); h = []
            h.append(Paragraph("BAUN Laboratuvar Takip Sistemi", st['Baslik']))
            h.append(Paragraph(f"Rapor Tarihi: {date.today().strftime('%d.%m.%Y')}", st['Kucuk']))
            h.append(Spacer(1, 0.5*cm))
            veriler = self.db.kategori_istatistik()
            if veriler:
                kats=[dict(v)['kategori'] for v in veriler]; m=[dict(v)['m'] for v in veriler]; o=[dict(v)['o'] for v in veriler]
                kisalt = lambda s: s[:9]+"…" if len(s)>10 else s
                fig, ax = plt.subplots(figsize=(7,3)); x=range(len(kats)); w=0.36
                
                ax.bar([i-w/2 for i in x],m,w,label='Müsait',color='#4FD1C5')
                ax.bar([i+w/2 for i in x],o,w,label='Ödünçte',color='#F6AD55')
                
                ax.set_xticks(list(x)); ax.set_xticklabels([kisalt(k) for k in kats],fontsize=8)
                ax.set_ylabel('Adet',fontsize=8, color='#4A5568'); ax.legend(fontsize=8)
                ax.set_title('Ekipman Kullanım Durumu',fontsize=10, color='#2C5282')
                ax.spines[['top','right']].set_visible(False); ax.yaxis.grid(True,alpha=0.3); plt.tight_layout(pad=0.5)
                buf=io.BytesIO(); fig.savefig(buf,format='png',dpi=120); plt.close(fig); buf.seek(0)
                h.append(Image(buf,width=14*cm,height=6*cm))
            h.append(Spacer(1,0.4*cm))
            h.append(Paragraph("Envanter Özeti", st['AltBaslik']))
            if veriler:
                rows=[["Kategori","Toplam","Müsait","Ödünçte","Doluluk %"]]
                for v in veriler:
                    d=dict(v); oran=f"%{round(d['o']*100/d['t'])}" if d['t'] else "%0"
                    rows.append([d['kategori'],str(d['t']),str(d['m']),str(d['o']),oran])
                h.append(Table(rows,repeatRows=1,colWidths=[6*cm,2.2*cm,2.2*cm,2.5*cm,2.5*cm],style=ts))
            h.append(Spacer(1,0.4*cm))
            h.append(Paragraph("En Çok Zimmetlenen Ekipmanlar", st['AltBaslik']))
            top=self.db.en_cok_zimmetlenen()
            if top:
                rows=[["Ekipman","Zimmet Sayısı","Toplam Adet"]]+[[dict(v)['isim'],str(dict(v)['say']),str(dict(v)['adet'])] for v in top]
                h.append(Table(rows,repeatRows=1,colWidths=[9*cm,4*cm,3*cm],style=ts))
            h.append(Spacer(1,0.4*cm))
            h.append(Paragraph("Aktif Zimmetler", st['AltBaslik']))
            aktif=self.db.aktif_zimmetler()
            if aktif:
                rows=[["Cihaz","Adet","Kullanıcı","Proje","Veriliş","İade"]]
                rows+=[[dict(v)['ekipman_isim'],str(dict(v)['adet']),dict(v)['kullanici_isim'],dict(v).get('proje_isim','-'),dict(v)['verilis_tarihi'],dict(v)['iade_tarihi']] for v in aktif]
                h.append(Table(rows,repeatRows=1,style=ts))
            else: h.append(Paragraph("Aktif zimmet kaydı bulunmamaktadır.", st['Kucuk']))
            doc.build(h)
            QMessageBox.information(self,"Başarılı","PDF raporu oluşturuldu.")
        except Exception as e: QMessageBox.critical(self,"Hata",str(e))

def _pdf(self):
        yol, _ = QFileDialog.getSaveFileName(self,"PDF Kaydet","lab_raporu.pdf","PDF (*.pdf)")
        if not yol: return
        try:
            doc = SimpleDocTemplate(yol, pagesize=pgsz.A4, topMargin=1.5*cm, bottomMargin=1.5*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)
            st = _pdf_stiller(); ts = _pdf_tablo_stili(); h = []
            h.append(Paragraph("BAUN Laboratuvar Takip Sistemi", st['Baslik']))
            h.append(Paragraph(f"Rapor Tarihi: {date.today().strftime('%d.%m.%Y')}", st['Kucuk']))
            h.append(Spacer(1, 0.5*cm))
            veriler = self.db.kategori_istatistik()
            if veriler:
                kats=[dict(v)['kategori'] for v in veriler]; m=[dict(v)['m'] for v in veriler]; o=[dict(v)['o'] for v in veriler]
                kisalt = lambda s: s[:9]+"…" if len(s)>10 else s
                fig, ax = plt.subplots(figsize=(7,3)); x=range(len(kats)); w=0.36
                
                ax.bar([i-w/2 for i in x],m,w,label='Müsait',color='#4FD1C5')
                ax.bar([i+w/2 for i in x],o,w,label='Ödünçte',color='#F6AD55')
                
                ax.set_xticks(list(x)); ax.set_xticklabels([kisalt(k) for k in kats],fontsize=8)
                ax.set_ylabel('Adet',fontsize=8, color='#4A5568'); ax.legend(fontsize=8)
                ax.set_title('Ekipman Kullanım Durumu',fontsize=10, color='#2C5282')
                ax.spines[['top','right']].set_visible(False); ax.yaxis.grid(True,alpha=0.3); plt.tight_layout(pad=0.5)
                buf=io.BytesIO(); fig.savefig(buf,format='png',dpi=120); plt.close(fig); buf.seek(0)
                h.append(Image(buf,width=14*cm,height=6*cm))
            h.append(Spacer(1,0.4*cm))
            h.append(Paragraph("Envanter Özeti", st['AltBaslik']))
            if veriler:
                rows=[["Kategori","Toplam","Müsait","Ödünçte","Doluluk %"]]
                for v in veriler:
                    d=dict(v); oran=f"%{round(d['o']*100/d['t'])}" if d['t'] else "%0"
                    rows.append([d['kategori'],str(d['t']),str(d['m']),str(d['o']),oran])
                h.append(Table(rows,repeatRows=1,colWidths=[6*cm,2.2*cm,2.2*cm,2.5*cm,2.5*cm],style=ts))
            h.append(Spacer(1,0.4*cm))
            h.append(Paragraph("En Çok Zimmetlenen Ekipmanlar", st['AltBaslik']))
            top=self.db.en_cok_zimmetlenen()
            if top:
                rows=[["Ekipman","Zimmet Sayısı","Toplam Adet"]]+[[dict(v)['isim'],str(dict(v)['say']),str(dict(v)['adet'])] for v in top]
                h.append(Table(rows,repeatRows=1,colWidths=[9*cm,4*cm,3*cm],style=ts))
            h.append(Spacer(1,0.4*cm))
            h.append(Paragraph("Aktif Zimmetler", st['AltBaslik']))
            aktif=self.db.aktif_zimmetler()
            if aktif:
                rows=[["Cihaz","Adet","Kullanıcı","Proje","Veriliş","İade"]]
                rows+=[[dict(v)['ekipman_isim'],str(dict(v)['adet']),dict(v)['kullanici_isim'],dict(v).get('proje_isim','-'),dict(v)['verilis_tarihi'],dict(v)['iade_tarihi']] for v in aktif]
                h.append(Table(rows,repeatRows=1,style=ts))
            else: h.append(Paragraph("Aktif zimmet kaydı bulunmamaktadır.", st['Kucuk']))
            doc.build(h)
            QMessageBox.information(self,"Başarılı","PDF raporu oluşturuldu.")
        except Exception as e: QMessageBox.critical(self,"Hata",str(e))

# ── ANA PENCERE ───────────────────────────────────────────────────────────────
class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__(); self.db = DB()
        self.setWindowTitle("BAUN Laboratuvar Takip Sistemi"); self.setGeometry(100,100,1100,680)
        self.setStyleSheet(get_stil(TEMALAR["yesil"])) 
        
        w = QWidget(); self.setCentralWidget(w)
        lay = QVBoxLayout(w); lay.setSpacing(12); lay.setContentsMargins(20,12,20,16)

        lay.addWidget(QLabel("🔬  <b>BAUN Laboratuvar Takip Sistemi</b>", styleSheet="font-size:18px;color:#276749;padding:0;margin:0;"))

        kart_lay = QHBoxLayout(); kart_lay.setSpacing(15); self.kart = {}
        kart_verileri = [
            ("ekipman", "Laboratuvar Envanteri", "📦", TEMALAR["mor"]),
            ("zimmet", "Aktif Zimmet Sayısı", "🔗", TEMALAR["mavi"])
        ]
        
        for key, baslik, ikon, t in kart_verileri:
            g = QGroupBox()
            g.setFixedHeight(95)
            g.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
            g.setStyleSheet(f"QGroupBox{{border:2px solid {t['hover']}; border-radius:12px; background:{t['acik']}; margin-top:0; padding:5px;}}")
            hl = QHBoxLayout(g); hl.setContentsMargins(10,5,10,5)
            ikon_lbl = QLabel(ikon); ikon_lbl.setStyleSheet("font-size:28px;"); ikon_lbl.setFixedWidth(44)
            sag = QVBoxLayout(); sag.setSpacing(0)
            baslik_lbl = QLabel(baslik); baslik_lbl.setStyleSheet(f"font-size:12px;color:{t['ana']};font-weight:bold;")
            sayi_lbl = QLabel("0"); sayi_lbl.setStyleSheet(f"font-size:26px;font-weight:bold;color:{t['ana']};")
            sag.addWidget(baslik_lbl); sag.addWidget(sayi_lbl)
            hl.addWidget(ikon_lbl); hl.addLayout(sag)
            self.kart[key] = sayi_lbl; kart_lay.addWidget(g)
        
        lay.addLayout(kart_lay)

        self.grafik_lbl = QLabel(); self.grafik_lbl.setAlignment(Qt.AlignCenter)
        self.grafik_lbl.setStyleSheet("background:#FFF;border:1px solid #9AE6B4;border-radius:12px;")
        self.grafik_lbl.setMinimumSize(300, 200)
        self.grafik_lbl.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding) 
        lay.addWidget(self.grafik_lbl, 1)

        MENU = [
            ("📦","Zimmet Ver", self._zimmet_ac, TEMALAR["mavi"]),
            ("📜","Geçmiş ve İade", self._gecmis_ac, TEMALAR["turuncu"]),
            ("🔧","Envanter", self._ekipman_ac, TEMALAR["mor"]),
            ("👤","Kullanıcılar", self._kullanici_ac, TEMALAR["kirmizi"]),
            ("📂","Projeler", self._proje_ac, TEMALAR["turkuaz"])
        ]
        
        menu = QGridLayout(); menu.setSpacing(12)
        for i, (ikon, metin, fn, tema) in enumerate(MENU):
            b = QPushButton(f"{ikon}\n{metin}"); b.setFixedHeight(85)
            b.setStyleSheet(f"QPushButton{{font-size:14px; font-weight:bold; padding:10px; border:2px solid {tema['hover']}; border-radius:12px; background:{tema['acik']}; color:{tema['ana']};}} QPushButton:hover{{background:#FFFFFF; border:2px solid {tema['ana']};}}")
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.clicked.connect(lambda checked=False, f=fn, t=tema: f(t))
            menu.addWidget(b, 0, i)
            
        lay.addLayout(menu)
        self._guncelle()

    def _grafik_ciz(self):
        veriler = self.db.kategori_istatistik()
        if not veriler or self.grafik_lbl.width() < 50 or self.grafik_lbl.height() < 50: return
        kats=[dict(v)['kategori'] for v in veriler]; musait=[dict(v)['m'] for v in veriler]; oduncte=[dict(v)['o'] for v in veriler]
        kisalt = lambda s: s[:9]+"…" if len(s)>10 else s
        
        w_px = self.grafik_lbl.width()
        h_px = self.grafik_lbl.height()
        w_inch = w_px / 100.0
        h_inch = h_px / 100.0
        
        fig, ax = plt.subplots(figsize=(w_inch, h_inch), dpi=100)
        fig.patch.set_facecolor('#FFF'); ax.set_facecolor('#FFF')
        
        x = range(len(kats))
        
        bw = min(0.38, 1.2 / max(len(kats), 1)) 
        
        ax.bar([i - bw/2 for i in x], musait, width=bw, label='Müsait', color='#68D391', zorder=3)
        ax.bar([i + bw/2 for i in x], oduncte, width=bw, label='Ödünçte', color='#63B3ED', zorder=3)
        
        ax.set_xticks(list(x)); ax.set_xticklabels([kisalt(k) for k in kats], fontsize=9)
        ax.set_ylabel('Adet', fontsize=9); ax.legend(fontsize=9, framealpha=0.7)
        ax.set_title('Kategori Bazlı Ekipman Durumu', fontsize=11, color='#276749', pad=6)
        ax.spines[['top','right']].set_visible(False); ax.yaxis.grid(True, alpha=0.3); ax.set_axisbelow(True)
        
        plt.tight_layout(pad=0.5)
        buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=100); plt.close(fig); buf.seek(0)
        
        pix = QPixmap.fromImage(QImage.fromData(buf.read()))
        self.grafik_lbl.setPixmap(pix)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._grafik_ciz()

    def showEvent(self, e): super().showEvent(e); QTimer.singleShot(50, self._grafik_ciz)

    def _guncelle(self):
        s = self.db.istatistik(); self.kart['ekipman'].setText(str(s['ekipman'])); self.kart['zimmet'].setText(str(s['zimmet']))
        self._grafik_ciz()

    def _zimmet_ac(self, tema): ZimmetVerPenceresi(self.db, tema).exec_(); self._guncelle()
    def _gecmis_ac(self, tema): GecmisPenceresi(self.db, tema).exec_(); self._guncelle()
    def _ekipman_ac(self, tema): EkipmanPencere(self.db, tema).exec_(); self._guncelle()
    def _kullanici_ac(self, tema): KullaniciPencere(self.db, tema).exec_(); self._guncelle()
    def _proje_ac(self, tema): ProjePencere(self.db, tema).exec_(); self._guncelle()

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    w = AnaPencere(); w.show(); sys.exit(app.exec_())
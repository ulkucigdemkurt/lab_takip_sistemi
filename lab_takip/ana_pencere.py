
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QPushButton, QSizePolicy
)
from db import DB
from tasarim import STIL_KODU
from ekipman_pencere import EkipmanPencere
from kullanici_pencere import KullaniciPencere
from proje_pencere import ProjePencere
from zimmet_pencereleri import ZimmetVerPenceresi, GecmisPenceresi

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

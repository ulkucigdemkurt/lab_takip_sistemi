
import os
import sqlite3
from datetime import date

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

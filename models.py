from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Hasta(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    ad_soyad = db.Column(db.String(120), nullable=False)
    yas = db.Column(db.Integer, nullable=False)
    sehir = db.Column(db.String(100))

    risk_skoru = db.Column(db.Integer, default=0)
    risk_seviyesi = db.Column(db.String(30))
    risk_rengi = db.Column(db.String(30))

    risk_yorumu = db.Column(db.Text)
    oneri = db.Column(db.Text)
    odak_alanlari = db.Column(db.String(200))
    analiz_notu = db.Column(db.Text)
    cevap_ozeti = db.Column(db.Text)

    maruziyet_puani = db.Column(db.Integer, default=0)
    belirti_puani = db.Column(db.Integer, default=0)
    kritik_puani = db.Column(db.Integer, default=0)
    korunma_puani = db.Column(db.Integer, default=0)

    tarih = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Hasta {self.ad_soyad}>"
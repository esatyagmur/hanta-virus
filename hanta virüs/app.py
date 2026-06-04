from flask import Flask, render_template, request, redirect, url_for
from models import db, Hasta
import os
import pandas as pd
import ast


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hanta_portal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

DATA_FILE = "hanta_data.csv"


SORULAR = [
    {
        "name": "kemirgen_gorme",
        "text": "Son 6 hafta içinde fare/sıçan gibi kemirgen gördünüz mü?",
        "category": "Maruziyet",
        "options": [
            ("0", "Hiç görmedim"),
            ("3", "Uzakta gördüm ama temas olmadı"),
            ("7", "Yaşam/çalışma alanımda gördüm"),
            ("10", "Aynı kapalı alanda uzun süre bulundum"),
        ],
    },
    {
        "name": "diski_idrar_temasi",
        "text": "Kemirgen dışkısı, idrarı, yuvası veya kemirilmiş eşya ile karşılaştınız mı?",
        "category": "Maruziyet",
        "options": [
            ("0", "Hayır, hiç karşılaşmadım"),
            ("4", "Gördüm ama dokunmadım"),
            ("8", "Temizlik sırasında yakın temas oldu"),
            ("12", "Eldivensiz/korumasız temas ettim"),
        ],
    },
    {
        "name": "tozlu_temizlik",
        "text": "Bodrum, depo, ahır, kulübe, garaj gibi kapalı ve tozlu bir alan temizlediniz mi?",
        "category": "Maruziyet",
        "options": [
            ("0", "Hayır"),
            ("3", "Kısa süre girdim"),
            ("7", "Süpürme/taşıma yaptım"),
            ("10", "Yoğun toz kalktı ve uzun süre kaldım"),
        ],
    },
    {
        "name": "havalandirma",
        "text": "Riskli alanı temizlemeden önce havalandırma yaptınız mı?",
        "category": "Korunma",
        "options": [
            ("8", "Hayır, doğrudan temizledim"),
            ("5", "Çok kısa havalandırdım"),
            ("2", "Bir süre havalandırdım"),
            ("0", "İyi havalandırdım ve tozu bastırdım"),
        ],
    },
    {
        "name": "maske_eldiven",
        "text": "Temizlik veya temas sırasında maske/eldiven kullandınız mı?",
        "category": "Korunma",
        "options": [
            ("8", "Hayır, korumasızdım"),
            ("5", "Sadece eldiven veya sadece maske vardı"),
            ("2", "Maske ve eldiven vardı ama kısa süreli kullandım"),
            ("0", "Uygun şekilde korundum"),
        ],
    },
    {
        "name": "kirsal_alan",
        "text": "Tarla, kamp, orman, odunluk, ahır veya hayvanların olduğu bir alana girdiniz mi?",
        "category": "Maruziyet",
        "options": [
            ("0", "Hayır"),
            ("2", "Kısa süre bulundum"),
            ("5", "Birkaç saat bulundum"),
            ("8", "Sık veya uzun süre bulundum"),
        ],
    },
    {
        "name": "yiyecek_depolama",
        "text": "Açıkta yiyecek, yem, tahıl veya kemirgen çekebilecek atık bulunan bir ortamda bulundunuz mu?",
        "category": "Maruziyet",
        "options": [
            ("0", "Hayır"),
            ("2", "Kısa süre"),
            ("5", "Belirgin şekilde vardı"),
            ("7", "Uzun süre aynı ortamdaydım"),
        ],
    },
    {
        "name": "ates",
        "text": "Son günlerde ateşiniz oldu mu?",
        "category": "Belirti",
        "options": [
            ("0", "Ateşim olmadı"),
            ("3", "Hafif ateş veya üşüme oldu"),
            ("7", "38°C ve üzeri ateş oldu"),
            ("10", "Yüksek ateş tekrarladı veya düşmedi"),
        ],
    },
    {
        "name": "kas_agrisi",
        "text": "Kas ağrısı, bel/sırt ağrısı veya belirgin halsizlik yaşadınız mı?",
        "category": "Belirti",
        "options": [
            ("0", "Hayır"),
            ("2", "Hafif"),
            ("6", "Belirgin"),
            ("9", "Günlük işleri zorlaştıracak kadar yoğun"),
        ],
    },
    {
        "name": "bas_agrisi",
        "text": "Baş ağrısı, baş dönmesi veya genel kırgınlık oldu mu?",
        "category": "Belirti",
        "options": [
            ("0", "Hayır"),
            ("2", "Hafif"),
            ("5", "Orta"),
            ("7", "Şiddetli veya sürekli"),
        ],
    },
    {
        "name": "mide_bulanti",
        "text": "Bulantı, kusma, karın ağrısı veya ishal gibi sindirim şikayetleri oldu mu?",
        "category": "Belirti",
        "options": [
            ("0", "Hayır"),
            ("2", "Hafif"),
            ("5", "Orta"),
            ("7", "Şiddetli veya tekrarlayan"),
        ],
    },
    {
        "name": "oksuruk",
        "text": "Öksürük veya göğüste baskı hissi var mı?",
        "category": "Belirti",
        "options": [
            ("0", "Hayır"),
            ("3", "Hafif öksürük"),
            ("7", "Belirgin öksürük veya göğüs baskısı"),
            ("10", "Giderek artıyor"),
        ],
    },
    {
        "name": "nefes_darligi",
        "text": "Nefes darlığı yaşıyor musunuz?",
        "category": "Kritik",
        "options": [
            ("0", "Hayır"),
            ("6", "Sadece eforla oluyor"),
            ("13", "Dinlenirken de hissediyorum"),
            ("18", "Belirgin ve kötüleşiyor"),
        ],
    },
    {
        "name": "hizli_kotulesme",
        "text": "Belirtiler kısa sürede kötüleşti mi?",
        "category": "Kritik",
        "options": [
            ("0", "Hayır, stabil"),
            ("3", "Yavaş arttı"),
            ("8", "Son 24-48 saatte belirgin arttı"),
            ("12", "Hızlı kötüleşme var"),
        ],
    },
    {
        "name": "temas_zamani",
        "text": "Riskli temas ne kadar zaman önce oldu?",
        "category": "Zaman",
        "options": [
            ("0", "Riskli temas hatırlamıyorum"),
            ("3", "Son 1 haftadan kısa"),
            ("7", "1-6 hafta arası"),
            ("5", "6 haftadan daha önce"),
        ],
    },
    {
        "name": "evde_kemirgen_izi",
        "text": "Evde veya iş yerinde kemirilmiş paket, yuva, dışkı ya da kötü koku gibi kemirgen izi var mı?",
        "category": "Maruziyet",
        "options": [
            ("0", "Yok"),
            ("3", "Şüpheli izler var"),
            ("7", "Net izler var"),
            ("10", "Sürekli tekrar ediyor"),
        ],
    },
    {
        "name": "olumlu_onlem",
        "text": "Kemirgen girişini önlemek için delik kapatma, yiyecek saklama, dezenfeksiyon gibi önlemler alındı mı?",
        "category": "Korunma",
        "options": [
            ("6", "Hayır, önlem alınmadı"),
            ("4", "Kısmen alındı"),
            ("1", "Büyük ölçüde alındı"),
            ("0", "Düzenli ve tam önlem var"),
        ],
    },
    {
        "name": "yas_riski",
        "text": "Yaş grubunuz veya kronik hastalık durumunuz hangisine daha yakın?",
        "category": "Kişisel",
        "options": [
            ("0", "60 yaş altı ve bilinen ek risk yok"),
            ("3", "60 yaş altı ama kronik hastalık var"),
            ("5", "60 yaş ve üzeri"),
            ("7", "60 yaş üzeri ve kronik hastalık var"),
        ],
    },
    {
        "name": "saglik_basvurusu",
        "text": "Bu şikayetler için sağlık kuruluşuna başvurdunuz mu?",
        "category": "Takip",
        "options": [
            ("4", "Hayır"),
            ("2", "Randevu aldım veya danışacağım"),
            ("0", "Başvurdum ve takipteyim"),
            ("1", "Acil değerlendirme önerildi"),
        ],
    },
    {
        "name": "genel_endise",
        "text": "Genel durumunuzu nasıl tarif edersiniz?",
        "category": "Takip",
        "options": [
            ("0", "İyi hissediyorum"),
            ("3", "Hafif rahatsızım"),
            ("7", "Belirgin hasta hissediyorum"),
            ("10", "Ciddi şekilde kötü hissediyorum"),
        ],
    },
]


def veri_yukle():
    if not os.path.exists(DATA_FILE):
        print("Uyarı: hanta_data.csv bulunamadı.")
        return None

    try:
        df = pd.read_csv(DATA_FILE, sep=None, engine="python", on_bad_lines="skip")
        print(f"Veri seti yüklendi: {len(df)} kayıt")
        return df
    except Exception as hata:
        print(f"Veri seti okunamadı: {hata}")
        return None


df_global = veri_yukle()


def veri_ozeti():
    if df_global is None or df_global.empty:
        return {
            "vaka": 0,
            "ulke": 0,
            "maruziyet": "Veri yok",
            "iyilesme": 0,
            "risk_yuksek": 0,
            "risk_orta": 0,
            "risk_dusuk": 0,
        }

    if "Outcome" in df_global.columns:
        iyilesme = round((df_global["Outcome"].astype(str) == "İyileşti").mean() * 100, 1)
    else:
        iyilesme = 0

    if "Country" in df_global.columns:
        ulke = int(df_global["Country"].nunique())
    else:
        ulke = 0

    if "Exposure_Type" in df_global.columns and not df_global["Exposure_Type"].mode().empty:
        maruziyet = df_global["Exposure_Type"].mode().iloc[0]
    else:
        maruziyet = "Veri yok"

    if "Risk_Level" in df_global.columns:
        risk_yuksek = int((df_global["Risk_Level"] == "Yüksek").sum())
        risk_orta = int((df_global["Risk_Level"] == "Orta").sum())
        risk_dusuk = int((df_global["Risk_Level"] == "Düşük").sum())
    else:
        risk_yuksek = 0
        risk_orta = 0
        risk_dusuk = 0

    return {
        "vaka": len(df_global),
        "ulke": ulke,
        "maruziyet": maruziyet,
        "iyilesme": iyilesme,
        "risk_yuksek": risk_yuksek,
        "risk_orta": risk_orta,
        "risk_dusuk": risk_dusuk,
    }


def yas_analizi(yas):
    if df_global is None or "Age" not in df_global.columns:
        return "Veri seti bulunamadığı için yaş grubu karşılaştırması yapılamadı."

    benzerler = df_global[
        (df_global["Age"] >= yas - 5) &
        (df_global["Age"] <= yas + 5)
    ]

    if benzerler.empty:
        return f"{yas - 5}-{yas + 5} yaş aralığında veri seti kaydı bulunamadı."

    fever = round(benzerler["Symptom_Fever"].mean() * 100, 1)
    breath = round(benzerler["Symptom_Shortness_of_Breath"].mean() * 100, 1)

    if "Risk_Level" in benzerler.columns and not benzerler["Risk_Level"].mode().empty:
        yaygin_risk = benzerler["Risk_Level"].mode().iloc[0]
    else:
        yaygin_risk = "bilinmiyor"

    return (
        f"Veri setinde {yas - 5}-{yas + 5} yaş aralığında {len(benzerler)} kayıt incelendi. "
        f"Bu grupta ateş oranı %{fever}, nefes darlığı oranı %{breath}, "
        f"en sık risk sınıfı: {yaygin_risk}."
    )


def analiz_yap(form):
    toplam = 0

    kategori = {
        "Maruziyet": 0,
        "Belirti": 0,
        "Kritik": 0,
        "Korunma": 0,
        "Zaman": 0,
        "Kişisel": 0,
        "Takip": 0,
    }

    cevaplar = []

    for soru in SORULAR:
        puan = int(form.get(soru["name"], 0))
        toplam += puan
        kategori[soru["category"]] += puan

        secilen_cevap = "Cevap yok"
        for deger, etiket in soru["options"]:
            if int(deger) == puan:
                secilen_cevap = etiket

        cevaplar.append({
            "soru": soru["text"],
            "kategori": soru["category"],
            "cevap": secilen_cevap,
            "puan": puan
        })

    skor = min(round((toplam / 183) * 100), 100)

    if kategori["Kritik"] >= 20 or skor >= 70:
        seviye = "Yüksek"
        renk = "danger"
        yorum = "Solunum bulguları, hızlı kötüleşme veya güçlü temas öyküsü nedeniyle risk yüksek görünüyor."
        oneri = "Bu sonuç tanı değildir; ancak sağlık kuruluşuna başvurmanız ve kemirgen teması öyküsünü belirtmeniz önerilir."
    elif skor >= 40:
        seviye = "Orta"
        renk = "warning"
        yorum = "Belirti ve temas yanıtları orta düzey risk gösteriyor. Durum yakından izlenmeli."
        oneri = "Belirtiler artarsa veya nefes darlığı gelişirse gecikmeden sağlık desteği alınmalıdır."
    else:
        seviye = "Düşük"
        renk = "success"
        yorum = "Yanıtlara göre risk düşük görünüyor."
        oneri = "Yeni belirti gelişirse testi tekrar doldurun ve gerekiyorsa sağlık danışmanlığı alın."

    en_yuksek = sorted(kategori.items(), key=lambda item: item[1], reverse=True)[:3]

    odak_listesi = []
    for ad, puan in en_yuksek:
        if puan > 0:
            odak_listesi.append(ad)

    if odak_listesi:
        odak = ", ".join(odak_listesi)
    else:
        odak = "Belirgin risk alanı yok"

    return skor, seviye, renk, yorum, oneri, odak, kategori, cevaplar


def cevaplari_coz(cevap_ozeti):
    try:
        return ast.literal_eval(cevap_ozeti)
    except Exception:
        return []


@app.route("/")
def index():
    return render_template("index.html", ozet=veri_ozeti())


@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "POST":
        ad_soyad = request.form.get("ad_soyad", "").strip()
        yas_raw = request.form.get("yas", "").strip()
        sehir = request.form.get("sehir", "").strip()

        if not ad_soyad or not yas_raw:
            return redirect(url_for("test"))

        yas = int(yas_raw)

        skor, seviye, renk, yorum, oneri, odak, kategori, cevaplar = analiz_yap(request.form)
        analiz_notu = yas_analizi(yas)

        hasta = Hasta(
            ad_soyad=ad_soyad,
            yas=yas,
            sehir=sehir,
            risk_skoru=skor,
            risk_seviyesi=seviye,
            risk_rengi=renk,
            risk_yorumu=yorum,
            oneri=oneri,
            odak_alanlari=odak,
            analiz_notu=analiz_notu,
            cevap_ozeti=str(cevaplar),
            maruziyet_puani=kategori["Maruziyet"],
            belirti_puani=kategori["Belirti"],
            kritik_puani=kategori["Kritik"],
            korunma_puani=kategori["Korunma"],
        )

        db.session.add(hasta)
        db.session.commit()

        return redirect(url_for("sonuc_detay", hasta_id=hasta.id))

    return render_template("test.html", sorular=SORULAR)


@app.route("/sonuclar")
def sonuclar():
    vakalar = Hasta.query.order_by(Hasta.id.desc()).all()
    return render_template(
        "sonuclar.html",
        vakalar=vakalar,
        secili=None,
        cevaplar=[]
    )


@app.route("/sonuclar/<int:hasta_id>")
def sonuc_detay(hasta_id):
    secili = Hasta.query.get_or_404(hasta_id)
    vakalar = Hasta.query.order_by(Hasta.id.desc()).all()
    cevaplar = cevaplari_coz(secili.cevap_ozeti)

    return render_template(
        "sonuclar.html",
        vakalar=vakalar,
        secili=secili,
        cevaplar=cevaplar
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    print("\nSistem başlatıldı")
    print("Ana sayfa: http://127.0.0.1:5000")
    print("Test: http://127.0.0.1:5000/test")
    print("Sonuçlar: http://127.0.0.1:5000/sonuclar\n")

    app.run(debug=True)
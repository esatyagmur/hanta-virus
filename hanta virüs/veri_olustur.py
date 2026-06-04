import csv
import random

random.seed(42)

countries_cities = [
    ("Türkiye", "İstanbul"),
    ("Türkiye", "Ankara"),
    ("Türkiye", "Bolu"),
    ("Türkiye", "Trabzon"),
    ("Türkiye", "Samsun"),
    ("Türkiye", "Erzurum"),
    ("Türkiye", "Kars"),
    ("Türkiye", "Rize"),
    ("ABD", "Colorado"),
    ("ABD", "New Mexico"),
    ("ABD", "Arizona"),
    ("Arjantin", "Buenos Aires"),
    ("Arjantin", "Salta"),
    ("Şili", "Santiago"),
    ("Brezilya", "Parana"),
    ("Güney Kore", "Seoul"),
    ("Çin", "Yunnan"),
    ("Almanya", "Berlin"),
    ("Fransa", "Lyon"),
    ("İsveç", "Umea"),
]

genders = ["Kadın", "Erkek"]
exposure_types = [
    "Kemirgen teması",
    "Kapalı alan temizliği",
    "Kırsal/hayvanlı alan",
    "Gıda deposu riski",
    "Belirgin temas yok"
]

outcomes = ["İyileşti", "Tedavi altında", "Takip önerildi", "Acil değerlendirme önerildi"]

headers = [
    "Age",
    "Gender",
    "Country",
    "City",
    "Symptom_Fever",
    "Symptom_Muscle_Pain",
    "Symptom_Headache",
    "Symptom_Nausea",
    "Symptom_Cough",
    "Symptom_Shortness_of_Breath",
    "Rodent_Seen",
    "Rodent_Droppings_Contact",
    "Dusty_Closed_Area",
    "Rural_Animal_Area",
    "Food_Storage_Risk",
    "Used_Mask_Gloves",
    "Ventilated_Before_Cleaning",
    "Exposure_Type",
    "Risk_Level",
    "Outcome"
]


def yes_by_probability(probability):
    return 1 if random.random() < probability else 0


def choose_risk(total_score):
    if total_score >= 70:
        return "Yüksek"
    if total_score >= 40:
        return "Orta"
    return "Düşük"


rows = []

for _ in range(1500):
    country, city = random.choice(countries_cities)
    age = random.randint(8, 88)
    gender = random.choice(genders)

    exposure_type = random.choices(
        exposure_types,
        weights=[24, 22, 22, 14, 18],
        k=1
    )[0]

    exposure_factor = {
        "Kemirgen teması": 0.72,
        "Kapalı alan temizliği": 0.62,
        "Kırsal/hayvanlı alan": 0.52,
        "Gıda deposu riski": 0.42,
        "Belirgin temas yok": 0.16
    }[exposure_type]

    rodent_seen = yes_by_probability(exposure_factor)
    droppings_contact = yes_by_probability(exposure_factor * 0.72)
    dusty_closed_area = yes_by_probability(exposure_factor * 0.68)
    rural_animal_area = yes_by_probability(exposure_factor * 0.65)
    food_storage_risk = yes_by_probability(exposure_factor * 0.50)

    used_mask_gloves = yes_by_probability(0.45)
    ventilated = yes_by_probability(0.52)

    symptom_base = 0.12 + (exposure_factor * 0.35)

    fever = yes_by_probability(symptom_base)
    muscle_pain = yes_by_probability(symptom_base + 0.06)
    headache = yes_by_probability(symptom_base + 0.04)
    nausea = yes_by_probability(symptom_base - 0.02)
    cough = yes_by_probability(symptom_base + 0.02)
    shortness_breath = yes_by_probability(symptom_base - 0.04)

    score = 0
    score += fever * 12
    score += muscle_pain * 10
    score += headache * 6
    score += nausea * 5
    score += cough * 8
    score += shortness_breath * 20
    score += rodent_seen * 10
    score += droppings_contact * 16
    score += dusty_closed_area * 12
    score += rural_animal_area * 8
    score += food_storage_risk * 7

    if used_mask_gloves == 0:
        score += 8

    if ventilated == 0:
        score += 7

    if age >= 60:
        score += 5

    risk_level = choose_risk(score)

    if risk_level == "Yüksek":
        outcome = random.choices(
            outcomes,
            weights=[18, 38, 18, 26],
            k=1
        )[0]
    elif risk_level == "Orta":
        outcome = random.choices(
            outcomes,
            weights=[34, 30, 28, 8],
            k=1
        )[0]
    else:
        outcome = random.choices(
            outcomes,
            weights=[58, 12, 28, 2],
            k=1
        )[0]

    rows.append([
        age,
        gender,
        country,
        city,
        fever,
        muscle_pain,
        headache,
        nausea,
        cough,
        shortness_breath,
        rodent_seen,
        droppings_contact,
        dusty_closed_area,
        rural_animal_area,
        food_storage_risk,
        used_mask_gloves,
        ventilated,
        exposure_type,
        risk_level,
        outcome
    ])

with open("hanta_data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)

print("hanta_data.csv başarıyla oluşturuldu.")
print(f"Toplam kayıt: {len(rows)}")
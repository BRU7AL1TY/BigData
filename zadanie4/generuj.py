import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

n = 1200

miasta = {
    "Warszawa":   (52.2297, 21.0122, 1.00),
    "Kraków":     (50.0647, 19.9450, 0.75),
    "Wrocław":    (51.1079, 17.0385, 0.65),
    "Poznań":     (52.4064, 16.9252, 0.55),
    "Gdańsk":     (54.3520, 18.6466, 0.55),
    "Łódź":       (51.7592, 19.4560, 0.50),
    "Katowice":   (50.2649, 19.0238, 0.45),
    "Lublin":     (51.2465, 22.5684, 0.30),
    "Białystok":  (53.1325, 23.1688, 0.25),
    "Szczecin":   (53.4285, 14.5528, 0.35),
}

gatunki = ["rock", "pop", "hip-hop", "electronic", "jazz",
           "classical", "folk", "metal", "indie", "reggae"]

typy_obiektow = ["klub", "arena", "stadion", "festiwal", "teatr", "amfiteatr"]
kapacjety = {
    "klub": (200, 1500), "arena": (3000, 15000), "stadion": (20000, 70000),
    "festiwal": (10000, 80000), "teatr": (400, 2000), "amfiteatr": (1500, 8000),
}
cena_bazowa = {
    "rock": 150, "pop": 200, "hip-hop": 180, "electronic": 160, "jazz": 130,
    "classical": 110, "folk": 90, "metal": 140, "indie": 100, "reggae": 110,
}
cena_mnoznik = {
    "klub": 0.7, "arena": 1.3, "stadion": 1.8,
    "festiwal": 1.5, "teatr": 1.2, "amfiteatr": 1.0,
}

start_date = datetime(2024, 1, 1)
daty = [start_date + timedelta(days=int(d)) for d in np.random.randint(0, 730, n)]

wagi = np.array([miasta[m][2] for m in miasta])
miasto = np.random.choice(list(miasta.keys()), n, p=wagi / wagi.sum())
gatunek = np.random.choice(gatunki, n)
typ_obiektu = np.random.choice(typy_obiektow, n,
                                p=[0.40, 0.15, 0.05, 0.10, 0.15, 0.15])

pojemnosc = np.array([np.random.randint(*kapacjety[t]) for t in typ_obiektu])
wypelnienie = np.clip(np.random.beta(5, 2, n), 0.15, 1.0)
sprzedane = (pojemnosc * wypelnienie).astype(int)

cena = np.array([cena_bazowa[g] * cena_mnoznik[t] for g, t in zip(gatunek, typ_obiektu)])
cena = np.round(cena * np.random.uniform(0.7, 1.4, n), -1)
przychod = (cena * sprzedane).astype(int)

df = pd.DataFrame({
    "event_id": range(50001, 50001 + n),
    "data": daty,
    "miasto": miasto,
    "latitude": [miasta[m][0] for m in miasto],
    "longitude": [miasta[m][1] for m in miasto],
    "gatunek": gatunek,
    "typ_obiektu": typ_obiektu,
    "pojemnosc": pojemnosc,
    "bilety_sprzedane": sprzedane,
    "cena_biletu_pln": cena,
    "przychod_pln": przychod,
})

df.to_csv("koncerty_polska.csv", index=False)
print(f"Wygenerowano plik 'koncerty_polska.csv' — {len(df)} koncertów")
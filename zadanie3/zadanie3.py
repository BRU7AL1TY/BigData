import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================================================
# Etap 0 - GENEROWANIE DANYCH (Uruchomienie skryptu z zadania)
# =====================================================================
np.random.seed(42)

n = 2000
dzielnice = ["Mokotów", "Wola", "Śródmieście", "Praga-Południe", "Ursynów",
             "Bemowo", "Białołęka", "Targówek", "Bielany", "Ochota", "Wilanów"]
multiplikator_dzielnicy = {
    "Mokotów": 1.15, "Wola": 1.10, "Śródmieście": 1.40, "Praga-Południe": 0.90,
    "Ursynów": 1.00, "Bemowo": 0.95, "Białołęka": 0.85, "Targówek": 0.88,
    "Bielany": 0.95, "Ochota": 1.05, "Wilanów": 1.20
}

dzielnica = np.random.choice(dzielnice, n)
metraz = np.clip(np.random.normal(55, 22, n), 18, 180)
pokoje = np.clip(np.round(metraz / 18 + np.random.normal(0, 0.5, n)), 1, 6).astype(int)
pietro = np.random.randint(0, 12, n)
rok_budowy = np.random.choice(
    list(range(1950, 2025)),
    n,
    p=np.linspace(0.5, 2, 75) / np.linspace(0.5, 2, 75).sum()
)
ma_balkon = np.random.choice([True, False], n, p=[0.75, 0.25])
ma_miejsce_parkingowe = np.random.choice([True, False], n, p=[0.45, 0.55])
odleglosc_od_centrum = np.clip(np.random.gamma(2.5, 2.5, n), 0.5, 25)

cena_za_m2 = (
    14000
    * np.array([multiplikator_dzielnicy[d] for d in dzielnica])
    * (1 + 0.005 * (rok_budowy - 1980))
    * (1 - 0.015 * odleglosc_od_centrum)
    * (1 + 0.05 * ma_balkon)
    * (1 + 0.08 * ma_miejsce_parkingowe)
    + np.random.normal(0, 1500, n)
)
cena = (cena_za_m2 * metraz).round(0)

df = pd.DataFrame({
    "id_oferty": range(10001, 10001 + n),
    "dzielnica": dzielnica,
    "metraz_m2": metraz.round(1),
    "liczba_pokoi": pokoje,
    "pietro": pietro,
    "rok_budowy": rok_budowy,
    "ma_balkon": ma_balkon,
    "ma_miejsce_parkingowe": ma_miejsce_parkingowe,
    "odleglosc_od_centrum_km": odleglosc_od_centrum.round(2),
    "cena_pln": cena
})

outlier_idx = np.random.choice(df.index, 30, replace=False)
df.loc[outlier_idx[:10], "cena_pln"] *= np.random.uniform(5, 12, 10)
df.loc[outlier_idx[10:20], "cena_pln"] *= np.random.uniform(0.05, 0.2, 10)
df.loc[outlier_idx[20:25], "metraz_m2"] = np.random.uniform(300, 600, 5)
df.loc[outlier_idx[25:30], "rok_budowy"] = np.random.choice([1800, 1850, 2050, 2099], 5)

df.to_csv("mieszkania_warszawa.csv", index=False)
print(f"Wygenerowano plik 'mieszkania_warszawa.csv' — {len(df)} ofert\n")


# =====================================================================
# Część 1 - Wstępna eksploracja
# =====================================================================
print("--- CZĘŚĆ 1: WSTĘPNA EKSPLORACJA ---")
df = pd.read_csv("mieszkania_warszawa.csv")

print(f"Kształt zbioru danych (shape): {df.shape}")
print("\nInformacje o zbiorze danych (info):")
df.info()
print("\nStatystyki opisowe (describe):")
print(df.describe())
print("\nLiczba brakujących wartości (isnull):")
print(df.isnull().sum())

print("""
Komentarz do wstępnej eksploracji:
W statystykach opisowych widać wyraźne błędy i outliery:
1. cena_pln: Maksymalna wartość to kilkanaście milionów złotych, a minimalna to kilkanaście tysięcy złotych za całe mieszkanie, co jest nierealne.
2. metraz_m2: Maksymalna wartość wynosi aż 596 m², co drastycznie odbiega od średniej (ok. 56 m²).
3. rok_budowy: Minimalny rok to 1800, a maksymalny to 2099 (rok z przyszłości).
""")


# =====================================================================
# Część 2 - Statystyki opisowe
# =====================================================================
print("\n--- CZĘŚĆ 2: STATYSTYKI OPISOWE ---")

# cena_pln
srednia_cena = df['cena_pln'].mean()
mediana_cena = df['cena_pln'].median()
std_cena = df['cena_pln'].std()
skew_cena = df['cena_pln'].skew()
kurt_cena = df['cena_pln'].kurt()

print(f"Cena PLN - Średnia: {srednia_cena:.2f}")
print(f"Cena PLN - Mediana: {mediana_cena:.2f}")
print(f"Cena PLN - Odchylenie std: {std_cena:.2f}")
print(f"Cena PLN - Skośność (skewness): {skew_cena:.2f}")
print(f"Cena PLN - Kurtoza (kurtosis): {kurt_cena:.2f}")

print("""
Komentarz do skośności ceny:
Wysoka, dodatnia skośność (skewness > 0) oznacza, że rozkład ma prawostronny (długi) ogon.
Większość mieszkań ma standardowe ceny, ale istnieje grupa ofert o ekstremalnie wysokich cenach.
""")

# metraz_m2
q1_metraz = df['metraz_m2'].quantile(0.25)
q3_metraz = df['metraz_m2'].quantile(0.75)
iqr_metraz = q3_metraz - q1_metraz
print(f"Metraż m2 - Q1: {q1_metraz:.2f}, Q3: {q3_metraz:.2f}, IQR: {iqr_metraz:.2f}")

# Dzielnice
print("\nLiczba unikalnych dzielnic:", df['dzielnica'].nunique())
print("Liczba ofert per dzielnica:")
print(df['dzielnica'].value_counts())


# =====================================================================
# Część 3 - Analiza pojedynczych zmiennych (Wizualizacja)
# =====================================================================
print("\n--- CZĘŚĆ 3: ANALIZA POJEDYNCZYCH ZMIENNYCH (WYKRESY) ---")

sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df['cena_pln'], kde=True, ax=axes[0], color='blue')
axes[0].set_title('Rozkład ceny (cena_pln)')
sns.histplot(df['metraz_m2'], kde=True, ax=axes[1], color='green')
axes[1].set_title('Rozkład metrażu (metraz_m2)')
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 4))
sns.boxplot(x=df['cena_pln'], color='orange')
plt.title('Boxplot ceny (cena_pln) - widoczne outliery po obu stronach')
plt.show()

plt.figure(figsize=(12, 5))
order_dzielnice = df['dzielnica'].value_counts().index
sns.countplot(data=df, x='dzielnica', order=order_dzielnice, hue='dzielnica', palette='viridis', legend=False)
plt.title('Liczba ofert w podziale na dzielnice')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# =====================================================================
# Część 4 - Analiza zależności
# =====================================================================
print("\n--- CZĘŚĆ 4: ANALIZA ZALEŻNOŚCI ---")

df_corr = df.copy()
df_corr["ma_balkon"] = df_corr["ma_balkon"].astype(int)
df_corr["ma_miejsce_parkingowe"] = df_corr["ma_miejsce_parkingowe"].astype(int)
macierz_kor = df_corr.select_dtypes(include="number").corr()

plt.figure(figsize=(10, 8))
sns.heatmap(macierz_kor, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
plt.title('Mapa korelacji zmiennych numerycznych')
plt.tight_layout()
plt.show()

print("Najsilniej z ceną (cena_pln) koreluje: metraz_m2 (oraz liczba_pokoi, która wynika z metrażu).")

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='metraz_m2', y='cena_pln', hue='dzielnica', alpha=0.7)
plt.title('Metraż vs Cena całkowita')
plt.tight_layout()
plt.show()

df["cena_pln_per_m2"] = df["cena_pln"] / df["metraz_m2"]

plt.figure(figsize=(12, 6))
order_cena_m2 = df.groupby('dzielnica')['cena_pln_per_m2'].median().sort_values(ascending=False).index
sns.boxplot(data=df, x='dzielnica', y='cena_pln_per_m2', order=order_cena_m2, hue='dzielnica', palette='Set2', legend=False)
plt.title('Cena za m² w podziale na dzielnice')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

najdrozsza_dzielnica = df.groupby('dzielnica')['cena_pln_per_m2'].median().idxmax()
print(f"Dzielnica o najwyższej medianie ceny za m2 to: {najdrozsza_dzielnica}")


# =====================================================================
# Część 5 - Detekcja outlierów
# =====================================================================
print("\n--- CZĘŚĆ 5: DETEKCJA OUTLIERÓW ---")

# 1. Metoda IQR dla ceny
q1_c = df['cena_pln'].quantile(0.25)
q3_c = df['cena_pln'].quantile(0.75)
iqr_c = q3_c - q1_c
outliers_iqr = df[(df['cena_pln'] < (q1_c - 1.5 * iqr_c)) | (df['cena_pln'] > (q3_c + 1.5 * iqr_c))]

# 2. Metoda Z-score dla ceny
z_scores = (df['cena_pln'] - df['cena_pln'].mean()) / df['cena_pln'].std()
outliers_z = df[abs(z_scores) > 3]

# 3. Metoda Modified Z-score dla ceny
median_c = df['cena_pln'].median()
mad_c = np.median(np.abs(df['cena_pln'] - median_c))
mod_z_scores = 0.6745 * (df['cena_pln'] - median_c) / mad_c
outliers_mod_z = df[abs(mod_z_scores) > 3.5]

print(f"Liczba outlierów (Cena) - Metoda IQR: {len(outliers_iqr)}")
print(f"Liczba outlierów (Cena) - Metoda Z-score: {len(outliers_z)}")
print(f"Liczba outlierów (Cena) - Metoda Modified Z-score: {len(outliers_mod_z)}")

# Outliery metrażu IQR + TOP 5
q1_m = df['metraz_m2'].quantile(0.25)
q3_m = df['metraz_m2'].quantile(0.75)
iqr_m = q3_m - q1_m
outliers_metraz = df[(df['metraz_m2'] < (q1_m - 1.5 * iqr_m)) | (df['metraz_m2'] > (q3_m + 1.5 * iqr_m))]
print(f"\nLiczba outlierów (Metraż) - Metoda IQR: {len(outliers_metraz)}")
print("Top 5 największych metraży:")
print(df['metraz_m2'].nlargest(5))

# Bzdurne lata budowy
bzdurne_lata = df[(df['rok_budowy'] < 1900) | (df['rok_budowy'] > 2026)]
print(f"\nLiczba wierszy z błędnym rokiem budowy: {len(bzdurne_lata)}")
print(bzdurne_lata[['id_oferty', 'rok_budowy']])


# =====================================================================
# Część 6 - Decyzja i czyszczenie
# =====================================================================
print("\n--- CZĘŚĆ 6: CZYSZCZENIE I TRANSFORMACJE ---")

# Usunięcie bzdurnych lat
df_clean = df[(df['rok_budowy'] >= 1900) & (df['rok_budowy'] <= 2026)].copy()

# Winsoryzacja (1 i 99 percentyl)
p1 = df_clean['cena_pln'].quantile(0.01)
p99 = df_clean['cena_pln'].quantile(0.99)
df_clean['cena_pln_capped'] = np.clip(df_clean['cena_pln'], p1, p99)

# Transformacja logarytmiczna
df_clean['cena_pln_log'] = np.log1p(df_clean['cena_pln'])

print(f"Skośność przed transformacją logarytmiczną: {df_clean['cena_pln'].skew():.2f}")
print(f"Skośność po transformacji logarytmicznej: {df_clean['cena_pln_log'].skew():.2f}")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df_clean['cena_pln'], kde=True, ax=axes[0], color='blue')
axes[0].set_title('Cena przed logarytmowaniem')
sns.histplot(df_clean['cena_pln_log'], kde=True, ax=axes[1], color='magenta')
axes[1].set_title('Cena po transformacji log1p (Rozkład zbliżony do normalnego)')
plt.tight_layout()
plt.show()

df_clean.to_csv("mieszkania_warszawa_clean.csv", index=False)


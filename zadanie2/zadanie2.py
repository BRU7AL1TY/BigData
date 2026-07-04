import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# ETAP 0: GENEROWANIE DANYCH
np.random.seed(42)

n = 500
klienci = ["Anna Kowalska", " Jan Nowak", "Anna Kowalska", "PIOTR WIŚNIEWSKI",
           "katarzyna lewandowska", "Tomasz Zieliński ", "Marta Wójcik",
           "anna kowalska ", "Krzysztof Kamiński", " Magdalena Dąbrowska"]
produkty = ["Laptop", "Mysz", "Klawiatura", "Monitor", "laptop", "MYSZ",
            "Słuchawki", "Pendrive", "monitor", "Webcam"]
kategorie = ["Elektronika", "elektronika", "ELEKTRONIKA", "Akcesoria",
             "akcesoria", "Akcesoria "]
miasta = ["Warszawa", "Kraków", "warszawa", "Gdańsk", "WROCŁAW",
          "Poznań", "Łódź ", " Warszawa", "kraków"]

start_date = datetime(2025, 1, 1)
daty_iso = [(start_date + timedelta(days=int(d))).strftime("%Y-%m-%d")
            for d in np.random.randint(0, 300, n // 2)]
daty_pl = [(start_date + timedelta(days=int(d))).strftime("%d.%m.%Y")
           for d in np.random.randint(0, 300, n // 2)]
daty = daty_iso + daty_pl
np.random.shuffle(daty)

df = pd.DataFrame({
    "order_id": range(1001, 1001 + n),
    "klient": np.random.choice(klienci, n),
    "produkt": np.random.choice(produkty, n),
    "kategoria": np.random.choice(kategorie, n),
    "miasto": np.random.choice(miasta, n),
    "ilosc": np.random.choice([1, 2, 3, 5, -1, 0], n, p=[0.5, 0.2, 0.15, 0.1, 0.025, 0.025]),
    "cena_jednostkowa": np.random.choice(
        ["199.99", "299,99", "1 499.00", "89.50", "2999", "399.00 zł", None, "abc"],
        n
    ),
    "data_zamowienia": daty,
    "email": np.random.choice(
        ["anna@gmail.com", "JAN@WP.PL", "piotr.w@onet", "marta@gmail.com",
         "tomasz@interia.pl", None, "krzysztof.k@gmail.com", "brak"],
        n
    )
})

# Wprowadzamy braki i duplikaty
for col in ["miasto", "kategoria", "data_zamowienia"]:
    df.loc[df.sample(frac=0.05, random_state=1).index, col] = np.nan

df = pd.concat([df, df.sample(20, random_state=2)], ignore_index=True)
df.to_csv("zamowienia_messy.csv", index=False)
print(f"Wygenerowano plik 'zamowienia_messy.csv' — {len(df)} wierszy\n")



# CZĘŚĆ 1: Eksploracja i identyfikacja problemów

print("--- CZĘŚĆ 1: EKSPLORACJA DANYCH ---")
df = pd.read_csv("zamowienia_messy.csv")

print("\nPodstawowe informacje (info):")
df.info()

print("\nLiczba braków danych (isnull):")
print(df.isnull().sum())

print("\n--- Zidentyfikowane problemy (Markdown / Komentarz) ---")
print("""
1. Duplikaty wierszy (sztucznie dodane na końcu skryptu generującego).
2. Niespójność wielkości liter i białe znaki (np. ' MYSZ', 'warszawa', 'Kraków').
3. Różne formaty dat (ISO 'YYYY-MM-DD' oraz polskie 'DD.MM.YYYY') przechowywane jako tekst.
4. Zanieczyszczone liczby w 'cena_jednostkowa' (np. '399.00 zł', spacje '1 499.00', przecinki zamiast kropek).
5. Brakujące wartości (NaN) w kluczowych kolumnach (miasto, kategoria, data).
6. Zamówienia z nielogiczną ilością sztuk (ujemne i zerowe ilości).
""")



# CZĘŚĆ 2: Czyszczenie

print("\n--- CZĘŚĆ 2: CZYSZCZENIE DANYCH ---")

# 1. Usunięcie duplikatów po unikalnym 'order_id'
df = df.drop_duplicates(subset=['order_id'])

# 2. Standaryzacja kolumn tekstowych
df['klient'] = df['klient'].astype(str).str.strip().str.title()
df['produkt'] = df['produkt'].astype(str).str.strip().str.title()
df['miasto'] = df['miasto'].astype(str).str.strip().str.title()
df['kategoria'] = df['kategoria'].astype(str).str.strip().str.lower()

# Zabezpieczenie przed zamianą rzeczywistych NaN na tekst 'Nan' przez astype(str)
df['miasto'] = df['miasto'].replace('Nan', np.nan)
df['kategoria'] = df['kategoria'].replace('nan', np.nan)

# 3. Konwersja daty do datetime (dayfirst=True pomoże przy polskich formatach z kropką)
df['data_zamowienia'] = pd.to_datetime(df['data_zamowienia'], format='mixed', dayfirst=True, errors='coerce')

# 4. Konwersja ceny jednostkowej do float
# Najpierw pozbywamy się " zł", spacji w tysiącach i zamieniamy przecinki na kropki
df['cena_jednostkowa'] = df['cena_jednostkowa'].astype(str)
df['cena_jednostkowa'] = df['cena_jednostkowa'].str.replace(' zł', '', regex=False)
df['cena_jednostkowa'] = df['cena_jednostkowa'].str.replace(' ', '', regex=False)
df['cena_jednostkowa'] = df['cena_jednostkowa'].str.replace(',', '.', regex=False)
df['cena_jednostkowa'] = pd.to_numeric(df['cena_jednostkowa'], errors='coerce')

# 5. Obsługa braków (NaN)
df = df.dropna(subset=['cena_jednostkowa', 'data_zamowienia'])
df['miasto'] = df['miasto'].fillna('unknown')
df['kategoria'] = df['kategoria'].fillna('unknown')
df['email'] = df['email'].fillna('brak_emaila')

# 6. Usunięcie zamówień o ilości <= 0
df = df[df['ilosc'] > 0]



# CZĘŚĆ 3: Transformacje

print("\n--- CZĘŚĆ 3: TRANSFORMACJE ---")

# 1. Wartość zamówienia
df['wartosc_zamowienia'] = df['ilosc'] * df['cena_jednostkowa']

# 2. Daty pochodne
df['rok'] = df['data_zamowienia'].dt.year
df['miesiac'] = df['data_zamowienia'].dt.month
df['nazwa_dnia'] = df['data_zamowienia'].dt.day_name()

# 3. Weryfikacja adresu email
# Szukamy czegoś w stylu: znak(i) @ znak(i) . znak(i)
wzorzec_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
df['email_poprawny'] = df['email'].str.contains(wzorzec_email, regex=True, na=False)



# CZĘŚĆ 4: Analiza SQL-style

print("\n--- CZĘŚĆ 4: ANALIZA WYNIKÓW ---")

# 1. Łączna wartość zamówień wg miesięcy
wartosc_miesiac = df.groupby('miesiac')['wartosc_zamowienia'].sum().reset_index()
print("\nŁączna wartość zamówień w poszczególnych miesiącach:")
print(wartosc_miesiac)

# 2. Top 5 klientów (wg wartości zamówień)
top_klienci = df.groupby('klient')['wartosc_zamowienia'].sum().nlargest(5).reset_index()
print("\nTop 5 klientów pod względem wartości zamówień:")
print(top_klienci)

# 3. Średnia wartość zamówienia wg kategorii
srednia_kategoria = df.groupby('kategoria')['wartosc_zamowienia'].mean().round(2).reset_index()
print("\nŚrednia wartość zamówienia w każdej kategorii:")
print(srednia_kategoria)



# CZĘŚĆ 5: Wizualizacja

plt.figure(figsize=(10, 6))
plt.bar(wartosc_miesiac['miesiac'].astype(str), wartosc_miesiac['wartosc_zamowienia'], color='royalblue', edgecolor='black')
plt.title('Łączna wartość zamówień w każdym miesiącu', fontsize=14)
plt.xlabel('Miesiąc', fontsize=12)
plt.ylabel('Łączna wartość zamówień (PLN)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()



# CZĘŚĆ 6: Zapis

df.to_csv('zamowienia_clean.csv', index=False, encoding='utf-8')
print("\n--- CZĘŚĆ 6: ZAPIS ---")
print("Oczyszczone dane zostały zapisane do pliku 'zamowienia_clean.csv'.")
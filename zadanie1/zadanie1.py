import requests
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# ==========================================
# Funkcje pomocnicze
# ==========================================
def get_currency(currencies_dict):
    if currencies_dict:
        return list(currencies_dict.keys())[0]
    return None

# ==========================================
# Część 1: Pozyskanie danych (API → DataFrame)
# ==========================================
print("--- Część 1: API -> DataFrame ---")

# System automatycznego przełączania serwerów.
# Jeśli oficjalne API zwróci błąd, skrypt płynnie przełączy się na serwer zapasowy.
urls = [
    "https://restcountries.com/v3.1/all",
    "https://studies.cs.helsinki.fi/restcountries/api/all"
]

data = None
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for url in urls:
    print(f"Łączenie z: {url} ...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            temp_data = response.json()
            
            # Twarde sprawdzenie: upewniamy się, że API zwróciło listę, a nie komunikat błędu
            if isinstance(temp_data, list) and len(temp_data) > 0:
                data = temp_data
                print("Sukces! Dane pobrane poprawnie.\n")
                break
            else:
                print("Odrzucono: Serwer zwrócił komunikat zamiast danych o krajach.")
        else:
            print(f"Odrzucono: Kod statusu {response.status_code}.")
    except Exception as e:
        print(f"Odrzucono: Problem z połączeniem ({e}).")

# Zabezpieczenie przed pustym DataFrame (to powodowało błąd bazy SQL)
if not data:
    print("\nKRYTYCZNY BŁĄD: Oba serwery API leżą lub blokują ruch. Spróbuj uruchomić skrypt za kilka minut.")
    exit()

# Parsowanie JSON do listy słowników
kraje_lista = []
for kraj in data:
    if not isinstance(kraj, dict):
        continue

    nazwa = kraj.get("name", {}).get("common", None)
    stolica = kraj.get("capital", [None])[0]
    region = kraj.get("region", None)
    subregion = kraj.get("subregion", None)
    populacja = kraj.get("population", None)
    powierzchnia = kraj.get("area", None)
    waluta = get_currency(kraj.get("currencies"))

    kraje_lista.append({
        "nazwa": nazwa,
        "stolica": stolica,
        "region": region,
        "subregion": subregion,
        "populacja": populacja,
        "powierzchnia": powierzchnia,
        "waluta": waluta
    })

# Konwersja do DataFrame
df = pd.DataFrame(kraje_lista)

print("Pierwsze 5 wierszy (head):")
print(df.head())
print(f"\nWymiary (shape): {df.shape}")
print("\nTypy danych (dtypes):")
print(df.dtypes)


# ==========================================
# Część 2: Zapis do bazy SQLite
# ==========================================
print("\n--- Część 2: Zapis do SQLite ---")
db_name = "kraje_swiata.db"
conn = sqlite3.connect(db_name)

df.to_sql("kraje", conn, if_exists="replace", index=False)
print(f"Dane zapisano pomyślnie do bazy {db_name} w tabeli 'kraje'.")


# ==========================================
# Część 3: Analiza SQL
# ==========================================
print("\n--- Część 3: Analiza SQL ---")

q1 = "SELECT SUM(populacja) AS calkowita_populacja FROM kraje"
print("\n1. Łączna populacja świata:")
print(pd.read_sql_query(q1, conn))

q2 = "SELECT nazwa, populacja FROM kraje ORDER BY populacja DESC LIMIT 10"
print("\n2. Top 10 krajów z największą populacją:")
print(pd.read_sql_query(q2, conn))

q3 = """
SELECT 
    region, 
    COUNT(*) AS liczba_krajow, 
    ROUND(AVG(populacja), 2) AS srednia_populacja
FROM kraje
WHERE region IS NOT NULL
GROUP BY region
ORDER BY liczba_krajow DESC
"""
print("\n3. Liczba krajów i średnia populacja wg regionów:")
print(pd.read_sql_query(q3, conn))

q4 = "SELECT nazwa, powierzchnia FROM kraje WHERE powierzchnia > 312679 ORDER BY powierzchnia DESC"
df_q4 = pd.read_sql_query(q4, conn)
print(f"\n4. Kraje o powierzchni większej niż Polska (Suma: {len(df_q4)}):")
print(df_q4.head(10)) 

q5 = """
SELECT 
    nazwa, 
    (populacja * 1.0 / powierzchnia) AS gestosc_zaludnienia
FROM kraje
WHERE powierzchnia > 0 AND populacja IS NOT NULL
ORDER BY gestosc_zaludnienia DESC
LIMIT 1
"""
print("\n5. Kraj o najwyższej gęstości zaludnienia:")
print(pd.read_sql_query(q5, conn))


# ==========================================
# Część 4: Wizualizacja
# ==========================================
print("\n--- Część 4: Wizualizacja ---")

q_plot = """
SELECT region, SUM(populacja) AS laczna_populacja
FROM kraje
WHERE region IS NOT NULL
GROUP BY region
ORDER BY laczna_populacja DESC
"""
df_plot = pd.read_sql_query(q_plot, conn)

plt.figure(figsize=(10, 6))
plt.bar(df_plot['region'], df_plot['laczna_populacja'], color='steelblue', edgecolor='black')

plt.title('Łączna populacja według regionów', fontsize=14, fontweight='bold')
plt.xlabel('Region', fontsize=12)
plt.ylabel('Populacja', fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

plt.show()
conn.close()
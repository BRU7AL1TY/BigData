import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Miejski Helpdesk Dashboard", layout="wide")

st.title("📊 Dashboard Zgłoszeń Miejskich (API)")
st.markdown("Analiza prawdziwych zgłoszeń serwisowych (np. awarie, hałas) pobieranych na żywo z publicznego API.")

@st.cache_data
def load_data():
    # Pobieranie 5000 najnowszych rozwiązanych zgłoszeń prosto z serwera
    url = "https://data.cityofnewyork.us/resource/erm2-nwe9.csv?$limit=5000&$where=closed_date IS NOT NULL"
    df = pd.read_csv(url, parse_dates=["created_date", "closed_date"])
    
    # Krok czyszczenia danych (punktowane w zadaniu)
    df = df.dropna(subset=["complaint_type", "status", "borough"])
    df = df[df["borough"] != "Unspecified"]
    
    # Tworzenie kolumn pochodnych
    df["Czas_rozwiazania_h"] = (df["closed_date"] - df["created_date"]).dt.total_seconds() / 3600
    df["Czas_rozwiazania_h"] = df["Czas_rozwiazania_h"].round(1)
    df = df[df["Czas_rozwiazania_h"] > 0] # Odrzucenie błędnych dat
    
    # Skrócenie daty do samego formatu RRRR-MM-DD na potrzeby wykresu
    df["Data"] = df["created_date"].dt.strftime('%Y-%m-%d')
    
    # Przetłumaczenie nazw kolumn na polski
    df = df.rename(columns={
        "complaint_type": "Kategoria",
        "status": "Status",
        "borough": "Dzielnica"
    })
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Nie udało się pobrać danych z API. Błąd: {e}")
    st.stop()

# Pasek boczny z filtrami (wymagane 3 sztuki)
st.sidebar.header("Filtruj dane")

wybrana_dzielnica = st.sidebar.selectbox(
    "Dzielnica",
    options=["Wszystkie"] + list(df["Dzielnica"].unique())
)

wybrane_kategorie = st.sidebar.multiselect(
    "Kategoria zgłoszenia",
    options=df["Kategoria"].unique(),
    default=list(df["Kategoria"].value_counts().head(5).index) # Domyślnie 5 najpopularniejszych
)

max_czas = st.sidebar.slider(
    "Maksymalny czas rozwiązania (h)",
    min_value=0,
    max_value=int(df["Czas_rozwiazania_h"].max()),
    value=int(df["Czas_rozwiazania_h"].max())
)

# Filtrowanie "w locie"
df_filtered = df.copy()
if wybrana_dzielnica != "Wszystkie":
    df_filtered = df_filtered[df_filtered["Dzielnica"] == wybrana_dzielnica]

df_filtered = df_filtered[
    (df_filtered["Kategoria"].isin(wybrane_kategorie)) & 
    (df_filtered["Czas_rozwiazania_h"] <= max_czas)
]

# Główne wskaźniki
col1, col2, col3 = st.columns(3)
col1.metric("Liczba wyświetlanych zgłoszeń", len(df_filtered))
col2.metric("Średni czas rozwiązania (h)", round(df_filtered["Czas_rozwiazania_h"].mean(), 1) if not df_filtered.empty else 0)
col3.metric("Liczba kategorii", df_filtered["Kategoria"].nunique())

st.divider()

if df_filtered.empty:
    st.warning("Brak danych dla wybranych filtrów. Zmień ustawienia w pasku bocznym.")
else:
    # Układ kolumnowy na wykresy (5 różnych typów)
    col_a, col_b = st.columns(2)

    with col_a:
        # 1. Wykres Liniowy
        df_trend = df_filtered.groupby("Data").size().reset_index(name="Liczba")
        fig1 = px.line(df_trend, x="Data", y="Liczba", title="Trend napływu zgłoszeń w dniach")
        st.plotly_chart(fig1, use_container_width=True)
        
        # 2. Histogram
        fig2 = px.histogram(df_filtered, x="Czas_rozwiazania_h", nbins=30, title="Rozkład czasu obsługi zgłoszeń")
        st.plotly_chart(fig2, use_container_width=True)

        # 3. Wykres Sunburst (Drzewiasty)
        fig3 = px.sunburst(df_filtered, path=["Dzielnica", "Kategoria"], title="Struktura zgłoszeń wg Dzielnicy i Kategorii")
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        # 4. Wykres Słupkowy
        df_kat = df_filtered.groupby("Kategoria").size().reset_index(name="Liczba").sort_values("Liczba", ascending=False)
        fig4 = px.bar(df_kat, x="Kategoria", y="Liczba", title="Najczęstsze kategorie problemów")
        st.plotly_chart(fig4, use_container_width=True)
        
        # 5. Wykres Pudełkowy (Boxplot)
        fig5 = px.box(df_filtered, x="Dzielnica", y="Czas_rozwiazania_h", color="Dzielnica", title="Czas obsługi z podziałem na dzielnice")
        st.plotly_chart(fig5, use_container_width=True)

st.caption("Dane pochodzą z oficjalnego, otwartego API miasta Nowy Jork (NYC 311 Service Requests).")
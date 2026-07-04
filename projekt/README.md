# Dashboard Zgłoszeń Miejskich (Nowy Jork)

Aplikacja analityczna zbudowana w Streamlit na zaliczenie przedmiotu. Pobiera na żywo dane z publicznego API miasta Nowy Jork (rejestr zgłoszeń 311) i wizualizuje czas oraz kategorie obsługiwanych incydentów.

## Funkcje
* Połączenie z prawdziwym REST API.
* Czyszczenie danych z błędnych dat i pustych wartości.
* Filtrowanie danych po dzielnicy, kategorii i czasie rozwiązania.
* 5 rodzajów wykresów interaktywnych.

## Jak uruchomić lokalnie
1. Pobierz repozytorium.
2. Zainstaluj paczki: `pip install -r requirements.txt`
3. Wpisz w terminalu: `streamlit run app.py`
# AI Robotics Investor 3.0 — wersja eksperymentalna

Aktualizacja istniejącej PWA z GitHub Pages. Uruchomienie: `python scanner.py`. GitHub Actions co 6 godzin uruchamia skaner i aktualizuje `data/scan.json`.

## Co robi
- Monitoruje 70+ spółek AI, robotyki, automatyki i infrastruktury.
- Pobiera wiadomości Google News RSS z sześciu zapytań.
- Próbuje odkrywać dodatkowych emitentów z rejestru tickerów SEC poprzez dopasowanie pełnej nazwy firmy do nagłówków.
- Pokazuje dowody źródłowe i wskaźnik uwagi; **nie** oblicza potencjału wzrostu ani wyceny.
- Nie wymaga płatnego API ani kluczy.

## Ograniczenia
Rejestr SEC nie zapewnia pełnego globalnego pokrycia. Dopasowanie nazw jest heurystyczne i może pomijać spółki lub dawać fałszywe trafienia. Nie należy traktować uwagi medialnej jako rankingu inwestycyjnego. Bez wiarygodnych cen, fundamentów, historii i walidacji nie ma jeszcze modelu oceny inwestycyjnej. Brak gwarancji ciągłości działania zewnętrznych źródeł.

## Instalacja
Użyj dołączonego importera Colab, aby zaktualizować pliki w istniejącym repozytorium; nie nadpisuj `.github/workflows/scan.yml`. Następnie uruchom workflow ręcznie.

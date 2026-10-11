# AI Robotics Investor 4.0 — etap fundamentalny

## Co działa
- Wersja 3.0: monitoring RSS, baza spółek, odkrycia SEC, obserwowane i notatki lokalne.
- Nowe: pobieranie danych z oficjalnego SEC EDGAR XBRL dla maksymalnie 8 emitentów w każdym skanie.
- Cache danych fundamentalnych w `data/scan.json`, kolejne skany rozszerzają pokrycie.
- Przychody, wzrost r/r, marża netto, OCF, FCF, gotówka i dług (jeśli dostępne).
- Prosty filtr kondycji finansowej 0-100 tylko przy kompletnych danych. To NIE ranking zakupu.
- Service Worker network-first dla HTML i skanu oraz czyszczenie starszych cache.

## Ograniczenia
Brak aktualnych notowań, kapitalizacji, wskaźników P/E i EV/FCF; nie ma wiarygodnej oceny atrakcyjności ceny ani prognozy wzrostu. Dane SEC historyczne, mogą być opóźnione i nie obejmują wszystkich spółek zagranicznych. Nie ma pełnego skanowania światowych giełd. Zdarzają się błędy dopasowania taksonomii XBRL. SEC może ograniczyć dostęp; błędy nie blokują całego skanu.

## Instalacja
Wgraj ZIP przez poprzedni importer Colab do istniejącego repozytorium. Importer pomija `.github/workflows/scan.yml`, który pozostaje niezmieniony i nadal uruchamia `python scanner.py`. Uruchom workflow ręcznie w Actions. Przed zmianami wyeksportuj obserwowane/notatki z aplikacji.

## Koszt
Kod bez płatnych API, GitHub Actions/Pages w ramach dostępnych limitów konta; brak gwarancji kosztu zerowego dla wszystkich konfiguracji.

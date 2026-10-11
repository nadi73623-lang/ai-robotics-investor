# AI Robotics Investor 4.1.1 — naprawa notowań

Naprawiono wyjątek `KeyError: Close` przy niepoprawnym CSV Stooq. Skrypt waliduje nagłówki, wartości, walutę (Yahoo), datę (maksymalnie 7 dni) i przełącza się na drugi dostawca: publiczny endpoint Yahoo Finance Chart. Wyniki nie są notowaniami live. Źródła mogą ograniczać dostęp, zmieniać format lub zasady użycia. Dane nie są gwarantowane.

`price_health` w `data/scan.json` pokazuje `status`, `attempted`, `updated` i diagnostykę tickerów. Log GitHub Actions pokazuje `PRICE_SUMMARY` i `QUOTE_FAIL` (bez danych uwierzytelniających). AVGO jest sprawdzane w każdym skanie. Brak wiarygodnej ceny nie jest zastępowany fikcyjną liczbą.

Zachowano istniejący `.github/workflows/scan.yml`, bez dodatkowych bibliotek i płatnych API. GitHub Actions nadal uruchamia `python scanner.py`.

Testy: `python -m unittest discover -p 'test_*.py'`. Po wdrożeniu uruchom ręcznie skan i sprawdź `PRICE_SUMMARY`, a następnie cenę AVGO. Zielony workflow nie oznacza sukcesu dostawcy.

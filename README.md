# AI Robotics Investor 4.1 — notowania EOD i ochrona danych

## Nowe
- Opcjonalne, **opóźnione** ceny zamknięcia z publicznego CSV Stooq dla wybranych tickerów USA, do 12 na skan. Błędy dostawcy nie blokują skanera.
- Odrzucanie cen starszych niż 7 dni, data i źródło przy każdym notowaniu.
- Licznik pokrycia cenowego; brak notowania nie jest traktowany jak zero.
- Eksport **wszystkich** notatek (nie tylko obserwowanych spółek).
- Wersjonowanie pamięci offline PWA 4.1.

## Ważne ograniczenia
Ceny nie są notowaniami na żywo, Stooq może zmienić lub ograniczyć dostęp, ticker zagraniczny/ADR może nie pasować do kodu Stooq. Dane nie są gwarantowane; bez wiarygodnej kapitalizacji, rozwodnionej liczby akcji i cen nie wyliczamy P/E, P/S ani ceny docelowej. Wynik uwagi i filtr kondycji NIE są rankingiem zakupowym. Pokrycie SEC i odkrycia nadal nie obejmują całego rynku.

## Wdrożenie
Wgraj ZIP przez importer Colab 4.0, który pomija `.github/workflows/scan.yml`. Nie usuwaj aplikacji ani danych lokalnych. Przed aktualizacją wyeksportuj notatki. Uruchom workflow ręcznie; w danych JSON sprawdź `price_coverage`, a w aplikacji daty cen. Jeśli `price_coverage` = 0, nie traktuj tego jako sukcesu pobierania notowań.

## Koszt
Bez płatnych API; GitHub Actions i Pages zależą od limitów konta.

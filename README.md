# AI Robotics Investor 4.2 — wycena orientacyjna

Rozszerzenie wersji 4.1.1 bez nowych bibliotek i bez zmiany GitHub Actions. `scanner.py` działa przez `python scanner.py`.

## Zmiany
- SEC companyfacts: liczba akcji i daty okresów dla przychodów, zysku netto, cash flow i nakładów.
- Wycena orientacyjna: kapitalizacja (cena EOD × historyczna liczba akcji), roczny P/S, roczny P/E wyłącznie przy dodatnim zysku, roczna rentowność FCF. Nie TTM i nie dane live.
- Brak wskaźnika przy brakujących, zbyt starych lub nieporównywalnych danych; wybrane zagraniczne ADR pomijane z uwagi na różne jednostki akcji.
- `VALUATION_SUMMARY` w logach i `valuation_coverage` w JSON. Dane SEC będą się stopniowo uzupełniać, maks. 8 emitentów na skan.
- UI wyraźnie odróżnia orientacyjne mnożniki od rankingu inwestycyjnego.

## Ograniczenia
Wynik może być niedokładny po emisjach, splitach i wykupach akcji, gdy liczba akcji SEC jest starsza od notowania. Dodatkowo różne daty raportów i okresy roczne ograniczają porównywalność. Nie jest to profesjonalny feed kapitalizacji ani rekomendacja inwestycyjna. Nie wyliczamy rankingu zakupowego z niekompletnych danych.

## Test
`python -m unittest discover -p 'test_*.py'`. W GitHub Actions uruchom skan, a następnie sprawdź `VALUATION_SUMMARY` i wycenę AVGO w aplikacji. Brak wyceny AVGO po pierwszym skanie nie musi oznaczać awarii, ponieważ dane SEC są uzupełniane rotacyjnie.

# AI Robotics Investor 4.2.2 — rozszerzenie pokrycia

Aktualizacja istniejącego repozytorium. Nie zmienia `.github/workflows/scan.yml`, struktury danych użytkownika ani źródeł płatnych.

- SEC: do 16 emitentów na skan (wcześniej 8); pierwszeństwo brakujących danych i liczby akcji, okresowy powrót do danych starszych.
- Ceny: do 24 tickerów na skan (wcześniej 12); pierwszeństwo spółek bez notowania i AVGO.
- Log: `SEC_BATCH_SUMMARY`, `PRICE_SUMMARY`, `VALUATION_SUMMARY`.
- Wyceny nadal wyłącznie orientacyjne, bez domyślania się brakujących danych.

Uwaga: wzrost pokrycia nie jest gwarantowany; Stooq/Yahoo i SEC mogą ograniczać dostęp, a spółki zagraniczne mogą wymagać innych źródeł. Przy harmonogramie co 6 godzin limit nie oznacza równoległych żądań.

Import: dotychczasowy notebook Colab 4.1, ZIP 4.2.2, token fine-grained Contents read/write wyłącznie dla repozytorium; unieważnij po imporcie.

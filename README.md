# AI Robotics Investor 2.0 — PWA + automatyczny skaner

## Co jest gotowe
- Polska mobilna aplikacja PWA: dashboard, lista spółek, filtrowanie, wiadomości, obserwowane, notatki i eksport.
- Skaner wiadomości RSS obejmujący **48** spółek AI, robotyki, półprzewodników i infrastruktury (sprawdź bieżącą liczbę w aplikacji).
- Automatyczne uruchamianie przez GitHub Actions co 6 godzin (harmonogram GitHub jest orientacyjny, może być opóźniany lub wyłączony).
- Zapisywanie wyniku jako `data/scan.json`, wyświetlanie daty ostatniego udanego skanu.
- Nie wymaga klucza API ani płatnego hostingu przy publicznym repozytorium i limitach darmowych usług.

## Uruchomienie na samym telefonie (Chrome na Androidzie)
1. Załóż bezpłatne konto na https://github.com (jeśli go nie masz).
2. Utwórz **publiczne** repozytorium `ai-robotics-investor`.
3. W przeglądarce telefonu otwórz repozytorium, wybierz `Add file` → `Upload files`. Wgraj zawartość ZIP **z zachowaniem struktury folderów**. Interfejs GitHub na telefonie może wymagać włączenia „Wersja na komputer” i może utrudniać upload folderów. Alternatywnie skorzystaj z mobilnego edytora repozytorium GitHub (github.dev) lub importu repozytorium przez usługę Git.
4. W `Settings` → `Pages` wybierz `Deploy from a branch`, gałąź `main`, katalog `/ (root)` i zapisz.
5. W `Actions` otwórz `AI Robotics market scan`, kliknij `Run workflow` (jeśli Actions wymaga zezwolenia, zezwól). Sprawdź wynik uruchomienia.
6. Otwórz `https://TWOJ_LOGIN.github.io/ai-robotics-investor/` (adres zależy od nazwy repozytorium).
7. W Chrome wybierz menu `⋮` → `Dodaj do ekranu głównego` / `Zainstaluj aplikację`.

## Koszt
Może wynosić 0 zł/mies. przy darmowym publicznym GitHub Pages i Actions, w ramach obowiązujących limitów. Dostępność i regulaminy usług mogą się zmieniać.

## Ważne ograniczenia
- Nie jest to model AI oceniający potencjał inwestycyjny. To **pierwszy działający etap zbierania informacji i odkrywania kandydatów**. Nie należy interpretować liczby wzmianek jako oceny jakości inwestycji.
- Nie pobiera notowań, nie oblicza wartości godziwej, nie wysyła push i nie korzysta z płatnego modelu AI.
- Publiczne wiadomości RSS mogą być niekompletne, opóźnione, blokowane albo zwracać zero wyników.
- Lista spółek jest szeroka, ale nie obejmuje wszystkich notowanych firm. Wykrywanie nowych nazw jest ograniczone do wstępnej listy kandydatów i wymaga weryfikacji statusu giełdowego.
- Nie ma synchronizacji z historią rozmów ChatGPT.
- Lokalna lista obserwowanych i notatki mogą zniknąć po wyczyszczeniu danych przeglądarki.
- GitHub może wyłączać harmonogramy w nieaktywnych repozytoriach; trzeba okresowo kontrolować datę ostatniego skanu.

## Rozwój
Aby spełnić docelowe założenia: dodać wiarygodny dostawca cen i fundamentów, raporty SEC/IR, automatyczne poszerzanie uniwersum z walidacją tickerów, model AI do oceny jakości i wyceny, archiwizację ocen oraz powiadomienia push. Klucze API trzymać tylko w GitHub Actions Secrets, nigdy w plikach publicznej aplikacji.

# ISS — symulacja zbiornika

Projekt laboratoryjny w Pythonie: poziom cieczy w zbiorniku o stałym przekroju, stały dopływ i odpływ swobodny. Wykresy Plotly, interfejs Dash uruchamiany w przeglądarce. Wszystkie suwaki działają wspólnie. PyCharm nie jest wymagany.

## Uruchomienie

Python 3.10 lub nowszy. Otwórz terminal w katalogu projektu.

Windows (PowerShell lub CMD):

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
```

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Otwórz **http://127.0.0.1:8050**. Serwer musi pozostać uruchomiony; zatrzymanie: Ctrl+C. Internet jest potrzebny do instalacji zależności. Repozytorium zawiera kod, a nie automatycznie wdrożoną usługę WWW.

## Zadanie i model

Bilans objętości: `A · dh/dt = Q_doplyw − Q_odplyw`.

Odpływ: `Q_odplyw(n) = beta · sqrt(h(n))`.

Rekurencja (jawny Euler):

```text
h(n+1) = h(n) + (Tp/A) · (Q_doplyw − beta · sqrt(h(n)))
h(0) = current_h
```

To zależność rekurencyjna wykonywana w pętli, bez wywołań rekurencyjnych funkcji. Model jest symulacją; poziom nie pochodzi z czujnika. Dopływ zmieniony suwakiem jest stały przez całą nową symulację. Przesunięcie suwaka przelicza przebieg od czasu 0, nie zmienia zaworu w trakcie jednej symulacji.

| Zmienna | Wartość początkowa | Znaczenie i jednostka |
|---|---:|---|
| A | 1.5 | Pole przekroju, m² |
| beta | 0.035 | Współczynnik wypływu, m^(5/2)/s |
| current_h | 0.0 | Początkowy poziom, m |
| Q_doplyw | 0.075 | Dopływ, m³/s (75 l/s) |
| h_min / h_max | 0 / 5 | Granice poziomu, m |
| Tp | 0.1 | Krok czasu, s |
| t_sim | 3600 | Czas symulacji, s |

Liczba kroków: `3600/0.1 = 36000`. Razem ze stanem początkowym listy `t` i `h` mają **36001 elementów**. Funkcja `max(h)` znajduje najwyższy poziom; `len(h)` liczbę wyników. Mnożenie wysokości w metrach przez 100 daje centymetry.

Dla wartości początkowych poziom rośnie od 0 do około **4.5918 m = 459.18 cm**. W równowadze dopływ jest równy odpływowi: `h* = (Q_doplyw/beta)²`. A zmienia szybkość dochodzenia do równowagi, ale nie tę wartość. Start z 5 m daje przebieg malejący do tej samej równowagi. Dla beta=0 odpływ jest zerowy: dodatni dopływ napełnia zbiornik, zerowy dopływ zachowuje poziom.

## Granice i uproszczenia

Poziom ograniczamy do przedziału 0–5 m. Przy górnej granicy nadmiar interpretowany jest jako przelew; CSV zawiera średni przelew w następnym kroku, w ostatnim wierszu 0 (brak następnego kroku). Odpływ Qo jest obliczany na początku kroku. Przy opróżnianiu Euler może zaproponować poziom ujemny, więc stosujemy dolną granicę 0. To zabezpieczenie numeryczne, nie dokładne rozwiązanie czasu opróżnienia wewnątrz kroku. Stały krok 0.1 s służy do tego zadania; model nie jest uniwersalnym rozwiązaniem dla dowolnie dużych kroków i parametrów.

Brak regulatora P/PID: obecny model opisuje obiekt sterowania. Nie modelujemy ciśnienia zewnętrznego, dynamiki zaworu ani zmiennego przekroju.

## Obsługa i eksport

- Cztery suwaki: A, beta, dopływ i poziom początkowy. Obliczenie po puszczeniu suwaka.
- Wykres poziomu oraz osobny wykres dopływu, odpływu i ewentualnego przelewu.
- Maksimum w cm, poziom końcowy, liczba wyników i teoretyczna równowaga.
- Reset wszystkich parametrów.
- Przycisk CSV zapisuje wszystkie punkty bieżącej symulacji.
- Pasek Plotly pozwala przybliżać, przesuwać, pobrać obraz i resetować widok.

Samodzielny raport HTML i CSV dla ustawień początkowych:

```bash
python export.py
```

Pliki w `exports/`. HTML zawiera Plotly i działa bez serwera i bez internetu; ma interaktywne przybliżanie i odczyt punktów, ale nie suwaki przeliczające model.

## Struktura i rozbudowa

- `model.py` — parametry, walidacja, obliczenia; niezależny od interfejsu.
- `app.py` — suwaki, callbacki, wykresy i eksport CSV.
- `assets/style.css` — wygląd.
- `export.py` — raport offline.
- `tests/test_model.py` — równowaga, opróżnianie, przelew, dane i interfejs HTTP.

Możliwa rozbudowa: osobny moduł regulatorów P/PI/PID, zmienny w czasie dopływ, zakłócenia i porównanie odpowiedzi. Tempomat powinien dostać osobny model prędkości samochodu; można wykorzystać tę samą strukturę aplikacji i wykresów. Dokładnych wymagań następnego zadania nie zakładamy.

Testy:

```bash
python -m unittest discover -s tests -v
```

## Publikacja kodu na GitHub

Utwórz puste **publiczne** repo `iss-tank-simulator` (bez README, licencji i .gitignore, bo pliki już są tutaj). W katalogu projektu:

```bash
git init -b main
git add .
git commit -m "Add tank simulation with Plotly and Dash"
git remote add origin https://github.com/pepolx/iss-tank-simulator.git
git push -u origin main
```

Logowanie do GitHub odbywa się standardowo przez Git; nie zapisuj tokenów w kodzie. Publiczne repo udostępnia kod. Dash wymaga działającego procesu Python i nie działa jako aplikacja Python na samym GitHub Pages.

## Dokumentacja bibliotek

- [Dash: callbacki i wspólna aktualizacja parametrów](https://dash.plotly.com/basic-callbacks)
- [Dash: Slider](https://dash.plotly.com/dash-core-components/slider)
- [Plotly: wykresy liniowe](https://plotly.com/python/line-charts/)

Opracowanie równania na podstawie slajdów przekazanych na zajęciach. Projekt nie dołącza zdjęć ani materiałów prowadzącego.

# Symulacja zbiornika — ISS

Python, Plotly i Dash. Cztery suwaki: pole przekroju, beta, dopływ i początkowy poziom wody. Jeden wykres poziomu w czasie. Pod wykresem maksimum w centymetrach i liczba wyników. Cały program jest w `app.py`.

## Uruchomienie w PowerShell

Pierwsze pobranie:

```powershell
git clone https://github.com/pepolx/iss-tank-simulator.git
cd iss-tank-simulator
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Otwórz http://127.0.0.1:8050 w przeglądarce. PowerShell zostaw otwarty. Zatrzymanie: Ctrl+C. Wymagany Python 3.10 lub nowszy.

Jeśli masz już pobrany projekt, przejdź w PowerShell do jego folderu. Zatrzymaj aplikację przez Ctrl+C, pobierz zmiany i uruchom ponownie:

```powershell
git pull
.\.venv\Scripts\python.exe app.py
```

## Obliczenia

```text
Q_odplyw = beta * sqrt(h)
h(n+1) = h(n) + (Tp / A) * (Q_doplyw - Q_odplyw)
```

A = 1.5 m², beta = 0.035 m^(5/2)/s, dopływ = 0.075 m³/s, poziom początkowy = 0 m. Krok Tp = 0.1 s, czas symulacji = 3600 s, granice poziomu = 0–5 m.

Lista `h` zawiera 36001 wyników: stan początkowy i 36000 kolejnych kroków. `max(h)` to najwyższy poziom, `len(h)` to liczba wyników. Metry mnożymy przez 100, aby dostać centymetry.

Dla ustawień początkowych poziom dąży do około 4.5918 m (459.18 cm). Powyżej tej wartości odpływ przewyższa dopływ, więc poziom maleje. Zwiększenie A spowalnia zmiany. Suwaki przeliczają cały przebieg od początku; w jednym przebiegu dopływ jest stały. Regulatora P/PID jeszcze nie ma.

Poziom obliczamy metodą Eulera i ograniczamy do 0–5 m. Górne ograniczenie upraszcza przepełnienie zbiornika, a dolne zabezpiecza przed ujemnym wynikiem przy opróżnianiu.

## Testy

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

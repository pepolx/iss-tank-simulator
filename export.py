"""Samodzielny raport HTML (bez suwaków) i pełne dane CSV."""
from pathlib import Path
from app import DEFAULT, csv_wynikow, wykres
from model import symulacja

if __name__ == '__main__':
    destination = Path('exports')
    destination.mkdir(exist_ok=True)
    wykres(DEFAULT, symulacja(DEFAULT)).write_html(destination / 'zbiornik.html', include_plotlyjs=True)
    (destination / 'wyniki_zbiornika.csv').write_text(csv_wynikow(DEFAULT), encoding='utf-8')
    print('Zapisano exports/zbiornik.html oraz exports/wyniki_zbiornika.csv')

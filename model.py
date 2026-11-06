"""Model zbiornika: bilans objętości, odpływ swobodny, Euler jawny."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Parametry:
    A: float = 1.5
    beta: float = 0.035
    current_h: float = 0.0
    h_min: float = 0.0
    h_max: float = 5.0
    Q_doplyw: float = 0.075
    Tp: float = 0.1
    t_sim: float = 3600.0

    def sprawdz(self):
        if not all(math.isfinite(v) for v in vars(self).values()):
            raise ValueError("Parametry muszą być skończonymi liczbami.")
        if self.A <= 0 or self.Tp <= 0 or self.t_sim <= 0:
            raise ValueError("A, Tp i t_sim muszą być dodatnie.")
        if self.beta < 0 or self.Q_doplyw < 0:
            raise ValueError("Beta i dopływ nie mogą być ujemne.")
        if self.h_min != 0 or not 0 <= self.current_h <= self.h_max or self.h_max <= 0:
            raise ValueError("Wymagane: h_min = 0 oraz 0 ≤ current_h ≤ h_max.")
        kroki = self.t_sim / self.Tp
        if not math.isclose(kroki, round(kroki), abs_tol=1e-8, rel_tol=0):
            raise ValueError("t_sim musi być wielokrotnością Tp.")
        if kroki > 200_000:
            raise ValueError("Maksymalnie 200000 kroków symulacji.")


@dataclass
class Wyniki:
    t: list[float]
    h: list[float]
    Q_odplyw: list[float]
    Q_przelew: list[float]


def symulacja(p: Parametry = Parametry()) -> Wyniki:
    p.sprawdz()
    t, h, odplyw, przelew = [], [], [], []
    current_h = p.current_h
    liczba_krokow = round(p.t_sim / p.Tp)

    for n in range(liczba_krokow + 1):
        Q_odplyw = p.beta * math.sqrt(current_h)
        # Dla ostatniego punktu nie ma już następnego przedziału czasu.
        next_h = current_h + (p.Tp / p.A) * (p.Q_doplyw - Q_odplyw)
        Q_przelew = max(0.0, next_h - p.h_max) * p.A / p.Tp if n < liczba_krokow else 0.0
        t.append(n * p.Tp)
        h.append(current_h)
        odplyw.append(Q_odplyw)
        przelew.append(Q_przelew)
        if n == liczba_krokow:
            break
        current_h = min(p.h_max, max(p.h_min, next_h))

    return Wyniki(t, h, odplyw, przelew)


def poziom_rownowagi(p: Parametry) -> float | None:
    """Równowaga bez ograniczenia wysokością zbiornika."""
    if p.beta == 0:
        return None
    return (p.Q_doplyw / p.beta) ** 2

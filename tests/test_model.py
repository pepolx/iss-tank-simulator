import csv
import io
import math
import unittest
from dataclasses import replace

from model import Parametry, symulacja, poziom_rownowagi
from app import app, aktualizuj, csv_wynikow, reset


class ModelTests(unittest.TestCase):
    def test_default_results_and_equilibrium(self):
        p = Parametry()
        r = symulacja(p)
        self.assertEqual(len(r.h), 36001)
        self.assertEqual(len(r.t), 36001)
        self.assertEqual(r.t[0], 0)
        self.assertEqual(r.t[-1], 3600)
        self.assertAlmostEqual(r.h[1], 0.005)
        self.assertAlmostEqual(r.h[-1], poziom_rownowagi(p), places=6)
        self.assertTrue(all(a <= b for a, b in zip(r.h, r.h[1:])))
        self.assertTrue(all(math.isfinite(x) for x in r.h))

    def test_falls_from_above_equilibrium(self):
        r = symulacja(replace(Parametry(), current_h=5))
        self.assertGreater(r.Q_odplyw[0], 0.075)
        self.assertTrue(all(a >= b for a, b in zip(r.h, r.h[1:])))
        self.assertAlmostEqual(r.h[-1], (0.075/0.035)**2, places=6)

    def test_empty_and_draining(self):
        self.assertEqual(max(symulacja(replace(Parametry(), Q_doplyw=0)).h), 0)
        r = symulacja(replace(Parametry(), Q_doplyw=0, current_h=5))
        self.assertEqual(r.h[-1], 0)
        self.assertGreaterEqual(min(r.h), 0)

    def test_overflow_and_closed_outlet(self):
        r = symulacja(replace(Parametry(), beta=0))
        self.assertEqual(r.h[-1], 5)
        self.assertAlmostEqual(r.Q_przelew[-2], 0.075)
        self.assertEqual(max(r.Q_odplyw), 0)

    def test_area_changes_speed_not_equilibrium(self):
        small = symulacja(replace(Parametry(), A=0.5))
        large = symulacja(replace(Parametry(), A=5, t_sim=7200))
        self.assertGreater(small.h[100], large.h[100])
        self.assertAlmostEqual(small.h[-1], large.h[-1], places=4)

    def test_validation(self):
        for changes in ({"A": 0}, {"Tp": 0}, {"beta": -1}, {"current_h": 6}, {"t_sim": 0.15}, {"Q_doplyw": float('nan')}):
            with self.assertRaises(ValueError):
                symulacja(replace(Parametry(), **changes))

    def test_csv_full_resolution(self):
        rows = list(csv.reader(io.StringIO(csv_wynikow(Parametry()))))
        self.assertEqual(len(rows), 36002)
        self.assertEqual(rows[0][0], 't_s')
        self.assertEqual(float(rows[-1][0]), 3600)
        self.assertAlmostEqual(float(rows[-1][2]), 100*float(rows[-1][1]))

    def test_dash_routes_callback_and_reset(self):
        client = app.server.test_client()
        for path in ('/', '/_dash-layout', '/_dash-dependencies', '/assets/style.css'):
            with client.get(path) as response:
                self.assertEqual(response.status_code, 200)
        fig, cards, state = aktualizuj(1.5, 0.035, 0.075, 0)
        self.assertEqual(len(fig.data[0].y), 36001)
        self.assertEqual(len(cards), 3)
        self.assertIn('4.5918', state)
        self.assertEqual(reset(1), [1.5, 0.035, 0.075, 0])


if __name__ == '__main__':
    unittest.main()

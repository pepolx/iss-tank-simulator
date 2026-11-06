import unittest
from app import app, symulacja, aktualizuj


class TestZbiornika(unittest.TestCase):
    def test_napelnianie(self):
        t, h = symulacja(1.5, 0.035, 0.075, 0)
        self.assertEqual(len(h), 36001)
        self.assertEqual(t[-1], 3600)
        self.assertAlmostEqual(h[1], 0.005)
        self.assertAlmostEqual(h[-1], (0.075 / 0.035) ** 2, places=6)

    def test_opadanie_i_oproznianie(self):
        _, h = symulacja(1.5, 0.035, 0.075, 5)
        self.assertLess(h[1], h[0])
        self.assertAlmostEqual(h[-1], (0.075 / 0.035) ** 2, places=6)
        _, h = symulacja(1.5, 0.035, 0, 5)
        self.assertEqual(h[-1], 0)
        self.assertGreaterEqual(min(h), 0)

    def test_granice(self):
        _, h = symulacja(1.5, 0, 0.075, 0)
        self.assertEqual(max(h), 5)
        _, h = symulacja(1.5, 0.035, 0, 0)
        self.assertEqual(max(h), 0)

    def test_interfejs(self):
        fig, wynik = aktualizuj(1.5, 0.035, 0.075, 0)
        self.assertEqual(len(fig.data), 1)
        self.assertIn('459.18 cm', wynik)
        self.assertIn('36001', wynik)
        client = app.server.test_client()
        self.assertEqual(client.get('/_dash-layout').status_code, 200)


if __name__ == '__main__':
    unittest.main()

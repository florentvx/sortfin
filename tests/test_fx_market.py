import unittest
from sortfin.fx_market import fx_market

from .test_asset import EUR, GBP, JPY, USD

FXM = fx_market()
FXM.add_quote(EUR, USD, 1.05)
FXM.add_quote(GBP, JPY, 200)
FXM.add_quote(GBP, USD, 1.5)

class TestFXMarket(unittest.TestCase):

    def test_add_quote(self):
        self.assertFalse(FXM.add_quote(EUR, JPY, 100))

    def test_fx_market(self):
        self.assertFalse(FXM.add_quote(EUR, JPY, 100))
        self.assertEqual(FXM.get_quote(EUR, EUR), 1.0)
        self.assertAlmostEqual(FXM.get_quote(USD, EUR), 1.0 / 1.05)
        self.assertAlmostEqual(FXM.get_quote(GBP, EUR), 1.5 / 1.05)
        self.assertAlmostEqual(FXM.get_quote(EUR, JPY), 1.05 / 1.5 * 200)



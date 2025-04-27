import unittest
from src.sortfin.asset import asset


GBP = asset("GBP", "£")
JPY = asset("JPY", "¥", separator_param=4, decimal_param=0)
USD = asset("USD", "$")
EUR = asset("EUR", "€")

class TestAsset(unittest.TestCase):

    def test_asset_creation(self):
        self.assertEqual(EUR.name, "EUR")
        self.assertEqual(EUR.symbol, "€")
        self.assertEqual(USD.name, "USD")
        self.assertEqual(USD.symbol, "$")
        self.assertEqual(GBP.name, "GBP")
        self.assertEqual(GBP.symbol, "£")
        self.assertEqual(JPY.name, "JPY")
        self.assertEqual(JPY.symbol, "¥")
        self.assertEqual(JPY.separator_param, 4)
        self.assertEqual(JPY.decimal_param, 0)

    def test_asset_show_value(self):
        self.assertEqual(GBP.show_value(123456.123456), "£ 123,456.12")
        self.assertEqual(JPY.show_value(12345678.926456), "¥ 1234,5679")
        self.assertEqual(USD.show_value(-9999.999), "- $ 10,000")

    def test_asset_copy(self):
        eur_copy = EUR.copy()
        self.assertEqual(eur_copy.name, EUR.name)
        self.assertEqual(eur_copy.symbol, EUR.symbol)
        self.assertIsNot(eur_copy, EUR)

    def test_asset_equality(self):
        eur_copy = EUR.copy()
        self.assertEqual(EUR, eur_copy)
        self.assertNotEqual(EUR, USD)
        self.assertNotEqual(EUR, GBP)
        self.assertNotEqual(EUR, JPY)
        self.assertNotEqual(USD, GBP)
        self.assertNotEqual(USD, JPY)
        self.assertNotEqual(GBP, JPY)

if __name__ == '__main__':
    unittest.main()
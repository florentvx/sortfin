import unittest

from src.sortfin.asset import Asset

JPY_SEPARATOR = 4
GBP = Asset("GBP", "£")
JPY = Asset("JPY", "¥", separator_param=JPY_SEPARATOR, decimal_param=0)
USD = Asset("USD", "$")
EUR = Asset("EUR", "€")

class TestAsset(unittest.TestCase):

    def test_asset_creation(self) -> None:
        assert EUR.name == "EUR" #noqa: S101
        assert EUR.symbol == "€" #noqa: S101
        assert USD.name == "USD" #noqa: S101
        assert USD.symbol == "$" #noqa: S101
        assert GBP.name == "GBP" #noqa: S101
        assert GBP.symbol == "£" #noqa: S101
        assert JPY.name == "JPY" #noqa: S101
        assert JPY.symbol == "¥" #noqa: S101
        assert JPY.separator_param == JPY_SEPARATOR #noqa: S101
        assert JPY.decimal_param == 0 #noqa: S101

    def test_asset_show_value(self) -> None:
        assert GBP.show_value(123456.123456) == "£ 123,456.12" #noqa: S101
        assert JPY.show_value(12345678.926456) == "¥ 1234,5679" #noqa: S101
        assert USD.show_value(-9999.999) == "- $ 10,000" #noqa: S101
        assert USD.show_value(127.0346784) == "$ 127.03" #noqa: S101

    def test_asset_copy(self) -> None:
        eur_copy = EUR.copy()
        assert eur_copy.name == EUR.name #noqa: S101
        assert eur_copy.symbol == EUR.symbol #noqa: S101
        assert eur_copy == EUR #noqa: S101

    def test_asset_equality(self) -> None:
        eur_copy = EUR.copy()
        assert eur_copy == EUR  # noqa: S101
        assert EUR != USD #noqa: S101
        assert EUR != GBP #noqa: S101
        assert EUR != JPY #noqa: S101
        assert USD != GBP #noqa: S101
        assert USD != JPY #noqa: S101
        assert GBP != JPY #noqa: S101

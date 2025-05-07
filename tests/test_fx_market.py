import unittest

from src.sortfin.fx_market import FxMarket

from .test_asset import EUR, GBP, JPY, USD

FXM = FxMarket()
FXM.add_quote(EUR, USD, 1.05)
FXM.add_quote(GBP, JPY, 200)
FXM.add_quote(GBP, USD, 1.5)

TOLERANCE = 1e-6
class TestFXMarket(unittest.TestCase):

    def test_add_quote(self) -> None:
        assert not FXM.add_quote(EUR, JPY, 100) #noqa: S101

    def test_fx_market(self) -> None:
        assert not FXM.add_quote(EUR, JPY, 100) #noqa: S101
        assert FXM.get_quote(EUR, EUR) == 1.0 #noqa: S101
        assert abs(FXM.get_quote(USD, EUR) - 1.0 / 1.05) < TOLERANCE #noqa: S101
        assert abs(FXM.get_quote(GBP, EUR) - 1.5 / 1.05) < TOLERANCE #noqa: S101
        assert abs(FXM.get_quote(EUR, JPY) - 1.05 / 1.5 * 200) < TOLERANCE #noqa: S101



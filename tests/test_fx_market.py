import unittest

from src.sortfin.fx_market import FxMarket

from .test_asset import EUR, GBP, JPY, USD
from .test_assetdb import ASSET_DB

FXM = FxMarket()
FXM.add_quote(ASSET_DB, EUR.name, USD.name, 1.05)
FXM.add_quote(ASSET_DB, GBP.name, JPY.name, 200)
FXM.add_quote(ASSET_DB, GBP.name, USD.name, 1.5)

TOLERANCE = 1e-6
class TestFXMarket(unittest.TestCase):

    def test_add_quote(self) -> None:
        assert not FXM.add_quote(ASSET_DB, EUR.name, JPY.name, 100) #noqa: S101

    def test_fx_market(self) -> None:
        assert not FXM.add_quote(ASSET_DB, EUR.name, JPY.name, 100) #noqa: S101
        assert FXM.get_quote(ASSET_DB, EUR.name, EUR.name) == 1.0 #noqa: S101
        assert abs(FXM.get_quote(ASSET_DB, USD.name, EUR.name) - 1.0 / 1.05) < TOLERANCE #noqa: S101
        assert abs(FXM.get_quote(ASSET_DB, GBP.name, EUR.name) - 1.5 / 1.05) < TOLERANCE #noqa: S101
        assert abs(FXM.get_quote(ASSET_DB, EUR.name, JPY.name) - 1.05 / 1.5 * 200) < TOLERANCE #noqa: S101, E501



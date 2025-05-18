import unittest

from src.sortfin.asset_database import AssetDatabase

from .test_asset import EUR, GBP, JPY, USD

ASSET_DB = AssetDatabase()
ASSET_DB.add_asset(EUR)
ASSET_DB.add_asset(USD)
ASSET_DB.add_asset(GBP)
ASSET_DB.add_asset(JPY)


class TestAssetDB(unittest.TestCase):

    def test_add(self) -> None:
        bmk0 = 0
        new_adb= AssetDatabase()
        new_adb_1 = AssetDatabase().copy()
        new_adb_1.add_asset(EUR)
        bmk1 = bmk0 + 1
        new_adb_2 = new_adb_1.copy()
        new_adb_2.add_asset(JPY)
        bmk2 = bmk1 + 1
        return len(new_adb.assets) == bmk0 and \
            len(new_adb_1.assets) == bmk1 and \
            len(new_adb_2.assets) == bmk2

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .asset_database import AssetDatabase


class FxMarket:
    def __init__(self) -> None:
        """Initialize the FX market with an empty quotes dictionary."""
        self.quotes : dict[tuple[str, str], float] = {}
        self.secondary_quotes : dict[tuple[str, str], float] = {}

    def __str__(self) -> str:
        res = "FX Market: \n"
        for t, v in self.quotes.items():
            res += f"{t[0]}/{t[1]} : {round(v,4)}\n"
        return res

    def __hash__(self) -> int:
        return self.quotes.__hash__() + self.secondary_quotes.__hash__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FxMarket):
            return False
        if len(self.quotes) != len(other.quotes):
            return False
        for k, v in self.quotes.items():
            if k not in other.quotes or other.quotes[k] != v:
                return False
        return True

    def copy(self) -> FxMarket:
        res = FxMarket()
        res.quotes = {
            (k[0], k[1]): v + 0
            for (k,v) in self.quotes.items()
        }
        return res

    def _filter_quote_dict(
            self,
            asset: str,
            quote_dict : dict[tuple[str, str], float]|None = None,
            filter_asset_list : list[str]|None = None,
        ) -> dict[tuple[str, str], float]:
        if filter_asset_list is None:
            filter_asset_list = []
        if quote_dict is None:
            quote_dict = {**self.quotes, **self.secondary_quotes}
        return {
            k: v
            for (k, v) in quote_dict.items()
            if (k[0] == asset or k[1] == asset) and \
                (k[0] not in filter_asset_list and k[1] not in filter_asset_list)
        }

    def _get_quote(
            self,
            asset1: str,
            asset2: str,
            filter_asset_list : list[str]|None = None,
        ) -> float|None:
        if filter_asset_list is None:
            filter_asset_list = []
        if asset1 == asset2:
            return 1.0
        asset1_dict = self._filter_quote_dict(
            asset1,
            filter_asset_list=filter_asset_list,
        )
        if len(asset1_dict) == 0:
            return None
        direct : dict[tuple[str, str], float] = self._filter_quote_dict(
            asset2,
            quote_dict=asset1_dict,
            filter_asset_list=filter_asset_list,
        )
        if len(direct) != 0:
            if len(direct) > 1:
                msg = f"multiple direct quotes found for {asset1}/{asset2}"
                raise ValueError(msg)
            [(key, value)] = list(direct.items())
            if key[0] == asset1:
                return value
            return 1 / value
        for asset_key in asset1_dict:
            asset_k = asset_key[1]
            asset_value = asset1_dict[asset_key]
            if asset_key[1] == asset1:
                asset_k = asset_key[0]
                asset_value = 1/asset_value
            res = self._get_quote(
                asset_k, asset2,
                filter_asset_list = [asset1, *filter_asset_list],
            )
            if res is not None:
                result = asset_value * res
                self.secondary_quotes[(asset1, asset2)] = result
                return result
        return None  # Return None if no quote is found

    def get_quote(
            self,
            asset_db: AssetDatabase,
            unit1: str,
            unit2: str,
        ) -> float|None:
        test1, asset1 = asset_db.find_asset_from_input(unit1)
        test2, asset2 = asset_db.find_asset_from_input(unit2)
        if not test1:
            msg = f"Asset {asset1} not found in the AssetDatabase"
            raise ValueError(msg)
        if not test2:
            msg = f"Asset {asset2} not found in the AssetDatabase"
            raise ValueError(msg)
        assert asset1 is not None #noqa: S101
        assert asset2 is not None #noqa: S101
        return self._get_quote(
            asset1.name,
            asset2.name,
        )

    def add_quote(
            self,
            asset_db: AssetDatabase,
            asset1: str,
            asset2: str,
            rate: float,
        ) -> bool:
        """Add a quote to the FX market."""
        if rate <= 0:
            msg = f"Rate must be positive, not {rate}"
            raise ValueError(msg)
        if asset1 == asset2:
            msg=f"Cannot add quote for identical assets: {asset1}/{asset2}"
            raise ValueError(msg)
        # testt with AssetDB
        test1, _ = asset_db.find_asset_from_input(asset1)
        if not test1:
            msg = f"Asset {asset1} not found in the AssetDatabase:  {asset_db}"
            raise ValueError(msg)
        test2, _ = asset_db.find_asset_from_input(asset2)
        if not test2:
            msg = f"Asset {asset2} not found in the AssetDatabase"
            raise ValueError(msg)
        # Clean up self-referential quotes
        self.quotes = {k: v for k, v in self.quotes.items() if k[0] != k[1]}
        if self.get_quote(asset_db, asset1, asset2) is None:
            self.quotes[(asset1, asset2)] = rate
            self.secondary_quotes = {} # clean up secondary quotes
            return True
        return False

    def modify_quote(
            self,
            asset1: str,
            asset2: str,
            rate: float,
        ) -> tuple[bool, str]:
        """Modify an existing quote in the FX market."""
        if rate <= 0:
            return False, f"Rate must be positive, not {rate}"
        if asset1 == asset2:
            return False, f"Cannot modify quote for identical assets: {asset1}/{asset2}"
        if (asset1, asset2) not in self.quotes:
            if (asset2, asset1) in self.quotes:
                self.quotes[(asset1, asset2)] = 1 / rate
                return True, f"Modified quote for {asset1}/{asset2} to {1 / rate}"
            return False, f"Quote for {asset1}/{asset2} does not exist"
        self.quotes[(asset1, asset2)] = rate
        return True, f"Modified quote for {asset1}/{asset2} to {rate}"

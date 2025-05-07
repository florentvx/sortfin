from __future__ import annotations

from .asset import Asset


class FxMarket:
    def __init__(self) -> None:
        self.quotes : dict[tuple[Asset, Asset], float] = {}
        self.secondary_quotes : dict[tuple[Asset, Asset], float] = {}

    def __str__(self) -> str:
        res = "FX Market: \n"
        for t, v in self.quotes.items():
            res += f"{t[0].name}/{t[1].name} : {round(v,4)}\n"
        return res

    def copy(self) -> FxMarket:
        res = FxMarket()
        res.quotes = {
            (k[0].copy(), k[1].copy()): v + 0
            for (k,v) in self.quotes.items()
        }
        return res

    def get_asset_database(self) -> set[Asset]:
        return {k[0] for k in self.quotes} | {k[1] for k in self.quotes}

    def get_asset_from_input(self, asset_input: Asset|str) -> Asset:
        if isinstance(asset_input, Asset):
            return asset_input
        if not isinstance(asset_input, str):
            msg = f"Asset input must be of type asset or str, not {type(asset_input)}"
            raise TypeError(msg)
        asset_list = [a for a in self.get_asset_database() if a.name == asset_input]
        if len(asset_list) == 0:
            msg=f"Asset {asset_input} not found in the FX market"
            raise ValueError(msg)
        if len(asset_list) > 1:
            msg=(
                f"Asset {asset_input} is ambiguous in the FX market:"
                f" {','.join([a.name for a in asset_list])}"
            )
            raise ValueError(msg)
        return asset_list[0]

    def _filter_quote_dict(
            self,
            asset: Asset,
            quote_dict : dict[tuple[Asset, Asset], float]|None = None,
            filter_asset_list : list[Asset]|None = None,
        ) -> dict[tuple[Asset, Asset], float]:
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
            asset1: Asset,
            asset2: Asset,
            filter_asset_list : list[Asset]|None = None,
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
        direct : dict[tuple[Asset, Asset], float] = self._filter_quote_dict(
            asset2,
            quote_dict=asset1_dict,
            filter_asset_list=filter_asset_list,
        )
        if len(direct) != 0:
            if len(direct) > 1:
                msg = "multiple direct quotes found for {asset1.name}/{asset2.name}"
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

    def get_quote(self, asset1: Asset|str, asset2: Asset|str) -> float|None:
        return self._get_quote(
            self.get_asset_from_input(asset1),
            self.get_asset_from_input(asset2),
        )

    def add_quote(self, asset1: Asset, asset2: Asset, rate: float) -> bool:
        if rate <= 0:
            msg = f"Rate must be positive, not {rate}"
            raise ValueError(msg)
        if asset1 == asset2:
            msg=f"Cannot add quote for identical assets: {asset1.name}/{asset2.name}"
            raise ValueError(msg)
        # Clean up self-referential quotes
        self.quotes = {k: v for k, v in self.quotes.items() if k[0] != k[1]}
        if self.get_quote(asset1, asset2) is None:
            self.quotes[(asset1, asset2)] = rate
            self.secondary_quotes = {} # clean up secondary quotes
            return True
        return False

    def set_single_asset(self, asset: Asset) -> None:
        if self.quotes:
            msg="Cannot set single asset when quotes are not empty"
            raise ValueError(msg)
        self.quotes[(asset, asset)] = 1.0  # Create a self-referential quote

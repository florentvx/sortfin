from __future__ import annotations

from .asset import asset

class fx_market:
    def __init__(self) -> None:
        self.quotes : dict[tuple[asset, asset], float] = {}
        self.secondary_quotes : dict[tuple[asset, asset], float] = {}

    def __str__(self) -> str:
        res = "FX Market: \n"
        for t, v in self.quotes.items():
            res += f"{t[0].name}/{t[1].name} : {round(v,4)}\n"
        return res

    def copy(self) -> fx_market:
        res = fx_market()
        res.quotes = {
            (k[0].copy(), k[1].copy()): v + 0
            for (k,v) in self.quotes.items()
        }
        return res
    
    def get_asset_database(self) -> set[asset]:
        return {k[0] for k in self.quotes} | {k[1] for k in self.quotes}

    def _filter_quote_dict(
            self, 
            asset: asset, 
            quote_dict = None,
            filter_asset_list : list[asset]|None = None,
        ) -> dict[tuple[asset, asset], float]:
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

    def _get_quote(self, asset1: asset, asset2: asset, filter_asset_list : list[asset]|None = None) -> float|None:
        if filter_asset_list is None:
            filter_asset_list = []
        if asset1 == asset2:
            return 1.0
        asset1_dict = self._filter_quote_dict(asset1, filter_asset_list=filter_asset_list)
        if len(asset1_dict) == 0:
            return None
        direct : dict[tuple[asset, asset], float] = self._filter_quote_dict(
            asset2, 
            quote_dict=asset1_dict, 
            filter_asset_list=filter_asset_list
        )
        if len(direct) != 0:
            assert len(direct) == 1
            [(key, value)] = list(direct.items())
            if key[0] == asset1:
                return value
            else:
                return 1 / value
        for asset_key in asset1_dict.keys():
            asset_k = asset_key[1]
            asset_value = asset1_dict[asset_key]
            if asset_key[1] == asset1:
                asset_k = asset_key[0]
                asset_value = 1/asset_value
            res = self._get_quote(
                asset_k, asset2, 
                filter_asset_list = [asset1] + filter_asset_list
            )
            if res is not None:
                result = asset_value * res
                self.secondary_quotes[(asset1, asset2)] = result
                return result
        return None  # Return None if no quote is found
            
    def get_quote(self, asset1: asset, asset2: asset|str) -> float|None:
        if isinstance(asset2, str):
            l_asset2 = [a for a in self.get_asset_database() if a.name == asset2]
            if len(l_asset2) == 0:
                raise ValueError(f"Asset {asset2} not found in the FX market")
            elif len(l_asset2) > 1:
                raise ValueError(f"Asset {asset2} is ambiguous in the FX market")
            asset2 = l_asset2[0]
        return self._get_quote(asset1, asset2)
    
    def add_quote(self, asset1: asset, asset2: asset, rate: float) -> bool:
        if rate <= 0:
            raise ValueError("Rate must be positive")
        if asset1 == asset2:
            raise ValueError("Cannot add quote for identical assets")
        # Clean up self-referential quotes
        self.quotes = {k: v for k, v in self.quotes.items() if k[0] != k[1]}
        if self.get_quote(asset1, asset2) is None:
            self.quotes[(asset1, asset2)] = rate
            self.secondary_quotes = {} # clean up secondary quotes
            return True
        return False

    def set_single_asset(self, asset: asset) -> None:
        if self.quotes:
            raise ValueError("Cannot set single asset when quotes are not empty")
        self.quotes[(asset, asset)] = 1.0  # Create a self-referential quote

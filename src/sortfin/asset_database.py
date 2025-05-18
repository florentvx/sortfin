from __future__ import annotations

from typing import Iterator

from .asset import Asset


class AssetDatabase:
    def __init__(self) -> None:
        self.assets : set[Asset] = set()

    def __str__(self) -> str:
        res = "AssetDatabase: \n"
        for a in self.assets:
            res += f"{a.name} ({a.symbol})\n"
        return res

    def __iter__(self) -> Iterator[Asset]:
        """Iterate over the assets in the database."""
        yield from self.assets

    def copy(self) -> AssetDatabase:
        """Create a copy of the AssetDatabase."""
        res = AssetDatabase()
        res.assets = {a.copy() for a in self.assets}
        return res

    def find_asset_from_input(self, asset_input: Asset|str) -> tuple[bool, Asset|None]:
        if isinstance(asset_input, Asset):
            return asset_input in self.assets, asset_input
        if not isinstance(asset_input, str):
            msg = f"Asset input must be of type asset or str, not {type(asset_input)}"
            raise TypeError(msg)
        asset_list = [a for a in self.assets if a.name == asset_input]
        if len(asset_list) == 0:
            return False, None
        if len(asset_list) > 1:
            msg=(
                f"AssetDatabase is corrupted as there are more than one {asset_input}:"
                f" {','.join([a.name + '-' +  a.symbol for a in asset_list])}"
            )
            raise ValueError(msg)
        return True, asset_list[0]

    def add_asset(self, asset: Asset) -> None:
        test, _ = self.find_asset_from_input(asset)
        if test:
            msg = (
                f"Asset {asset} already exists in the AssetDatabase"
                f" (available assets: {', '.join([a.name for a in self.assets])})"
            )
            raise ValueError(msg)
        self.assets.add(asset)

    def get_asset_from_name(self, asset_id: str) -> Asset|None:
        test, asset = self.find_asset_from_input(asset_id)
        return asset if test else None

    def remove_asset(self, asset: Asset) -> None:
        test, _ = self.find_asset_from_input(asset)
        if test:
            self.assets.discard(asset)

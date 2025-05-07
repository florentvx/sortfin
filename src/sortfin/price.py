from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .asset import Asset


class Price:
    def __init__(self, value: float, unit: Asset) -> None:
        self.value: float = value
        self.unit: Asset = unit

    def __str__(self) -> str:
        return self.unit.show_value(self.value)

    def __repr__(self) -> str:
        return f"price({self.value} {self.unit.name})"

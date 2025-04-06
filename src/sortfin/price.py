from __future__ import annotations

from .asset import asset

class price:
    def __init__(self, value: float, unit: asset):
        self.value: float = value
        self.unit: asset = unit

    def __str__(self):
        return self.unit.show_value(self.value)
    
    def __repr__(self):
        return f"price({self.value} {self.unit.name})"
    
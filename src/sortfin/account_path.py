from __future__ import annotations

class account_path:

    def __init__(self, x: str|None = None):
        if x is None or x == ".":
            x = ""
        if len(x) > 0 and x[0] == "/":
            raise ValueError(f"Do not use a / at the beginning: {x}")
        self.parts = x.split("/")
        if x == "":
            self.parts = []
        elif self.parts[-1] == "":
            self.parts.pop(len(self.parts)-1)

    def __str__(self):
        if len(self.parts) == 0:
            return '.'
        return "/".join(self.parts)
    
    def __repr__(self):
        return f"account_path({str(self)})"
    
    def __truediv__(self, other: str|account_path):
        if isinstance(other, str):
            if len(self.parts) == 0:
                return account_path(other)
            return account_path(str(self) + "/" + other)    

        if len(self.parts) == 0 or len(other.parts) == 0:
            raise ValueError()
        return account_path('/'.join(self.parts + other.parts))

    @property
    def is_empty(self):
        return len(self.parts) == 0

    @property
    def is_singleton(self):
        return len(self.parts) == 1
    
    @property
    def root_folder(self):
        if self.is_empty:
            return None
        return self.parts[0]

    @property
    def parent(self) -> account_path:
        if len(self.parts) == 1:
            return account_path(None)
        return account_path('/'.join(self.parts[:(len(self.parts)-1)]))
    
    @property
    def name(self) -> str:
        return self.parts[-1]

    def get_child(self) -> account_path:
        return account_path('/'.join(self.parts[1:]))


from __future__ import annotations


class AccountPathError(ValueError):
    """Custom error for AccountPath."""

class AccountPath:

    def __init__(self, x: str|None = None) -> None:
        if x is None or x == ".":
            x = ""
        if len(x) > 0 and x[0] == "/":
            msg=f"Do not use a / at the beginning: {x}"
            raise AccountPathError(msg)
        self.parts = x.split("/")
        if x == "":
            self.parts = []
        elif self.parts[-1] == "":
            self.parts.pop(len(self.parts)-1)

    def __str__(self) -> str:
        if len(self.parts) == 0:
            return "."
        return "/".join(self.parts)

    def __repr__(self) -> str:
        return f"account_path({self!s})"

    def __truediv__(self, other: str|AccountPath) -> AccountPath:
        if isinstance(other, str):
            if len(self.parts) == 0:
                return AccountPath(other)
            return AccountPath(str(self) + "/" + other)

        if len(self.parts) == 0 or len(other.parts) == 0:
            msg="Cannot combine empty paths"
            raise ValueError(msg)
        return AccountPath("/".join(self.parts + other.parts))

    @property
    def is_empty(self) -> bool:
        return len(self.parts) == 0

    @property
    def is_singleton(self) -> bool:
        return len(self.parts) == 1

    @property
    def root_folder(self) -> str|None:
        if self.is_empty:
            return None
        return self.parts[0]

    @property
    def parent(self) -> AccountPath:
        if len(self.parts) == 1:
            return AccountPath(None)
        return AccountPath("/".join(self.parts[:(len(self.parts)-1)]))

    @property
    def name(self) -> str:
        return self.parts[-1]

    def get_child(self) -> AccountPath:
        return AccountPath("/".join(self.parts[1:]))


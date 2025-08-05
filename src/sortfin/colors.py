from enum import Enum


class Color(str, Enum):
    RED="\033[0;31m"
    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    YELLOW = "\033[0;33m"
    RESET = "\033[0m"

    def __str__(self) -> str:
        return self.value

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator

from .account_path import AccountPath
from .asset import Asset
from .price import Price

if TYPE_CHECKING:
    from .fx_market import FxMarket


class Account:
    def __init__(
            self,
            name: str,
            unit: Asset,
            *,
            value: float | None = None,
            sub_accounts: list[Account] | None = None,
        ) -> None:

        if (value is None and sub_accounts is None):
            msg="Account has to be terminal or intemediary"
            raise ValueError(msg)
        if ((value is not None) and (sub_accounts is not None)):
            msg="Account cannot be terminal and intermediary at the same time"
            raise ValueError(msg)
        if not isinstance(name, str) or name == "":
            msg=f"account name is not set properly [{name}]"
            raise ValueError(msg)
        if not isinstance(unit, Asset):
            msg=f"unit of account is not an asset: {unit}"
            raise TypeError(msg)

        self.name: str = name
        self.unit : Asset = unit
        self.value: float | None = value
        self.sub_accounts : list[Account] | None = sub_accounts

    def __str__(self) -> str:
        return f"{self.name} {self.unit}"

    @property
    def is_terminal(self) -> bool:
        return self.value is not None

    def get_price(self) -> Price:
        if self.value is not None:
            return Price(self.value, self.unit)
        msg="Account is not terminal and does not have a price"
        raise ValueError(msg)

    def set_value(self, new_value: float) -> None:
        if not self.is_terminal:
            msg="cannot set value on a intermediary account"
            raise ValueError(msg)
        self.value = new_value

    def get_account(self, path: AccountPath | None) -> Account:
        if path is None or path.is_empty:
            return self
        if self.sub_accounts is None:
            msg = f"account {self.name} is terminal and cannot have sub_accounts"
            raise ValueError(msg)
        if path.root_folder is None:
            msg="path.root_folder is None"
            raise ValueError(msg)
        sa_match_list = [
            sa
            for sa in self.sub_accounts
            if sa.name.upper() == path.root_folder.upper()
        ]
        if len(sa_match_list) == 0:
            msg= f"no match for {path.root_folder} in {self.name}"
            raise ValueError(msg)
        if len(sa_match_list) > 1:
            msg= f"multiple matches for {path.root_folder} in {self.name}"
            raise ValueError(msg)
        return sa_match_list[0].get_account(path.get_child())

    def get_account_structure(
            self,
            prefix: AccountPath | None = None,
        ) -> tuple[AccountPath, Any]:
        if prefix is None:
            prefix = AccountPath()
        full_prefix = prefix / self.name
        if self.is_terminal:
            return (full_prefix, None)
        if self.sub_accounts is None:
            msg = "sub_accounts is None"
            raise ValueError(msg)
        return (
            full_prefix,
            [
                sa.get_account_structure(full_prefix)
                for sa in self.sub_accounts
            ],
        )

    def _print_structure(
            self,
            structure: tuple[AccountPath, Any],
            level: int,
        ) -> Iterator[str]:
        acc_p, rest_struct = structure
        acc = self.get_account(acc_p.get_child())
        prefix = f"{'  ' * level} {level}. {acc_p} : {acc.unit.name}"
        if rest_struct is None:
            if acc.value is None:
                msg="account is not terminal"
                raise ValueError(msg)
            yield prefix + f" -> {acc.unit.show_value(acc.value)}"
        else:
            yield prefix
            for child in rest_struct:
                yield from self._print_structure(child, level + 1)

    def print_structure(self) -> str:
        return (
            "\n".join(
                self._print_structure(
                    structure = self.get_account_structure(),
                    level=0,
                ),
            )
        )

    def _get_account_value(
            self,
            fx_mkt: FxMarket,
            unit: Asset|str|None = None,
        ) -> float:
        if unit is None:
            unit = self.unit
        if self.sub_accounts is None:
            if self.value is None:
                msg="account is not terminal"
                raise ValueError(msg)
            fx_rate = fx_mkt.get_quote(self.unit, unit)
            if fx_rate is None:
                msg=f"no quote for {self.unit} to {unit}"
                raise ValueError(msg)
            return self.value * fx_rate
        return sum([
            sa._get_account_value(fx_mkt, unit) #noqa: SLF001
            for sa in self.sub_accounts
        ])

    def _get_account_price(
            self,
            fx_mkt: FxMarket,
            unit: Asset|None = None,
        ) -> Price:
        return Price(
            self._get_account_value(fx_mkt, unit),
            unit if unit is not None else self.unit,
        )

    def _get_account_summary(
            self,
            fx_mkt: FxMarket,
            unit: Asset|None = None,
        ) -> list[tuple[str, Price, Price]]:
        if unit is None:
            unit = self.unit
        if self.sub_accounts is None:
            msg="account is not terminal"
            raise ValueError(msg)
        return [
            (
                sa.name,
                sa._get_account_price(fx_mkt, sa.unit), #noqa: SLF001
                sa._get_account_price(fx_mkt, unit), #noqa: SLF001
            )
            for sa in self.sub_accounts
        ]

    def get_account_price(
            self,
            fx_mkt: FxMarket,
            path: AccountPath|None = None,
            unit: Asset|None = None,
        ) -> Price:
        return self.get_account(path)._get_account_price(fx_mkt, unit) #noqa: SLF001

    def get_account_summary(
            self,
            fx_mkt: FxMarket,
            path: AccountPath|None = None,
            unit: Asset|None = None,
        ) -> list[tuple[str, Price, Price]]:
        return self.get_account(path)._get_account_summary(fx_mkt, unit) #noqa: SLF001

    def print_account_summary(
            self, fx_mkt: FxMarket,
            path: AccountPath|None = None,
            unit: Asset|None = None,
        ) -> str:
        res = ""
        for name, price1, price2 in self.get_account_summary(fx_mkt, path, unit):
            value1 = str(price1)
            len_name = len(name)
            space1 = 10 - len_name
            len_val1 = len(value1)
            space2 = 15 - len_val1
            res += f'\n{name}:{" " * space1}{value1}{" " * space2}{price2}'
        return f"Account Summary: {self.name} {self.unit.name}" + res

    def add_account(
            self,
            path: AccountPath,
            *,
            is_terminal: bool,
            unit: Asset|None = None,
        ) -> None:
        sub_acc = self.get_account(path.parent)
        if sub_acc.sub_accounts is None:
            msg="cannot add account to a terminal account"
            raise ValueError(msg)
        test_l = [sa for sa in sub_acc.sub_accounts if sa.name == path.name]
        if len(test_l) != 0:
            msg="account already exists"
            raise ValueError(msg)
        unit_to_use = unit if unit is not None else sub_acc.unit
        if is_terminal:
            sub_acc.sub_accounts += [
                Account(path.name, value=0, unit=unit_to_use),
            ]
        else:
            sub_acc.sub_accounts += [
                Account(path.name, sub_accounts=[], unit=unit_to_use),
            ]

    def copy(self) -> Account:
        if self.sub_accounts is None:
            return Account(self.name + "", unit= self.unit.copy(), value=self.value)
        return Account(
            self.name + "", self.unit.copy(),
            sub_accounts=[acc.copy() for acc in self.sub_accounts],
        )

    def diff(self, other: Account, memory: str = "") -> str:  # noqa: C901, PLR0912
        if not isinstance(other, Account):
            msg="other is not an account"
            raise TypeError(msg)

        title = f"Account Differences for {memory + self.name}:\n"
        res = ""
        test_res = False
        test_res_2 = False

        # Compare names
        if self.name != other.name:
            test_res = True
            res += f"  Name: {self.name} -> {other.name}\n"

        # Compare types
        if self.is_terminal != other.is_terminal:
            test_res = True
            res += (
                f"  Type: {'Terminal' if self.is_terminal else 'Folder'} -> "
                f"{'Terminal' if other.is_terminal else 'Folder'}\n"
            )

        # Compare units
        if self.unit != other.unit:
            test_res = True
            res += f"Unit: {self.unit.name} -> {other.unit.name}\n"

        if self.is_terminal and other.is_terminal and self.value != other.value:
            test_res = True
            res += f"Value: {self.value} -> {other.value}\n"

        if self.sub_accounts is not None and other.sub_accounts is not None:
            # Compare sub-accounts
            self_sub_accounts = {
                sub_acc.name: sub_acc for sub_acc in self.sub_accounts
            }
            other_sub_accounts = {
                sub_acc.name: sub_acc for sub_acc in other.sub_accounts
            }

            for name, sub_acc in self_sub_accounts.items():
                if name in other_sub_accounts:
                    sub_acc_diff = sub_acc.diff(
                        other_sub_accounts[name],
                        memory=memory + self.name + "/",
                    )
                    if sub_acc_diff != "":
                        test_res_2 = True
                        res += sub_acc_diff
                else:
                    test_res = True
                    res += f"Missing Sub-Account {name}\n"

            for name in other_sub_accounts:
                if name not in self_sub_accounts:
                    test_res = True
                    res += f"New Sub-Account {name}\n"
        if test_res:
            return title + res
        if test_res_2:
            return res
        return ""




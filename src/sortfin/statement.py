from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from .account import Account
from .fx_market import FxMarket

if TYPE_CHECKING:

    from .account_path import AccountPath
    from .asset import Asset


def initialize_statement(unit: Asset) -> Statement:
    """Initialize a statement with a given unit and the current date."""
    fx_mkt = FxMarket()
    fx_mkt.set_single_asset(unit)
    return Statement(
        dt.datetime.now(tz=dt.timezone.utc),
        fx_mkt,
        Account(name="root", unit=unit, sub_accounts=[]),
    )

class Statement:
    def __init__(
            self,
            date: dt.datetime,
            fx_mkt: FxMarket,
            acc: Account,
        ) -> None:
        self.date : dt.datetime = date
        self.fx_market : FxMarket = fx_mkt
        self.account : Account = acc
        self.print_summary() # forces the computation of all fx quotes needed # noqa: E501

    def copy_statement(self, date: dt.datetime) -> Statement:
        return Statement(date, self.fx_market.copy(), self.account.copy())

    def get_account(self, ap: AccountPath) -> Account:
        return self.account.get_account(ap)

    def change_terminal_account(
            self,
            ap: AccountPath,
            value: float|None = None,
            unit: Asset|None = None,
        ) -> None:
        acc = self.get_account(ap)
        if acc.is_terminal:
            if value is not None:
                acc.value=value
            if unit is not None:
                acc.unit=unit
        else:
            msg=f"account: [{acc}] is not terminal"
            raise ValueError(msg)

    def change_folder_account(self, ap:AccountPath, unit: Asset) -> None:
        acc = self.get_account(ap)
        if not acc.is_terminal:
            if unit is not None:
                acc.unit=unit
        else:
            msg=f"account: [{acc}] is terminal"
            raise ValueError(msg)

    def add_account(self, folder_path: AccountPath, new_account: Account|str) -> None:
        folder_account = self.get_account(folder_path)
        if folder_account.sub_accounts is None:
            msg=f"Cannot add an account to a terminal account: {folder_account}"
            raise ValueError(msg)
        if isinstance(new_account, str):
            new_account = Account(new_account, unit=folder_account.unit)
        folder_account.sub_accounts.append(new_account)

    def print_structure(self) -> str:
        return self.account.print_structure() + "\n" + str(self.fx_market)

    def print_summary(
            self,
            path: AccountPath|None = None,
            unit: Asset|None = None,
        ) -> str:
        return (
            f"Statement: {self.date.date().isoformat()}\n"
            f"{self.account.print_account_summary(self.fx_market, path, unit)}"
        )

    def diff(self, other: Statement) -> str:
        if not isinstance(other, Statement):
            msg="The other object must be an instance of statement"
            raise TypeError(msg)
        res = ""
        if self.date != other.date:
            res += f"Date: {self.date} -> {other.date}\n"

        # Compare account structures
        diff_acc_struct = self.account.diff(other.account)
        if len(diff_acc_struct) > 0:
            res += "Account Structure Differences:\n"
            res +=diff_acc_struct

        # Compare FX markets
        res_fx = ""
        for (k, v) in self.fx_market.quotes.items():
            if k in other.fx_market.quotes:
                if v != other.fx_market.quotes[k]:
                    res_fx += (
                        f"{k[0].name}/{k[1].name}: {v} "
                        f"-> {other.fx_market.quotes[k]}\n"
                    )
            else:
                res_fx += (
                    f"{k[0].name}/{k[1].name}: {v} "
                    "-> Not present in other statement\n"
                )

        for (k, v) in other.fx_market.quotes.items():
            if k not in self.fx_market.quotes:
                res_fx += (
                    f"{k[0].name}/{k[1].name}: "
                    f"Not present in this statement -> {round(v,6)}\n"
                )
        if len(res_fx) > 0:
            res += "FX Market Differences:\n"
            res += res_fx
        return res

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from .account import Account
from .asset_database import AssetDatabase
from .fx_market import FxMarket

if TYPE_CHECKING:
    from .account_path import AccountPath
    from .asset import Asset


class Statement:
    def __init__(
            self,
            date: dt.datetime,
            fx_mkt: FxMarket,
            acc: Account,
            asset_db: AssetDatabase|None = None,
        ) -> None:
        self.date : dt.datetime = date
        self.fx_market : FxMarket = fx_mkt
        self.account : Account = acc
        if asset_db is not None:
            # forces the computation of all fx quotes needed
            # check if this is needed
            self.print_summary(asset_db)

    def copy(self, date: dt.datetime) -> Statement:
        return Statement(
            date,
            self.fx_market.copy(),
            self.account.copy(),
        )

    def get_account(self, ap: AccountPath) -> Account:
        return self.account.get_account(ap)

    def change_terminal_account(
            self,
            ap: AccountPath,
            value: float|None = None,
            unit: str|None = None,
        ) -> None:
        if value is None and unit is None:
            msg = "Either value or unit must be provided"
            raise ValueError(msg)
        acc = self.get_account(ap)
        if not acc.is_terminal:
            msg=f"account: [{acc}] is not terminal"
            raise ValueError(msg)
        if value is not None:
            acc.value=value
            if unit is not None:
                acc.unit=unit
        else:
            acc.unit=unit

    def change_folder_account(self, ap:AccountPath, unit: str) -> None:
        acc = self.get_account(ap)
        if acc.value is not None:
            msg=f"account: [{acc}] is terminal"
            raise ValueError(msg)
        acc.unit=unit

    def add_account(
            self,
            folder_path: AccountPath,
            new_account: Account|str,
            *,
            unit: str|None = None,
            value: float|None = None,
        ) -> None:
        if isinstance(new_account, Account):
            if unit is not None:
                msg="Cannot set unit on an existing account"
                raise ValueError(msg)
            if value is not None:
                msg="Cannot set value on an existing account"
                raise ValueError(msg)
        folder_account = self.get_account(folder_path)
        if folder_account.sub_accounts is None:
            msg=f"Cannot add an account to a terminal account: {folder_account}"
            raise ValueError(msg)
        if isinstance(new_account, str):
            new_account = Account(
                new_account,
                unit=folder_account.unit if unit is None else unit,
                value=value,
                sub_accounts=[] if value is None else None,
            )
        folder_account.sub_accounts.append(new_account)

    def print_structure(self, asset_db: AssetDatabase) -> str:
        return (
            f"{self.account.print_structure(asset_db)}\n"
            f"{self.fx_market}"
        )

    def print_summary(
            self,
            asset_db: AssetDatabase,
            path: AccountPath|None = None,
            unit: str|None = None,
        ) -> str:
        return (
            f"Statement: {self.date.date().isoformat()}\n"
            f"{self.get_account(path).print_account_summary(
                asset_db, self.fx_market, unit=unit
            )}"
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
                        f"{k[0]}/{k[1]}: {v} "
                        f"-> {other.fx_market.quotes[k]}\n"
                    )
            else:
                res_fx += (
                    f"{k[0]}/{k[1]}: {v} "
                    "-> Not present in other statement\n"
                )

        for (k, v) in other.fx_market.quotes.items():
            if k not in self.fx_market.quotes:
                res_fx += (
                    f"{k[0]}/{k[1]}: "
                    f"Not present in this statement -> {round(v,6)}\n"
                )
        if len(res_fx) > 0:
            res += "FX Market Differences:\n"
            res += res_fx
        return res


def initialize_statement(unit: Asset) -> Statement:
    """Initialize a statement with a given unit and the current date."""
    fx_mkt = FxMarket()
    asset_db = AssetDatabase()
    asset_db.add_asset(unit)
    return Statement(
        dt.datetime.now(tz=dt.timezone.utc),
        asset_db,
        fx_mkt,
        Account(name="root", unit=unit.name, sub_accounts=[]),
    )

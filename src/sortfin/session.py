from __future__ import annotations

from typing import TYPE_CHECKING

from .account import Account
from .asset_database import AssetDatabase
from .fx_market import FxMarket
from .statement import Statement

if TYPE_CHECKING:
    import datetime as dt

    from .account_path import AccountPath
    from .asset import Asset


class Session:
    def __init__(
            self,
            asset_db: AssetDatabase|None = None,
        ) -> None:
        self.asset_db: AssetDatabase = asset_db \
            if asset_db is not None else AssetDatabase()
        self.data : dict[dt.datetime, Statement] = {}

    def get_statement(
            self,
            date: dt.datetime|None = None,
            *,
            exact_date: bool = False,
        ) -> Statement:
        """Get the statement for a specific date."""
        if date is None:
            if len(self.data) == 0:
                msg = "No statements available in session data"
                raise ValueError(msg)
            return self.data[max(self.data.keys())]

        if date not in self.data and exact_date:
            msg = f"Date {date} not found in session data"
            raise ValueError(msg)
        statement_date_list = [dte for dte in self.data if dte <= date]
        if len(statement_date_list) == 0:
            msg = f"No statement found before or on {date}"
            raise ValueError(msg)
        return self.data[max(statement_date_list)]

    def copy_session(self, date: dt.datetime) -> Statement:
        state = Session(
            date,
            self.asset_db.copy(),
        )
        state.data = self.data.copy()
        return state

    def copy_statement(
            self,
            date_copy: dt.datetime,
            date_paste: dt.datetime,
        ) -> None:
        if date_copy not in self.data:
            msg = f"Date {date_copy} not found in statement data"
            raise ValueError(msg)
        self.data[date_paste] = self.data[date_copy].copy()

    def print_structure(self, date: dt.datetime|None) -> str:
        """Print the structure of the session."""
        statement=self.get_statement(date)
        return (
            "Session:\n"
            f"Date: {statement.date.strftime("%d/%m/%Y")}\n"
            "Statement:\n"
            f"{statement.print_structure(self.asset_db)}"
            "\n"
        )

    def print_summary(self, date:dt.datetime, acc_path: AccountPath) -> str:
        """Print a summary of the session."""
        statement = self.get_statement(date)
        return (
            "Session:\n"
            f"Date: {statement.date.strftime('%d/%m/%Y')}\n"
            "Statement Summary:\n"
            f"{statement.print_summary(self.asset_db, acc_path)}"
            "\n"
        )

    def get_account(self, folder_path: AccountPath) -> Account:
        """Get the account at the specified folder path."""
        statement = self.get_statement()
        return statement.account.get_account(folder_path)

    def get_fxmarket(self) -> FxMarket:
        """Get the FX market for the current statement."""
        statement = self.get_statement()
        return statement.fx_market

    def add_account(self, folder_path: AccountPath, new_account: Account|str) -> None:
        """Add a new account to the session."""
        statement = self.get_statement()
        statement.add_account(folder_path, new_account)

def initialize_session(
        asset: Asset,
        date: dt.datetime,
    ) -> Session:
    """Initialize a new session with an optional asset database."""
    adb=AssetDatabase()
    adb.add_asset(asset)
    res = Session(adb)
    res.data[date] = Statement(
        date,
        fx_mkt=FxMarket(),
        acc=Account("root", asset.name, sub_accounts=[]),
    )
    return res

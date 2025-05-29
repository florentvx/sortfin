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

    def dates(self) -> list[dt.datetime]:
        """Get the list of dates for which statements are available."""
        return sorted(self.data.keys())

    def get_date(
            self,
            date: dt.datetime|None = None,
            *,
            is_exact_date: bool = False,
            is_before: bool = False,
            is_after: bool = False,
        ) -> dt.datetime:
        """Get the date for a specific statement."""
        if is_after and is_before:
            msg = "Cannot specify both is_after and is_before"
            raise ValueError(msg)
        if date is None:
            if len(self.data) == 0:
                msg = "No statements available in session data"
                raise ValueError(msg)
            return max(self.dates())
        if not (is_exact_date or is_before or is_after):
            msg = "Must specify at least one of is_exact_date, is_before, or is_after"
            raise ValueError(msg)
        is_exact_date_only = is_exact_date and not (is_before or is_after)
        if date not in self.data and is_exact_date_only:
            msg = f"Date {date} not found in session data"
            raise ValueError(msg)
        if is_exact_date and date in self.data:
                return date
        if is_before:
            statement_date_list = [dte for dte in self.data if dte < date]
            if len(statement_date_list) == 0:
                msg = f"No statement found before or on {date}"
                raise ValueError(msg)
            return max(statement_date_list)
        assert is_after # noqa: S101
        statement_date_list = [dte for dte in self.data if dte > date]
        if len(statement_date_list) == 0:
            msg = f"No statement found after or on {date}"
            raise ValueError(msg)
        return min(statement_date_list)

    def get_statement(
            self,
            date: dt.datetime|None = None,
            *,
            is_exact_date: bool = True,
            is_before: bool = False,
            is_after: bool = False,
        ) -> Statement:
        return self.data[
            self.get_date(
                date,
                is_exact_date=is_exact_date,
                is_before=is_before,
                is_after=is_after,
            )
        ]

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
        self.data[date_paste] = self.data[date_copy].copy(date=date_paste)

    def diff(
            self,
            date1: dt.datetime,
            date2: dt.datetime,
        ) -> str:
        """Get the difference between two statements."""
        if date1 not in self.data or date2 not in self.data:
            msg = "Both dates must be present in session data"
            raise ValueError(msg)
        statement1 = self.data[date1]
        statement2 = self.data[date2]
        return statement1.diff(statement2)

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

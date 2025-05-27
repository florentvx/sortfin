import datetime as dt
import unittest

from src.sortfin.account_path import AccountPath
from src.sortfin.session import Session

from .test_assetdb import ASSET_DB
from .test_statement import STATEMENT


class TestSession(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Session(ASSET_DB)
        self.session.data[STATEMENT.date] = STATEMENT.copy()
        self.new_date = STATEMENT.date + dt.timedelta(days=1)
        self.session.copy_statement(
            STATEMENT.date,
            self.new_date,
        )
        self.session.data[self.new_date].fx_market.modify_quote(
            "EUR", "USD", 1.1,
        )
        self.session.data[self.new_date].account.get_account(
            AccountPath("europe/my_bank"),
        ).value = 2000

    def test_get_statement(self) -> None:
        statement = self.session.get_statement(STATEMENT.date)
        self.assertEqual(statement.date, STATEMENT.date) #noqa: PT009
        self.assertEqual(statement.fx_market, STATEMENT.fx_market) #noqa: PT009
        self.assertEqual(statement.account, STATEMENT.account) #noqa: PT009

    def test_diff(self) -> None:
        test = self.session.diff(
            STATEMENT.date,
            self.new_date,
        )
        ref = (
            "Date: 2025-01-05 00:00:00+00:00 -> 2025-01-06 00:00:00+00:00\n"
            "Account Structure Differences:\n"
            "Account Differences for root/europe/my_bank:\n"
            "Value: 1000 -> 2000\n"
            "FX Market Differences:\n"
            "EUR/USD: 1.05 -> 1.1\n"
        )
        return test==ref

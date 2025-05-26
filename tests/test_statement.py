import datetime as dt
import unittest

import pytest

from src.sortfin import Account, AccountPath, Asset, Statement

from .test_asset import EUR, GBP, JPY, USD
from .test_assetdb import ASSET_DB
from .test_fx_market import FXM

ACC_TEST = Account("root", unit=EUR.name,
    sub_accounts=[
        Account("europe", unit=EUR.name,
            sub_accounts=[
                Account("my_bank", unit=EUR.name, value=1000),
                Account("my_loan", unit=EUR.name, value=-100),
            ],
        ),
        Account("usa", unit=USD.name,
            sub_accounts=[
                Account("my_bank", unit=USD.name, value=250),
                Account("my_investment", unit=USD.name, value=145600.2),
            ],
        ),
    ],
)

class TestStatement(unittest.TestCase):

    TZ = dt.timezone.utc

    def setUp(self) -> None:
        self.my_state = Statement(
            dt.datetime(2025, 1, 5, tzinfo=self.TZ), FXM, ACC_TEST,
        )
        self.my_state2=self.my_state.copy(
            dt.datetime(2025, 2, 5, tzinfo=self.TZ),
        )
        self.my_state3=self.my_state.copy(
            dt.datetime(2025, 3, 5, tzinfo=self.TZ),
        )
        self.my_state4=self.my_state.copy(
            dt.datetime(2025, 4, 5, tzinfo=self.TZ),
        )

    def test_copy_statement(self) -> None:
        assert self.my_state.date == dt.datetime(2025, 1, 5, tzinfo=self.TZ) # noqa: S101
        assert self.my_state2.date == dt.datetime(2025, 2, 5, tzinfo=self.TZ) # noqa: S101
        assert self.my_state3.date == dt.datetime(2025, 3, 5, tzinfo=self.TZ) # noqa: S101
        assert self.my_state4.date == dt.datetime(2025, 4, 5, tzinfo=self.TZ) # noqa: S101

    def test_change_terminal_account(self) -> None:
        new_value = 100
        self.my_state2.change_terminal_account(
            AccountPath("europe/my_bank"),
            value=new_value,
        )
        assert self.my_state2.get_account( # noqa: S101
            AccountPath("europe/my_bank"),
        ).value == new_value
        new_jpy_value = 123456
        self.my_state3.change_terminal_account(
            AccountPath("usa/my_investment"),
            value=new_jpy_value,
            unit=JPY.name,
        )
        assert self.my_state3.get_account( # noqa: S101
            AccountPath("usa/my_investment"),
        ).value == new_jpy_value
        assert self.my_state3.get_account( # noqa: S101
            AccountPath("usa/my_investment"),
        ).unit == JPY.name

    def test_change_folder_account(self) -> None:
        self.my_state4.change_folder_account(AccountPath("europe"), unit=GBP.name)
        assert self.my_state4.get_account(AccountPath("europe")).unit == GBP.name # noqa: S101

    def test_invalid_change_terminal_account(self) -> None:
        with pytest.raises(
            ValueError,
            match=r"account: \[.*\] is not terminal",
            ):
            self.my_state3.change_terminal_account(AccountPath("usa"), unit=EUR)

    def test_print_summary(self) -> None:
        current_adb = ASSET_DB.copy()
        ps1 = self.my_state.print_structure(current_adb)
        self.my_state2.change_terminal_account(
            AccountPath("europe/my_bank"), value=100,
        )
        ps2 = self.my_state2.print_summary(current_adb)
        self.my_state3.change_terminal_account(
            AccountPath("usa/my_investment"), value=123456, unit=JPY.name,
        )
        ps3 = self.my_state3.print_summary(current_adb)
        asset_btc = Asset("BTC", "B", decimal_param=6)
        current_adb.add_asset(asset_btc)
        self.my_state4.change_folder_account(AccountPath("europe"), unit=asset_btc)
        self.my_state4.fx_market.add_quote(
            current_adb, asset_btc.name, JPY.name, 140000,
        )
        ps4 = self.my_state4.print_summary(current_adb)

        assert ps1 is not None # noqa: S101
        assert ps2 is not None # noqa: S101
        assert ps3 is not None # noqa: S101
        assert ps4 is not None # noqa: S101

        log_2 = self.my_state.diff(self.my_state2)
        bmk_2 = (
            "Date: 2025-01-05 00:00:00+00:00 -> 2025-02-05 00:00:00+00:00\n"
            "Account Structure Differences:\n"
            "Account Differences for root/europe/my_bank:\n"
            "Value: 1000 -> 100\n"
        )
        if log_2 != bmk_2:
            assert log_2 == bmk_2 # noqa: S101

        log_3 = self.my_state.diff(self.my_state3)
        bmk_3 = (
            "Date: 2025-01-05 00:00:00+00:00 -> 2025-03-05 00:00:00+00:00\n"
            "Account Structure Differences:\n"
            "Account Differences for root/usa/my_investment:\n"
            "Unit: USD -> JPY\nValue: 145600.2 -> 123456\n"
        )
        if log_3 != bmk_3:
            assert log_3 == bmk_3 # noqa: S101

        log_4 = self.my_state.diff(self.my_state4)
        bmk_4 = (
            "Date: 2025-01-05 00:00:00+00:00 -> 2025-04-05 00:00:00+00:00\n"
            "Account Structure Differences:\n"
            "Account Differences for root/europe:\n"
            "Unit: EUR -> BTC\n"
            "FX Market Differences:\n"
            "BTC/JPY: Not present in this statement -> 140000\n"
        )
        if log_4 != bmk_4:
            assert log_4 == bmk_4 # noqa: S101


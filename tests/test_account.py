from __future__ import annotations

import unittest

import pytest

from src.sortfin.account import Account
from src.sortfin.account_path import AccountPath
from src.sortfin.colors import Color

from .test_asset import EUR, JPY
from .test_assetdb import ASSET_DB
from .test_fx_market import FXM

ACC = Account("acc", value = 100, unit=EUR.name)
ACC_EMPTY = Account("acc_sv_2", sub_accounts=[], unit=EUR.name)
ACC_SA01 = Account("sa01", value = 12, unit = EUR.name)
JPY_ACC = Account("x", value=100000, unit = JPY.name)
ACC_2 = Account("acc2", sub_accounts=[
    Account("sa0", value = 102, unit = EUR.name),
    Account("sa1", sub_accounts= [
        Account("sa00", value = 52, unit = EUR.name),
        ACC_SA01,
    ], unit = EUR.name),
    Account("sa3", sub_accounts=[
        JPY_ACC,
        Account("y", sub_accounts=[], unit = JPY.name),
    ], unit = JPY.name),
], unit = EUR.name)

class TestAccount(unittest.TestCase):

    def test_init(self) -> None:
        with pytest.raises(TypeError):
            Account("Error")
        with pytest.raises(TypeError):
            Account("Error", value=None)
        with pytest.raises(TypeError):
            Account("Error", sub_accounts=None)

    def test_is_terminal(self) -> None:
        terminal = Account("singleton", value=10, unit=EUR.name)
        if not terminal.is_terminal:
            msg="Terminal account should be terminal"
            raise AssertionError(msg)

        intermediary_empty = Account("int_empty", sub_accounts=[], unit=EUR.name)
        if intermediary_empty.is_terminal:
            msg="Intermediary account should not be terminal"
            raise AssertionError(msg)

    def test_set_value(self) -> None:
        acc1 = Account("acc_sv_1", value=0, unit=EUR.name)
        val=101
        acc1.set_value(val)
        if acc1.value != val:
            msg="Value should be set to 101"
            raise AssertionError(msg)

        with pytest.raises(
            ValueError,
            match="cannot set value on a intermediary account",
            ):
            ACC_EMPTY.set_value(101)

    def test_get_account(self) -> None:
        acc_p = AccountPath("a/x")
        acc_p2 = AccountPath("sa0/y")
        acc_p3 = AccountPath("Sa1/sA01")
        acc_p4 = AccountPath("sa3/x")

        assert ACC_2.get_account(None) == ACC_2 #noqa: S101
        assert ACC.get_account(None) == ACC #noqa: S101
        assert ACC.get_account(AccountPath("")) == ACC #noqa: S101

        with pytest.raises(
            ValueError,
            match=f"no match for {acc_p.root_folder} in {ACC_2.name}",
            ):
            ACC_2.get_account(acc_p)
        with pytest.raises(
            ValueError,
            match=f"account {acc_p2.parent} is terminal and cannot have sub_accounts",
            ):
            ACC_2.get_account(acc_p2)
        assert ACC_2.get_account(acc_p3) == ACC_SA01 #noqa: S101
        assert ACC_2.get_account(acc_p4) == JPY_ACC #noqa: S101


    def test_get_account_structure(self) -> None:
        expected_structure = (
            f"Account Structure:\n {Color.RED}0{Color.RESET}. {Color.GREEN}acc2{Color.RESET} : EUR\n"  # noqa: E501
            f"   {Color.RED}1{Color.RESET}. {Color.GREEN}sa0{Color.RESET} : EUR -> {Color.YELLOW}€ 102{Color.RESET}\n"  # noqa: E501
            f"   {Color.RED}1{Color.RESET}. {Color.GREEN}sa1{Color.RESET} : EUR\n"
            f"     {Color.RED}2{Color.RESET}. sa1/{Color.GREEN}sa00{Color.RESET} : EUR -> {Color.YELLOW}€ 52{Color.RESET}\n"  # noqa: E501
            f"     {Color.RED}2{Color.RESET}. sa1/{Color.GREEN}sa01{Color.RESET} : EUR -> {Color.YELLOW}€ 12{Color.RESET}\n"  # noqa: E501
            f"   {Color.RED}1{Color.RESET}. {Color.GREEN}sa3{Color.RESET} : JPY\n"
            f"     {Color.RED}2{Color.RESET}. sa3/{Color.GREEN}x{Color.RESET} : JPY -> {Color.YELLOW}¥ 10,0000{Color.RESET}\n"  # noqa: E501
            f"     {Color.RED}2{Color.RESET}. sa3/{Color.GREEN}y{Color.RESET} : JPY\n"
        )
        assert ACC_2.print_structure(ASSET_DB) == expected_structure #noqa: S101

        expected_summary = (
            f"Account Summary: {Color.RED}acc2{Color.RESET} {Color.YELLOW}EUR{Color.RESET}\n"  # noqa: E501
            f"{Color.CYAN}sa0{Color.RESET}:                {Color.GREEN}€ 102{Color.RESET}                    {Color.GREEN}€ 102{Color.RESET}\n" # noqa: E501
            f"{Color.CYAN}sa1{Color.RESET}:                {Color.GREEN}€ 64{Color.RESET}                     {Color.GREEN}€ 64{Color.RESET}\n" # noqa: E501
            f"{Color.CYAN}sa3{Color.RESET}:                {Color.GREEN}¥ 10,0000{Color.RESET}                {Color.GREEN}€ 714.29{Color.RESET}\n" # noqa: E501
            f"{Color.YELLOW}TOTAL{Color.RESET}:              {Color.MAGENTA}{Color.RESET}                         {Color.GREEN}€ 880.29{Color.RESET}\n" # noqa: E501
        )
        assert ACC_2.print_account_summary(ASSET_DB, FXM) == expected_summary #noqa: S101


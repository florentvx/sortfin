from __future__ import annotations
import unittest
from sortfin.account_path import account_path
from sortfin.account import account

from .test_asset import EUR, JPY
from .test_fx_market import FXM

ACC = account("acc", value = 100, unit=EUR)
ACC_EMPTY = account("acc_sv_2", sub_accounts=[], unit=EUR)
ACC_SA01 = account("sa01", value = 12, unit = EUR)
JPY_ACC = account("x", value=100000, unit = JPY)
ACC_2 = account("acc2", sub_accounts=[
    account("sa0", value = 102, unit = EUR),
    account("sa1", sub_accounts= [
        account("sa00", value = 52, unit = EUR),
        ACC_SA01,
    ], unit = EUR),
    account("sa3", sub_accounts=[
        JPY_ACC,
        account("y", sub_accounts=[], unit = JPY),
    ], unit = JPY),
], unit = EUR)

class TestAccount(unittest.TestCase):

    def test_init(self):
        with self.assertRaises(TypeError):
            account("Error")
        with self.assertRaises(TypeError):
            account("Error", value=None)
        with self.assertRaises(TypeError):
            account("Error", sub_accounts=None)

    def test_is_terminal(self):
        terminal = account("singleton", value=10, unit=EUR)
        self.assertTrue(terminal.is_terminal)

        intermediary_empty = account("int_empty", sub_accounts=[], unit=EUR)
        self.assertFalse(intermediary_empty.is_terminal)

    def test_set_value(self):
        acc1 = account("acc_sv_1", value=0, unit=EUR)
        acc1.set_value(101)
        self.assertEqual(acc1.value, 101)

        with self.assertRaises(ValueError):
            ACC_EMPTY.set_value(101)
    
    def test_get_account(self):
        acc_p = account_path("a/x")
        acc_p2 = account_path("sa0/y")
        acc_p3 = account_path("Sa1/sA01")
        acc_p4 = account_path("sa3/x")

        self.assertEqual(ACC_2.get_account(None), ACC_2)
        self.assertEqual(ACC.get_account(None), ACC)
        self.assertEqual(ACC.get_account(account_path("")), ACC)

        with self.assertRaises(ValueError):
            ACC_2.get_account(acc_p)
        with self.assertRaises(ValueError):
            ACC_2.get_account(acc_p2)
        self.assertEqual(ACC_2.get_account(acc_p3), ACC_SA01)
        self.assertEqual(ACC_2.get_account(acc_p4), JPY_ACC)


    def test_get_account_structure(self):
        expected_structure = ' 0. acc2 : EUR\n   1. acc2/sa0 -> € 102\n   1. acc2/sa1 : EUR\n' + \
            '     2. acc2/sa1/sa00 -> € 52\n     2. acc2/sa1/sa01 -> € 12\n   1. acc2/sa3 : JPY\n' + \
            '     2. acc2/sa3/x -> ¥ 10,0000\n     2. acc2/sa3/y : JPY\n'
        self.assertEqual(ACC_2.print_structure(), expected_structure)

        expected_summary = 'sa0:       € 102          € 102\nsa1:       € 64           € 64\n' + \
            'sa3:       ¥ 10,0000      € 714.29\n'
        self.assertEqual(ACC_2.print_account_summary(FXM), expected_summary)

    
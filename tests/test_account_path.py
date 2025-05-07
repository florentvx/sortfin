import unittest

import pytest

from src.sortfin.account_path import AccountPath, AccountPathError


class TestAccountPath(unittest.TestCase):

    def do_test_path(self, my_path: str) -> str:
        ap = AccountPath(my_path)
        return (
            f"{ap!s}_{ap.is_empty}_{ap.is_singleton}_"
            f"{ap.root_folder}_{ap.get_child()!s}"
        )

    def test_account_path(self) -> None:
        if self.do_test_path("") != "._True_False_None_.":
            msg="Empty path test failed"
            raise AssertionError(msg)
        if self.do_test_path("root/a/b/c/") != "root/a/b/c_False_False_root_a/b/c":
            msg="[root/a/b/c/] test failed"
            raise AssertionError(msg)
        if self.do_test_path("root2/z/y") != "root2/z/y_False_False_root2_z/y":
            msg="[root2/z/y] test failed"
            raise AssertionError(msg)
        if self.do_test_path("folder") != "folder_False_True_folder_.":
            msg="[folder] test failed"
            raise AssertionError(msg)
        if self.do_test_path("folder/") != "folder_False_True_folder_.":
            msg="[folder/] test failed"
            raise AssertionError(msg)

    def test_invalid_path(self) -> None:
        with pytest.raises(AccountPathError):
            self.do_test_path("/R3/1/5/")

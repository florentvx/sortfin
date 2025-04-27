import unittest
from src.sortfin.account_path import account_path


class TestAccountPath(unittest.TestCase):

    def do_test_path(self, my_path: str):
        ap = account_path(my_path)
        return f"{str(ap)}_{ap.is_empty}_{ap.is_singleton}_{ap.root_folder}_{str(ap.get_child())}"

    def test_account_path(self):
        self.assertEqual(self.do_test_path(""), "._True_False_None_.")
        self.assertEqual(self.do_test_path("root/a/b/c/"), "root/a/b/c_False_False_root_a/b/c")
        self.assertEqual(self.do_test_path("root2/z/y"), "root2/z/y_False_False_root2_z/y")
        self.assertEqual(self.do_test_path("folder"), "folder_False_True_folder_.")

    def test_invalid_path(self):
        # with self.assertRaises(TypeError):
        #    self.do_test_path(None)
        with self.assertRaises(ValueError):
            self.do_test_path("/R3/1/5/")
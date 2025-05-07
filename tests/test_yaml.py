
import unittest


class TestYamlPackage(unittest.TestCase):
    def test_yaml(self) -> None:
        import yaml
        assert len(dir(yaml)) > 0, "YAML module is not available or empty" #noqa: S101
        assert hasattr(yaml, "safe_load"), "YAML module does not have safe_load method" #noqa: S101
        assert hasattr(yaml, "safe_dump"), "YAML module does not have safe_dump method" #noqa: S101

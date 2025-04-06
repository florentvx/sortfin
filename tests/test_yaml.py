def test_yaml():
    import yaml
    assert len(dir(yaml)) > 0, "YAML module is not available or empty"
    assert hasattr(yaml, 'safe_load'), "YAML module does not have safe_load method"
    assert hasattr(yaml, 'safe_dump'), "YAML module does not have safe_dump method"

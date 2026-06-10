def dummy_upper(value):
    """Test Jinja2 filter: uppercases a string."""
    return str(value).upper()


filters = {
    'dummy_upper': dummy_upper,
}

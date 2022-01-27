def linkify_phone(value):
    """
    Render a telephone number as a hyperlink.
    """
    if value is None:
        return None
    return f"tel:{value}"

def is_script(obj):
    """
    Returns True if the object is a Script.
    """
    from .scripts import Script
    try:
        return issubclass(obj, Script) and obj != Script
    except TypeError:
        return False


def is_report(obj):
    """
    Returns True if the given object is a Report.
    """
    from .reports import Report
    try:
        return issubclass(obj, Report) and obj != Report
    except TypeError:
        return False

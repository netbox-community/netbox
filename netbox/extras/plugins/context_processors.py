from extras.registry import registry


def plugin_menu_items(request):
    """
    Retrieve and expose all plugin registered navigation menu items.
    """
    return {
        'plugin_menu_items': registry['plugin_menu_items']
    }

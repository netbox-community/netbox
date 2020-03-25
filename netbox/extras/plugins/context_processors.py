from extras.registry import registry


def nav_menu_links(request):
    """
    Retrieve and expose all plugin registered nav links
    """
    return {
        'plugin_nav_menu_links': registry['plugin_nav_menu_links']
    }

from . import get_nav_menu_link_classes


def nav_menu_links(request):
    """
    Retrieve and expose all plugin registered nav links
    """
    nav_menu_links = get_nav_menu_link_classes()

    return {
        'plugin_nav_menu_links': nav_menu_links
    }

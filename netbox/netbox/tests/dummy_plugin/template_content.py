from netbox.plugins.templates import PluginTemplateExtension


class GlobalContent(PluginTemplateExtension):

    def navbar(self):
        return "GLOBAL CONTENT - NAVBAR"


class SiteContent(PluginTemplateExtension):
    models = ['dcim.site']

    def buttons(self):
        return "SITE CONTENT - BUTTONS"

    def alerts(self):
        return "SITE CONTENT - ALERTS"

    def left_page(self):
        return "SITE CONTENT - LEFT PAGE"

    def right_page(self):
        return "SITE CONTENT - RIGHT PAGE"

    def full_width_page(self):
        return "SITE CONTENT - FULL WIDTH PAGE"

    def list_buttons(self):
        return "SITE CONTENT - LIST BUTTONS"


template_extensions = [GlobalContent, SiteContent]

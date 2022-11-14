from extras.plugins import PluginTemplateExtension


class SiteContent(PluginTemplateExtension):
    model = 'dcim.site'

    def left_page(self):
        return "SITE CONTENT - LEFT PAGE"

    def right_page(self):
        return "SITE CONTENT - RIGHT PAGE"

    def full_width_page(self):
        return "SITE CONTENT - FULL WIDTH PAGE"

    def buttons(self):
        return "SITE CONTENT - BUTTONS"

    def list_buttons(self):
        return "SITE CONTENT - LIST BUTTONS"


template_extensions = [SiteContent]

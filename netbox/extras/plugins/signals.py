import django.dispatch
from django.dispatch.dispatcher import NO_RECEIVERS


class PluginSignal(django.dispatch.Signal):

    def _sorted_receivers(self, sender):
        orig_list = self._live_receivers(sender)
        sorted_list = sorted(
            orig_list,
            key=lambda receiver: (
                receiver.__module__,
                receiver.__name__,
            )
        )
        return sorted_list

    def send(self, sender, **kwargs):
        responses = []
        if not self.receivers or self.sender_receivers_cache.get(sender) is NO_RECEIVERS:
            return responses

        for receiver in self._sorted_receivers(sender):
            response = receiver(signal=self, sender=sender, **kwargs)
            responses.append((receiver, response))
        return responses


"""
This signal collects template content classes which render content for object detail pages
"""
register_detail_page_content_classes = PluginSignal(
    providing_args=[]
)


"""
This signal collects nav menu link classes
"""
register_nav_menu_link_classes = PluginSignal(
    providing_args=[]
)

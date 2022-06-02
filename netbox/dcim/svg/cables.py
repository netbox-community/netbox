import svgwrite
from svgwrite.container import Group, Hyperlink
from svgwrite.shapes import Line, Rect
from svgwrite.text import Text

from django.conf import settings

from utilities.utils import foreground_color


__all__ = (
    'CableTraceSVG',
)


OFFSET = 0.5
PADDING = 10
LINE_HEIGHT = 20


class CableTraceSVG:
    """
    Generate a graphical representation of a CablePath in SVG format.

    :param origin: The originating termination
    :param width: Width of the generated image (in pixels)
    :param base_url: Base URL for links within the SVG document. If none, links will be relative.
    """
    def __init__(self, origin, width=400, base_url=None):
        self.origin = origin
        self.width = width
        self.base_url = base_url.rstrip('/') if base_url is not None else ''

        # Establish a cursor to track position on the y axis
        # Center edges on pixels to render sharp borders
        self.cursor = OFFSET

    @property
    def center(self):
        return self.width / 2

    @classmethod
    def _get_labels(cls, instance):
        """
        Return a list of text labels for the given instance based on model type.
        """
        labels = [str(instance)]
        if instance._meta.model_name == 'device':
            labels.append(f'{instance.device_type.manufacturer} {instance.device_type}')
            location_label = f'{instance.site}'
            if instance.location:
                location_label += f' / {instance.location}'
            if instance.rack:
                location_label += f' / {instance.rack}'
            labels.append(location_label)
        elif instance._meta.model_name == 'circuit':
            labels[0] = f'Circuit {instance}'
            labels.append(instance.provider)
        elif instance._meta.model_name == 'circuittermination':
            if instance.xconnect_id:
                labels.append(f'{instance.xconnect_id}')
        elif instance._meta.model_name == 'providernetwork':
            labels.append(instance.provider)

        return labels

    @classmethod
    def _get_color(cls, instance):
        """
        Return the appropriate fill color for an object within a cable path.
        """
        if hasattr(instance, 'parent_object'):
            # Termination
            return 'f0f0f0'
        if hasattr(instance, 'device_role'):
            # Device
            return instance.device_role.color
        else:
            # Other parent object
            return 'e0e0e0'

    def _draw_box(self, width, color, url, labels, y_indent=0, padding_multiplier=1, radius=10):
        """
        Return an SVG Link element containing a Rect and one or more text labels representing a
        parent object or cable termination point.

        :param width: Box width
        :param color: Box fill color
        :param url: Hyperlink URL
        :param labels: Iterable of text labels
        :param y_indent: Vertical indent (for overlapping other boxes) (default: 0)
        :param padding_multiplier: Add extra vertical padding (default: 1)
        :param radius: Box corner radius (default: 10)
        """
        self.cursor -= y_indent

        # Create a hyperlink
        link = Hyperlink(href=f'{self.base_url}{url}', target='_blank')

        # Add the box
        position = (
            OFFSET + (self.width - width) / 2,
            self.cursor
        )
        height = PADDING * padding_multiplier \
            + LINE_HEIGHT * len(labels) \
            + PADDING * padding_multiplier
        box = Rect(position, (width - 2, height), rx=radius, class_='parent-object', style=f'fill: #{color}')
        link.add(box)
        self.cursor += PADDING * padding_multiplier

        # Add text label(s)
        for i, label in enumerate(labels):
            self.cursor += LINE_HEIGHT
            text_coords = (self.center, self.cursor - LINE_HEIGHT / 2)
            text_color = f'#{foreground_color(color, dark="303030")}'
            text = Text(label, insert=text_coords, fill=text_color, class_='bold' if not i else [])
            link.add(text)

        self.cursor += PADDING * padding_multiplier

        return link

    def _draw_cable(self, color, url, labels):
        """
        Return an SVG group containing a line element and text labels representing a Cable.

        :param color: Cable (line) color
        :param url: Hyperlink URL
        :param labels: Iterable of text labels
        """
        group = Group(class_='connector')

        # Draw a "shadow" line to give the cable a border
        start = (OFFSET + self.center, self.cursor)
        height = PADDING * 2 + LINE_HEIGHT * len(labels) + PADDING * 2
        end = (start[0], start[1] + height)
        cable_shadow = Line(start=start, end=end, class_='cable-shadow')
        group.add(cable_shadow)

        # Draw the cable
        cable = Line(start=start, end=end, style=f'stroke: #{color}')
        group.add(cable)

        self.cursor += PADDING * 2

        # Add link
        link = Hyperlink(href=f'{self.base_url}{url}', target='_blank')

        # Add text label(s)
        for i, label in enumerate(labels):
            self.cursor += LINE_HEIGHT
            text_coords = (self.center + PADDING * 2, self.cursor - LINE_HEIGHT / 2)
            text = Text(label, insert=text_coords, class_='bold' if not i else [])
            link.add(text)

        group.add(link)
        self.cursor += PADDING * 2

        return group

    def _draw_wirelesslink(self, url, labels):
        """
        Draw a line with labels representing a WirelessLink.

        :param url: Hyperlink URL
        :param labels: Iterable of text labels
        """
        group = Group(class_='connector')

        # Draw the wireless link
        start = (OFFSET + self.center, self.cursor)
        height = PADDING * 2 + LINE_HEIGHT * len(labels) + PADDING * 2
        end = (start[0], start[1] + height)
        line = Line(start=start, end=end, class_='wireless-link')
        group.add(line)

        self.cursor += PADDING * 2

        # Add link
        link = Hyperlink(href=f'{self.base_url}{url}', target='_blank')

        # Add text label(s)
        for i, label in enumerate(labels):
            self.cursor += LINE_HEIGHT
            text_coords = (self.center + PADDING * 2, self.cursor - LINE_HEIGHT / 2)
            text = Text(label, insert=text_coords, class_='bold' if not i else [])
            link.add(text)

        group.add(link)
        self.cursor += PADDING * 2

        return group

    def _draw_attachment(self):
        """
        Return an SVG group containing a line element and "Attachment" label.
        """
        group = Group(class_='connector')

        # Draw attachment (line)
        start = (OFFSET + self.center, OFFSET + self.cursor)
        height = PADDING * 2 + LINE_HEIGHT + PADDING * 2
        end = (start[0], start[1] + height)
        line = Line(start=start, end=end, class_='attachment')
        group.add(line)
        self.cursor += PADDING * 4

        return group

    def render(self):
        """
        Return an SVG document representing a cable trace.
        """
        from dcim.models import Cable
        from wireless.models import WirelessLink

        traced_path = self.origin.trace()

        # Prep elements list
        parent_objects = []
        terminations = []
        connectors = []

        # Iterate through each (term, cable, term) segment in the path
        for i, segment in enumerate(traced_path):
            near_end, connector, far_end = segment

            # Near end parent
            if i == 0:
                # If this is the first segment, draw the originating termination's parent object
                parent_object = self._draw_box(
                    width=self.width,
                    color=self._get_color(near_end.parent_object),
                    url=near_end.parent_object.get_absolute_url(),
                    labels=self._get_labels(near_end.parent_object),
                    padding_multiplier=2
                )
                parent_objects.append(parent_object)

            # Near end termination
            if near_end is not None:
                termination = self._draw_box(
                    width=self.width * .8,
                    color=self._get_color(near_end),
                    url=near_end.get_absolute_url(),
                    labels=self._get_labels(near_end),
                    y_indent=PADDING,
                    radius=5
                )
                terminations.append(termination)

            # Connector (a Cable or WirelessLink)
            if connector is not None:

                # Cable
                if type(connector) is Cable:
                    connector_labels = [
                        f'Cable {connector}',
                        connector.get_status_display()
                    ]
                    if connector.type:
                        connector_labels.append(connector.get_type_display())
                    if connector.length and connector.length_unit:
                        connector_labels.append(f'{connector.length} {connector.get_length_unit_display()}')
                    cable = self._draw_cable(
                        color=connector.color or '000000',
                        url=connector.get_absolute_url(),
                        labels=connector_labels
                    )
                    connectors.append(cable)

                # WirelessLink
                elif type(connector) is WirelessLink:
                    connector_labels = [
                        f'Wireless link {connector}',
                        connector.get_status_display()
                    ]
                    if connector.ssid:
                        connector_labels.append(connector.ssid)
                    wirelesslink = self._draw_wirelesslink(
                        url=connector.get_absolute_url(),
                        labels=connector_labels
                    )
                    connectors.append(wirelesslink)

                # Far end termination
                termination = self._draw_box(
                    width=self.width * .8,
                    color=self._get_color(far_end),
                    url=far_end.get_absolute_url(),
                    labels=self._get_labels(far_end),
                    radius=5
                )
                terminations.append(termination)

                # Far end parent
                parent_object = self._draw_box(
                    width=self.width,
                    color=self._get_color(far_end.parent_object),
                    url=far_end.parent_object.get_absolute_url(),
                    labels=self._get_labels(far_end.parent_object),
                    y_indent=PADDING,
                    padding_multiplier=2
                )
                parent_objects.append(parent_object)

            elif far_end:

                # Attachment
                attachment = self._draw_attachment()
                connectors.append(attachment)

                # ProviderNetwork
                parent_object = self._draw_box(
                    width=self.width,
                    color=self._get_color(far_end),
                    url=far_end.get_absolute_url(),
                    labels=self._get_labels(far_end),
                    padding_multiplier=2
                )
                parent_objects.append(parent_object)

        # Determine drawing size
        self.drawing = svgwrite.Drawing(
            size=(self.width, self.cursor + 2)
        )

        # Attach CSS stylesheet
        with open(f'{settings.STATIC_ROOT}/cable_trace.css') as css_file:
            self.drawing.defs.add(self.drawing.style(css_file.read()))

        # Add elements to the drawing in order of depth (Z axis)
        for element in connectors + parent_objects + terminations:
            self.drawing.add(element)

        return self.drawing

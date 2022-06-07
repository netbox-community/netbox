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

TERMINATION_WIDTH = 80


class Node(Hyperlink):
    """
    Create a node to be represented in the SVG document as a rectangular box with a hyperlink.

    Arguments:
        position: (x, y) coordinates of the box's top left corner
        width: Box width
        url: Hyperlink URL
        color: Box fill color (RRGGBB format)
        labels: An iterable of text strings. Each label will render on a new line within the box.
        radius: Box corner radius, for rounded corners (default: 10)
    """

    def __init__(self, position, width, url, color, labels, radius=10, **extra):
        super(Node, self).__init__(href=url, target='_blank', **extra)

        x, y = position

        # Add the box
        dimensions = (width - 2, PADDING + LINE_HEIGHT * len(labels) + PADDING)
        box = Rect((x + OFFSET, y), dimensions, rx=radius, class_='parent-object', style=f'fill: #{color}')
        self.add(box)

        cursor = y + PADDING

        # Add text label(s)
        for i, label in enumerate(labels):
            cursor += LINE_HEIGHT
            text_coords = (x + width / 2, cursor - LINE_HEIGHT / 2)
            text_color = f'#{foreground_color(color, dark="303030")}'
            text = Text(label, insert=text_coords, fill=text_color, class_='bold' if not i else [])
            self.add(text)

    @property
    def box(self):
        return self.elements[0] if self.elements else None

    @property
    def top_center(self):
        return self.box['x'] + self.box['width'] / 2, self.box['y']

    @property
    def bottom_center(self):
        return self.box['x'] + self.box['width'] / 2, self.box['y'] + self.box['height']


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

        # Prep elements lists
        self.parent_objects = []
        self.terminations = []
        self.connectors = []

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

    def draw_parent_object(self, obj):
        node = Node(
            position=(0, self.cursor),
            width=self.width,
            url=obj.get_absolute_url(),
            color=self._get_color(obj),
            labels=self._get_labels(obj)
        )
        self.parent_objects.append(node)
        self.cursor += node.box['height']

    def draw_terminations(self, terminations):
        """
        Draw a row of terminating objects (e.g. interfaces) belonging to the same parent object, all of which
        are attached to the same end of a cable.
        """
        nodes = []
        nodes_height = 0
        x = self.width / 2 - len(terminations) * TERMINATION_WIDTH / 2

        for i, term in enumerate(terminations):
            node = Node(
                position=(x + i * TERMINATION_WIDTH, self.cursor),
                width=TERMINATION_WIDTH,
                url=term.get_absolute_url(),
                color=self._get_color(term),
                labels=self._get_labels(term),
                radius=5
            )
            nodes_height = max(nodes_height, node.box['height'])
            nodes.append(node)

        self.cursor += nodes_height
        self.terminations.extend(nodes)

        return nodes

    def draw_cable(self, color, url, labels):
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

    def draw_wirelesslink(self, url, labels):
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

    def draw_attachment(self):
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

        # Iterate through each (terms, cable, terms) segment in the path
        for i, segment in enumerate(traced_path):
            near_ends, connector, far_ends = segment

            # Near end parent
            if i == 0:
                # If this is the first segment, draw the originating termination's parent object
                self.draw_parent_object(near_ends[0].parent_object)

            # Near end termination
            self.draw_terminations(near_ends)

            # Connector (a Cable or WirelessLink)
            connector = connector[0]  # Remove Cable from list
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
                    cable = self.draw_cable(
                        color=connector.color or '000000',
                        url=connector.get_absolute_url(),
                        labels=connector_labels
                    )
                    self.connectors.append(cable)

                # WirelessLink
                elif type(connector) is WirelessLink:
                    connector_labels = [
                        f'Wireless link {connector}',
                        connector.get_status_display()
                    ]
                    if connector.ssid:
                        connector_labels.append(connector.ssid)
                    wirelesslink = self.draw_wirelesslink(
                        url=connector.get_absolute_url(),
                        labels=connector_labels
                    )
                    self.connectors.append(wirelesslink)

                # Far end termination
                self.draw_terminations(far_ends)

                # Far end parent
                self.draw_parent_object(far_ends[0].parent_object)

            elif far_ends:

                # Attachment
                attachment = self.draw_attachment()
                self.connectors.append(attachment)

                # ProviderNetwork
                self.draw_parent_object(far_ends[0])

        # Determine drawing size
        self.drawing = svgwrite.Drawing(
            size=(self.width, self.cursor + 2)
        )

        # Attach CSS stylesheet
        with open(f'{settings.STATIC_ROOT}/cable_trace.css') as css_file:
            self.drawing.defs.add(self.drawing.style(css_file.read()))

        # Add elements to the drawing in order of depth (Z axis)
        for element in self.connectors + self.parent_objects + self.terminations:
            self.drawing.add(element)

        return self.drawing

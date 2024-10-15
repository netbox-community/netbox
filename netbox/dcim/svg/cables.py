import svgwrite
from svgwrite.container import Group, Hyperlink
from svgwrite.shapes import Line, Polyline, Rect
from svgwrite.text import Text

from django.conf import settings

from dcim.constants import CABLE_TRACE_SVG_DEFAULT_WIDTH
from utilities.html import foreground_color

__all__ = (
    'CableTraceSVG',
)

OFFSET = 0.5
PADDING = 10
LINE_HEIGHT = 20
FANOUT_HEIGHT = 35
FANOUT_LEG_HEIGHT = 15
CABLE_HEIGHT = 5 * LINE_HEIGHT + FANOUT_HEIGHT + FANOUT_LEG_HEIGHT


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
        object: A copy of the object to allow reference when drawing cables to determine which cables are connected to
                which terminations.
    """

    object = None

    def __init__(self, position, width, url, color, labels, radius=10, object=object, **extra):
        super(Node, self).__init__(href=url, target='_parent', **extra)

        # Save object for reference by cable systems
        self.object = object

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


class Connector(Group):
    """
    Return an SVG group containing a line element and text labels representing a Cable.

    Arguments:
        color: Cable (line) color
        url: Hyperlink URL
        labels: Iterable of text labels
    """

    def __init__(self, start, url, color, wireless, labels=[], description=[], end=None, text_offset=0, **extra):
        super().__init__(class_="connector", **extra)

        self.start = start
        self.height = PADDING * 2 + LINE_HEIGHT * len(labels) + PADDING * 2
        # Allow to specify end-position or auto-calculate
        self.end = end if end else (start[0], start[1] + self.height)
        self.color = color or '000000'

        if wireless:
            # Draw the cable
            cable = Line(start=self.start, end=self.end, class_="wireless-link")
            self.add(cable)
        else:
            # Draw a "shadow" line to give the cable a border
            cable_shadow = Line(start=self.start, end=self.end, class_='cable-shadow')
            self.add(cable_shadow)

            # Draw the cable
            cable = Line(start=self.start, end=self.end, style=f'stroke: #{self.color}')
            self.add(cable)

        # Add link
        link = Hyperlink(href=url, target='_parent')

        # Add text label(s)
        cursor = start[1] + text_offset
        cursor += PADDING * 2 + LINE_HEIGHT * 2
        x_coord = (start[0] + end[0]) / 2 + PADDING
        for i, label in enumerate(labels):
            cursor += LINE_HEIGHT
            text_coords = (x_coord, cursor - LINE_HEIGHT / 2)
            text = Text(label, insert=text_coords, class_='bold' if not i else [])
            link.add(text)
        if len(description) > 0:
            link.set_desc("\n".join(description))

        self.add(link)


class CableTraceSVG:
    """
    Generate a graphical representation of a CablePath in SVG format.

    :param origin: The originating termination
    :param width: Width of the generated image (in pixels)
    :param base_url: Base URL for links within the SVG document. If none, links will be relative.
    """
    def __init__(self, origin, width=CABLE_TRACE_SVG_DEFAULT_WIDTH, base_url=None):
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
            if instance.position:
                location_label += f' / {instance.get_face_display()}'
                location_label += f' / U{instance.position}'
            labels.append(location_label)
        elif instance._meta.model_name == 'circuit':
            labels[0] = f'Circuit {instance}'
            labels.append(instance.type)
            labels.append(instance.provider)
            if instance.description:
                labels.append(instance.description)
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
            return getattr(instance, 'color', 'f0f0f0') or 'f0f0f0'
        if hasattr(instance, 'role'):
            # Device
            return instance.role.color
        elif instance._meta.model_name == 'circuit' and instance.type.color:
            return instance.type.color
        else:
            # Other parent object
            return 'e0e0e0'

    def draw_parent_objects(self, obj_list):
        """
        Draw a set of parent objects (eg hosts, switched, patchpanels) and return all created nodes
        """
        objects = []
        width = self.width / len(obj_list)
        for i, obj in enumerate(obj_list):
            node = Node(
                position=(i * width, self.cursor),
                width=width,
                url=f'{self.base_url}{obj.get_absolute_url()}',
                color=self._get_color(obj),
                labels=self._get_labels(obj),
                object=obj
            )
            objects.append(node)
            self.parent_objects.append(node)
            if i + 1 == len(obj_list):
                self.cursor += node.box['height']
        return objects

    def draw_object_terminations(self, terminations, offset_x, width):
        """
        Draw all terminations belonging to an object with specified offset and width
        Return all created nodes and their maximum height
        """
        nodes_height = 0
        nodes = []
        # Sort them by name to make renders more readable
        for i, term in enumerate(sorted(terminations, key=lambda x: str(x))):
            node = Node(
                position=(offset_x + i * width, self.cursor),
                width=width,
                url=f'{self.base_url}{term.get_absolute_url()}',
                color=self._get_color(term),
                labels=self._get_labels(term),
                radius=5,
                object=term
            )
            nodes_height = max(nodes_height, node.box['height'])
            nodes.append(node)
        return nodes, nodes_height

    def draw_terminations(self, terminations, parent_object_nodes):
        """
        Draw a row of terminating objects (e.g. interfaces) and return all created nodes
        Attach them to previously created parent objects
        """
        nodes = []
        nodes_height = 0

        # Draw terminations for each parent object
        for parent in parent_object_nodes:
            parent_terms = [term for term in terminations if term.parent_object == parent.object]

            # Width and offset(position) for each termination box
            width = parent.box['width'] / len(parent_terms)
            offset_x = parent.box['x']

            result, nodes_height = self.draw_object_terminations(parent_terms, offset_x, width)
            nodes.extend(result)

        self.cursor += nodes_height
        self.terminations.extend(nodes)

        return nodes

    def draw_far_objects(self, obj_list, terminations):
        """
        Draw the far-end objects and its terminations and return all created nodes
        """
        # Make sure elements are sorted by name for readability
        objects = sorted(obj_list, key=lambda x: str(x))
        width = self.width / len(objects)

        # Max-height of created terminations
        terms_height = 0
        term_nodes = []

        # Draw the terminations by per object first
        for i, obj in enumerate(objects):
            obj_terms = [term for term in terminations if term.parent_object == obj]
            obj_pos = i * width
            result, result_nodes_height = self.draw_object_terminations(obj_terms, obj_pos, width / len(obj_terms))

            terms_height = max(terms_height, result_nodes_height)
            term_nodes.extend(result)

        # Update cursor and draw the objects
        self.cursor += terms_height
        self.terminations.extend(term_nodes)
        object_nodes = self.draw_parent_objects(objects)

        return object_nodes, term_nodes

    def draw_fanin(self, target, terminations, color):
        """
        Draw the fan-in-lines from each of the terminations to the targetpoint
        """
        for term in terminations:
            points = (
                term.bottom_center,
                (term.bottom_center[0], term.bottom_center[1] + FANOUT_LEG_HEIGHT),
                target,
            )
            self.connectors.extend((
                Polyline(points=points, class_='cable-shadow'),
                Polyline(points=points, style=f'stroke: #{color}'),
            ))

    def draw_fanout(self, start, terminations, color):
        """
        Draw the fan-out-lines from the startpoint to each of the terminations
        """
        for term in terminations:
            points = (
                term.top_center,
                (term.top_center[0], term.top_center[1] - FANOUT_LEG_HEIGHT),
                start,
            )
            self.connectors.extend((
                Polyline(points=points, class_='cable-shadow'),
                Polyline(points=points, style=f'stroke: #{color}'),
            ))

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

        parent_object_nodes = []
        # Iterate through each (terms, cable, terms) segment in the path
        for i, segment in enumerate(traced_path):
            near_ends, links, far_ends = segment

            # This is segment number one.
            if i == 0:
                # If this is the first segment, draw the originating termination's parent object
                parent_object_nodes = self.draw_parent_objects(set(end.parent_object for end in near_ends))
            # Else: No need to draw parent objects (parent objects are drawn in last "round" as the far-end!)

            near_terminations = self.draw_terminations(near_ends, parent_object_nodes)
            self.cursor += CABLE_HEIGHT

            # Connector (a Cable or WirelessLink)
            if links:

                obj_list = {end.parent_object for end in far_ends}
                parent_object_nodes, far_terminations = self.draw_far_objects(obj_list, far_ends)
                for cable in links:
                    # Fill in labels and description with all available data
                    description = [
                        f"Link {cable}",
                        cable.get_status_display()
                    ]
                    near = []
                    far = []
                    color = '000000'
                    if cable.description:
                        description.append(f"{cable.description}")
                    if isinstance(cable, Cable):
                        labels = [f"{cable}"] if len(links) > 2 else [f"Cable {cable}", cable.get_status_display()]
                        if cable.type:
                            description.append(cable.get_type_display())
                        if cable.length and cable.length_unit:
                            description.append(f"{cable.length} {cable.get_length_unit_display()}")
                        color = cable.color or '000000'

                        # Collect all connected nodes to this cable
                        near = [term for term in near_terminations if term.object in cable.a_terminations]
                        far = [term for term in far_terminations if term.object in cable.b_terminations]
                        if not (near and far):
                            # a and b terminations may be swapped
                            near = [term for term in near_terminations if term.object in cable.b_terminations]
                            far = [term for term in far_terminations if term.object in cable.a_terminations]
                    elif isinstance(cable, WirelessLink):
                        labels = [f"{cable}"] if len(links) > 2 else [f"Wireless {cable}", cable.get_status_display()]
                        if cable.ssid:
                            description.append(f"{cable.ssid}")
                        if cable.distance and cable.distance_unit:
                            description.append(f"{cable.distance} {cable.get_distance_unit_display()}")
                        near = [term for term in near_terminations if term.object == cable.interface_a]
                        far = [term for term in far_terminations if term.object == cable.interface_b]
                        if not (near and far):
                            # a and b terminations may be swapped
                            near = [term for term in near_terminations if term.object == cable.interface_b]
                            far = [term for term in far_terminations if term.object == cable.interface_a]

                    # Select most-probable start and end position
                    start = near[0].bottom_center
                    end = far[0].top_center
                    text_offset = 0

                    if len(near) > 1 and len(far) > 1:
                        start_center = sum([pos.bottom_center[0] for pos in near]) / len(near)
                        end_center = sum([pos.bottom_center[0] for pos in far]) / len(far)
                        center_x = (start_center + end_center) / 2

                        start = (center_x, start[1] + FANOUT_HEIGHT + FANOUT_LEG_HEIGHT)
                        end = (center_x, end[1] - FANOUT_HEIGHT - FANOUT_LEG_HEIGHT)
                        text_offset -= (FANOUT_HEIGHT + FANOUT_LEG_HEIGHT)
                        self.draw_fanin(start, near, color)
                        self.draw_fanout(end, far, color)
                    elif len(near) > 1:
                        # Handle Fan-In - change start position to be directly below start
                        start = (end[0], start[1] + FANOUT_HEIGHT + FANOUT_LEG_HEIGHT)
                        self.draw_fanin(start, near, color)
                        text_offset -= FANOUT_HEIGHT + FANOUT_LEG_HEIGHT
                    elif len(far) > 1:
                        # Handle Fan-Out - change end position to be directly above end
                        end = (start[0], end[1] - FANOUT_HEIGHT - FANOUT_LEG_HEIGHT)
                        self.draw_fanout(end, far, color)
                        text_offset -= FANOUT_HEIGHT

                    # Create the connector
                    connector = Connector(
                        start=start,
                        end=end,
                        color=color,
                        wireless=isinstance(cable, WirelessLink),
                        url=f'{self.base_url}{cable.get_absolute_url()}',
                        text_offset=text_offset,
                        labels=labels,
                        description=description
                    )
                    self.connectors.append(connector)

            # Render a far-end object not connected via a link (e.g. a ProviderNetwork or Site associated with
            # a CircuitTermination)
            elif far_ends:
                # Attachment
                attachment = self.draw_attachment()
                self.connectors.append(attachment)

                # Object
                parent_object_nodes = self.draw_parent_objects(far_ends)

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

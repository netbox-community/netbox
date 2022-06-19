import decimal
import svgwrite
from svgwrite.container import Group, Hyperlink
from svgwrite.shapes import Line, Rect
from svgwrite.text import Text

from django.conf import settings
from django.urls import reverse
from django.utils.http import urlencode

from netbox.config import get_config
from utilities.utils import foreground_color
from .choices import DeviceFaceChoices
from .constants import RACK_ELEVATION_BORDER_WIDTH


__all__ = (
    'CableTraceSVG',
    'RackElevationSVG',
)


def get_device_name(device):
    if device.virtual_chassis:
        return f'{device.virtual_chassis.name}:{device.vc_position}'
    elif device.name:
        return device.name
    else:
        return str(device.device_type)


class RackElevationSVG:
    """
    Use this class to render a rack elevation as an SVG image.

    :param rack: A NetBox Rack instance
    :param user: User instance. If specified, only devices viewable by this user will be fully displayed.
    :param include_images: If true, the SVG document will embed front/rear device face images, where available
    :param base_url: Base URL for links within the SVG document. If none, links will be relative.
    """
    def __init__(self, rack, unit_height=None, unit_width=None, legend_width=None, user=None, include_images=True,
                 base_url=None):
        self.rack = rack
        self.include_images = include_images
        self.base_url = base_url.rstrip('/') if base_url is not None else ''

        # Set drawing dimensions
        config = get_config()
        self.unit_width = unit_width or config.RACK_ELEVATION_DEFAULT_UNIT_WIDTH
        self.unit_height = unit_height or config.RACK_ELEVATION_DEFAULT_UNIT_HEIGHT
        self.legend_width = legend_width or config.RACK_ELEVATION_LEGEND_WIDTH_DEFAULT

        # Determine the subset of devices within this rack that are viewable by the user, if any
        permitted_devices = self.rack.devices
        if user is not None:
            permitted_devices = permitted_devices.restrict(user, 'view')
        self.permitted_device_ids = permitted_devices.values_list('pk', flat=True)

    @staticmethod
    def _get_device_description(device):
        return '{} ({}) — {} {} ({}U) {} {}'.format(
            device.name,
            device.device_role,
            device.device_type.manufacturer.name,
            device.device_type.model,
            device.device_type.u_height,
            device.asset_tag or '',
            device.serial or ''
        )

    @staticmethod
    def _add_gradient(drawing, id_, color):
        gradient = drawing.linearGradient(
            start=(0, 0),
            end=(0, 25),
            spreadMethod='repeat',
            id_=id_,
            gradientTransform='rotate(45, 0, 0)',
            gradientUnits='userSpaceOnUse'
        )
        gradient.add_stop_color(offset='0%', color='#f7f7f7')
        gradient.add_stop_color(offset='50%', color='#f7f7f7')
        gradient.add_stop_color(offset='50%', color=color)
        gradient.add_stop_color(offset='100%', color=color)
        drawing.defs.add(gradient)

    def _setup_drawing(self):
        width = self.unit_width + self.legend_width + RACK_ELEVATION_BORDER_WIDTH * 2
        height = self.unit_height * self.rack.u_height + RACK_ELEVATION_BORDER_WIDTH * 2
        drawing = svgwrite.Drawing(size=(width, height))

        # Add the stylesheet
        with open('{}/rack_elevation.css'.format(settings.STATIC_ROOT)) as css_file:
            drawing.defs.add(drawing.style(css_file.read()))

        # Add gradients
        RackElevationSVG._add_gradient(drawing, 'occupied', '#d7d7d7')
        RackElevationSVG._add_gradient(drawing, 'blocked', '#ffc0c0')

        return drawing

    def _get_device_coords(self, position, height):
        """
        Return the X, Y coordinates of the top left corner for a device in the specified rack unit.
        """
        x = self.legend_width + RACK_ELEVATION_BORDER_WIDTH
        y = RACK_ELEVATION_BORDER_WIDTH
        if self.rack.desc_units:
            y += int((position - 1) * self.unit_height)
        else:
            y += int((self.rack.u_height - position + 1) * self.unit_height) - int(height * self.unit_height)

        return x, y

    def _draw_device_front(self, drawing, device, start, size):
        text_coords = (
            start[0] + size[0] / 2,
            start[1] + size[1] / 2
        )
        name = get_device_name(device)
        if device.devicebay_count:
            name += ' ({}/{})'.format(device.get_children().count(), device.devicebay_count)
        color = device.device_role.color

        link = drawing.add(
            drawing.a(
                href='{}{}'.format(self.base_url, reverse('dcim:device', kwargs={'pk': device.pk})),
                target='_top',
                fill='black'
            )
        )
        link.set_desc(self._get_device_description(device))
        link.add(drawing.rect(start, size, style='fill: #{}'.format(color), class_='slot'))
        hex_color = '#{}'.format(foreground_color(color))
        link.add(drawing.text(str(name), insert=text_coords, fill=hex_color))

        # Embed front device type image if one exists
        if self.include_images and device.device_type.front_image:
            image = drawing.image(
                href='{}{}'.format(self.base_url, device.device_type.front_image.url),
                insert=start,
                size=size,
                class_='device-image'
            )
            image.fit(scale='slice')
            link.add(image)
            link.add(drawing.text(str(name), insert=text_coords, stroke='black',
                     stroke_width='0.2em', stroke_linejoin='round', class_='device-image-label'))
            link.add(drawing.text(str(name), insert=text_coords, fill='white', class_='device-image-label'))

    def _draw_device_rear(self, drawing, device, start, size):
        text_coords = (
            start[0] + size[0] / 2,
            start[1] + size[1] / 2
        )

        link = drawing.add(
            drawing.a(
                href='{}{}'.format(self.base_url, reverse('dcim:device', kwargs={'pk': device.pk})),
                target='_top',
                fill='black'
            )
        )
        link.set_desc(self._get_device_description(device))
        link.add(drawing.rect(start, size, class_="slot blocked"))
        link.add(drawing.text(get_device_name(device), insert=text_coords))

        # Embed rear device type image if one exists
        if self.include_images and device.device_type.rear_image:
            image = drawing.image(
                href='{}{}'.format(self.base_url, device.device_type.rear_image.url),
                insert=start,
                size=size,
                class_='device-image'
            )
            image.fit(scale='slice')
            link.add(image)
            link.add(Text(get_device_name(device), insert=text_coords, stroke='black',
                     stroke_width='0.2em', stroke_linejoin='round', class_='device-image-label'))
            link.add(Text(get_device_name(device), insert=text_coords, fill='white', class_='device-image-label'))

    def draw_border(self):
        """
        Draw a border around the collection of rack units.
        """
        border_width = RACK_ELEVATION_BORDER_WIDTH
        border_offset = RACK_ELEVATION_BORDER_WIDTH / 2
        frame = Rect(
            insert=(self.legend_width + border_offset, border_offset),
            size=(self.unit_width + border_width, self.rack.u_height * self.unit_height + border_width),
            class_='rack'
        )
        self.drawing.add(frame)

    def draw_legend(self):
        """
        Draw the rack unit labels along the lefthand side of the elevation.
        """
        for ru in range(0, self.rack.u_height):
            start_y = ru * self.unit_height + RACK_ELEVATION_BORDER_WIDTH
            position_coordinates = (self.legend_width / 2, start_y + self.unit_height / 2 + RACK_ELEVATION_BORDER_WIDTH)
            unit = ru + 1 if self.rack.desc_units else self.rack.u_height - ru
            self.drawing.add(
                Text(str(unit), position_coordinates, class_='unit')
            )

    def draw_background(self, face):
        """
        Draw the rack unit placeholders which form the "background" of the rack elevation.
        """
        x_offset = RACK_ELEVATION_BORDER_WIDTH + self.legend_width
        url_string = '{}?{}&position={{}}'.format(
            reverse('dcim:device_add'),
            urlencode({
                'site': self.rack.site.pk,
                'location': self.rack.location.pk if self.rack.location else '',
                'rack': self.rack.pk,
                'face': face,
            })
        )

        for ru in range(0, self.rack.u_height):
            y_offset = RACK_ELEVATION_BORDER_WIDTH + ru * self.unit_height
            text_coords = (
                x_offset + self.unit_width / 2,
                y_offset + self.unit_height / 2
            )

            link = Hyperlink(href=url_string.format(ru), target='_blank')
            link.add(Rect((x_offset, y_offset), (self.unit_width, self.unit_height), class_='slot'))
            link.add(self.drawing.text('add device', insert=text_coords, class_='add-device'))

            self.drawing.add(link)

    def draw_face(self, face, opposite=False):
        """
        Draw any occupied rack units for the specified rack face.
        """
        for unit in self.rack.get_rack_units(face=face, expand_devices=False):

            # Loop through all units in the elevation
            device = unit['device']
            height = unit.get('height', decimal.Decimal(1.0))

            start_cordinates = self._get_device_coords(unit['id'], height)
            end_y = int(self.unit_height * height)
            size = (self.unit_width, end_y)

            # Draw the device
            if device and device.pk in self.permitted_device_ids:
                if device.face == face and not opposite:
                    self._draw_device_front(self.drawing, device, start_cordinates, size)
                else:
                    self._draw_device_rear(self.drawing, device, start_cordinates, size)

            elif device:
                # Devices which the user does not have permission to view are rendered only as unavailable space
                self.drawing.add(Rect(start_cordinates, size, class_='blocked'))

    def render(self, face):
        """
        Return an SVG document representing a rack elevation.
        """

        # Initialize the drawing
        self.drawing = self._setup_drawing()

        # Draw the empty rack & legend
        self.draw_legend()
        self.draw_background(face)

        # Draw the opposite rack face first, then the near face
        if face == DeviceFaceChoices.FACE_REAR:
            opposite_face = DeviceFaceChoices.FACE_FRONT
        else:
            opposite_face = DeviceFaceChoices.FACE_REAR
        # self.draw_face(opposite_face, opposite=True)
        self.draw_face(face)

        # Draw the rack border last
        self.draw_border()

        return self.drawing


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

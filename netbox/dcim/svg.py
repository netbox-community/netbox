import svgwrite
from svgwrite.container import Group, Hyperlink
from svgwrite.shapes import Line, Rect
from svgwrite.text import Text

from django.conf import settings
from django.urls import reverse
from django.utils.http import urlencode

from utilities.utils import foreground_color
from .choices import DeviceFaceChoices
from .constants import RACK_ELEVATION_BORDER_WIDTH


__all__ = (
    'CableTraceSVG',
    'RackElevationSVG',
)


class RackElevationSVG:
    """
    Use this class to render a rack elevation as an SVG image.

    :param rack: A NetBox Rack instance
    :param user: User instance. If specified, only devices viewable by this user will be fully displayed.
    :param include_images: If true, the SVG document will embed front/rear device face images, where available
    :param base_url: Base URL for links within the SVG document. If none, links will be relative.
    """
    def __init__(self, rack, user=None, include_images=True, base_url=None):
        self.rack = rack
        self.include_images = include_images
        if base_url is not None:
            self.base_url = base_url.rstrip('/')
        else:
            self.base_url = ''

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

    @staticmethod
    def _setup_drawing(width, height):
        drawing = svgwrite.Drawing(size=(width, height))

        # add the stylesheet
        with open('{}/rack_elevation.css'.format(settings.STATIC_ROOT)) as css_file:
            drawing.defs.add(drawing.style(css_file.read()))

        # add gradients
        RackElevationSVG._add_gradient(drawing, 'reserved', '#c7c7ff')
        RackElevationSVG._add_gradient(drawing, 'occupied', '#d7d7d7')
        RackElevationSVG._add_gradient(drawing, 'blocked', '#ffc0c0')

        return drawing

    def _draw_device_front(self, drawing, device, start, end, text):
        name = str(device)
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
        link.add(drawing.rect(start, end, style='fill: #{}'.format(color), class_='slot'))
        hex_color = '#{}'.format(foreground_color(color))
        link.add(drawing.text(str(name), insert=text, fill=hex_color))

        # Embed front device type image if one exists
        if self.include_images and device.device_type.front_image:
            image = drawing.image(
                href=device.device_type.front_image.url,
                insert=start,
                size=end,
                class_='device-image'
            )
            image.fit(scale='slice')
            link.add(image)

    def _draw_device_rear(self, drawing, device, start, end, text):
        rect = drawing.rect(start, end, class_="slot blocked")
        rect.set_desc(self._get_device_description(device))
        drawing.add(rect)
        drawing.add(drawing.text(str(device), insert=text))

        # Embed rear device type image if one exists
        if self.include_images and device.device_type.rear_image:
            image = drawing.image(
                href=device.device_type.rear_image.url,
                insert=start,
                size=end,
                class_='device-image'
            )
            image.fit(scale='slice')
            drawing.add(image)

    @staticmethod
    def _draw_empty(drawing, rack, start, end, text, id_, face_id, class_, reservation):
        link = drawing.add(
            drawing.a(
                href='{}?{}'.format(
                    reverse('dcim:device_add'),
                    urlencode({'rack': rack.pk, 'site': rack.site.pk, 'face': face_id, 'position': id_})
                ),
                target='_top'
            )
        )
        if reservation:
            link.set_desc('{} — {} · {}'.format(
                reservation.description, reservation.user, reservation.created
            ))
        link.add(drawing.rect(start, end, class_=class_))
        link.add(drawing.text("add device", insert=text, class_='add-device'))

    def merge_elevations(self, face):
        elevation = self.rack.get_rack_units(face=face, expand_devices=False)
        if face == DeviceFaceChoices.FACE_REAR:
            other_face = DeviceFaceChoices.FACE_FRONT
        else:
            other_face = DeviceFaceChoices.FACE_REAR
        other = self.rack.get_rack_units(face=other_face)

        unit_cursor = 0
        for u in elevation:
            o = other[unit_cursor]
            if not u['device'] and o['device'] and o['device'].device_type.is_full_depth:
                u['device'] = o['device']
                u['height'] = 1
            unit_cursor += u.get('height', 1)

        return elevation

    def render(self, face, unit_width, unit_height, legend_width):
        """
        Return an SVG document representing a rack elevation.
        """
        drawing = self._setup_drawing(
            unit_width + legend_width + RACK_ELEVATION_BORDER_WIDTH * 2,
            unit_height * self.rack.u_height + RACK_ELEVATION_BORDER_WIDTH * 2
        )
        reserved_units = self.rack.get_reserved_units()

        unit_cursor = 0
        for ru in range(0, self.rack.u_height):
            start_y = ru * unit_height
            position_coordinates = (legend_width / 2, start_y + unit_height / 2 + RACK_ELEVATION_BORDER_WIDTH)
            unit = ru + 1 if self.rack.desc_units else self.rack.u_height - ru
            drawing.add(
                drawing.text(str(unit), position_coordinates, class_="unit")
            )

        for unit in self.merge_elevations(face):

            # Loop through all units in the elevation
            device = unit['device']
            height = unit.get('height', 1)

            # Setup drawing coordinates
            x_offset = legend_width + RACK_ELEVATION_BORDER_WIDTH
            y_offset = unit_cursor * unit_height + RACK_ELEVATION_BORDER_WIDTH
            end_y = unit_height * height
            start_cordinates = (x_offset, y_offset)
            end_cordinates = (unit_width, end_y)
            text_cordinates = (x_offset + (unit_width / 2), y_offset + end_y / 2)

            # Draw the device
            if device and device.face == face and device.pk in self.permitted_device_ids:
                self._draw_device_front(drawing, device, start_cordinates, end_cordinates, text_cordinates)
            elif device and device.device_type.is_full_depth and device.pk in self.permitted_device_ids:
                self._draw_device_rear(drawing, device, start_cordinates, end_cordinates, text_cordinates)
            elif device:
                # Devices which the user does not have permission to view are rendered only as unavailable space
                drawing.add(drawing.rect(start_cordinates, end_cordinates, class_='blocked'))
            else:
                # Draw shallow devices, reservations, or empty units
                class_ = 'slot'
                reservation = reserved_units.get(unit["id"])
                if device:
                    class_ += ' occupied'
                if reservation:
                    class_ += ' reserved'
                self._draw_empty(
                    drawing,
                    self.rack,
                    start_cordinates,
                    end_cordinates,
                    text_cordinates,
                    unit["id"],
                    face,
                    class_,
                    reservation
                )

            unit_cursor += height

        # Wrap the drawing with a border
        border_width = RACK_ELEVATION_BORDER_WIDTH
        border_offset = RACK_ELEVATION_BORDER_WIDTH / 2
        frame = drawing.rect(
            insert=(legend_width + border_offset, border_offset),
            size=(unit_width + border_width, self.rack.u_height * unit_height + border_width),
            class_='rack'
        )
        drawing.add(frame)

        return drawing


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
            text_color = f'#{foreground_color(color)}'
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
            termination = self._draw_box(
                width=self.width * .8,
                color=self._get_color(near_end),
                url=near_end.get_absolute_url(),
                labels=self._get_labels(near_end),
                y_indent=PADDING,
                radius=5
            )
            terminations.append(termination)

            # Connector (either a Cable or attachment to a ProviderNetwork)
            if connector is not None:

                # Cable
                cable = self._draw_cable(
                    color=connector.color or '000000',
                    url=connector.get_absolute_url(),
                    labels=[f'Cable {connector}', connector.get_status_display()]
                )
                connectors.append(cable)

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

            else:

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

import decimal
import svgwrite
from svgwrite.container import Hyperlink
from svgwrite.image import Image
from svgwrite.gradients import LinearGradient
from svgwrite.shapes import Rect
from svgwrite.text import Text

from django.conf import settings
from django.core.exceptions import FieldError
from django.db.models import Q
from django.template.defaultfilters import floatformat
from django.urls import reverse
from django.utils.http import urlencode

from netbox.config import get_config
from utilities.data import array_to_ranges
from utilities.html import foreground_color
from dcim.constants import RACK_ELEVATION_BORDER_WIDTH


__all__ = (
    'RackElevationSVG',
)

GRADIENT_RESERVED = '#b0b0ff'
GRADIENT_OCCUPIED = '#d7d7d7'
GRADIENT_BLOCKED = '#ffc0c0'
STROKE_RESERVED = '#4d4dff'


def get_device_name(device):
    if device.virtual_chassis:
        name = f'{device.virtual_chassis.name}:{device.vc_position}'
    elif device.name:
        name = device.name
    else:
        name = str(device.device_type)
    if device.devicebay_count:
        name += ' ({}/{})'.format(device.get_children().count(), device.devicebay_count)

    return name


def get_device_description(device):
    """
    Return a description for a device to be rendered in the rack elevation in the following format

    Name: <name>
    Role: <role>
    Device Type: <manufacturer> <model> (<u_height>)
    Asset tag: <asset_tag> (if defined)
    Serial: <serial> (if defined)
    Description: <description> (if defined)
    """
    description = f'Name: {device.name}'
    description += f'\nRole: {device.role}'
    u_height = f'{floatformat(device.device_type.u_height)}U'
    description += f'\nDevice Type: {device.device_type.manufacturer.name} {device.device_type.model} ({u_height})'
    if device.asset_tag:
        description += f'\nAsset tag: {device.asset_tag}'
    if device.serial:
        description += f'\nSerial: {device.serial}'
    if device.description:
        description += f'\nDescription: {device.description}'

    return description


class RackElevationSVG:
    """
    Use this class to render a rack elevation as an SVG image.

    :param rack: A NetBox Rack instance
    :param unit_width: Rendered unit width, in pixels
    :param unit_height: Rendered unit height, in pixels
    :param legend_width: Legend width, in pixels (where the unit labels appear)
    :param margin_width: Margin width, in pixels (where reservations appear)
    :param user: User instance. If specified, only devices viewable by this user will be fully displayed.
    :param include_images: If true, the SVG document will embed front/rear device face images, where available
    :param base_url: Base URL for links within the SVG document. If none, links will be relative.
    :param highlight_params: Iterable of two-tuples which identifies attributes of devices to highlight
    """
    def __init__(self, rack, unit_height=None, unit_width=None, legend_width=None, margin_width=None, user=None,
                 include_images=True, base_url=None, highlight_params=None):
        self.rack = rack
        self.include_images = include_images
        self.base_url = base_url.rstrip('/') if base_url is not None else ''

        # Set drawing dimensions
        config = get_config()
        self.unit_width = unit_width or config.RACK_ELEVATION_DEFAULT_UNIT_WIDTH
        self.unit_height = unit_height or config.RACK_ELEVATION_DEFAULT_UNIT_HEIGHT
        self.legend_width = legend_width or config.RACK_ELEVATION_DEFAULT_LEGEND_WIDTH
        self.margin_width = margin_width or config.RACK_ELEVATION_DEFAULT_MARGIN_WIDTH

        # Determine the subset of devices within this rack that are viewable by the user, if any
        permitted_devices = self.rack.devices
        if user is not None:
            permitted_devices = permitted_devices.restrict(user, 'view')
        self.permitted_device_ids = permitted_devices.values_list('pk', flat=True)

        # Determine device(s) to highlight within the elevation (if any)
        self.highlight_devices = []
        if highlight_params:
            q = Q()
            for k, v in highlight_params:
                q |= Q(**{k: v})
            try:
                self.highlight_devices = permitted_devices.filter(q)
            except FieldError:
                pass

    @staticmethod
    def _add_gradient(drawing, id_, color):
        gradient = LinearGradient(
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
        width = self.unit_width + self.legend_width + self.margin_width + RACK_ELEVATION_BORDER_WIDTH * 2
        height = self.unit_height * self.rack.u_height + RACK_ELEVATION_BORDER_WIDTH * 2
        drawing = svgwrite.Drawing(size=(width, height))

        # Add the stylesheet
        with open(f'{settings.STATIC_ROOT}/rack_elevation.css') as css_file:
            drawing.defs.add(drawing.style(css_file.read()))

        # Add gradients
        RackElevationSVG._add_gradient(drawing, 'reserved', GRADIENT_RESERVED)
        RackElevationSVG._add_gradient(drawing, 'occupied', GRADIENT_OCCUPIED)
        RackElevationSVG._add_gradient(drawing, 'blocked', GRADIENT_BLOCKED)

        return drawing

    def _get_device_coords(self, position, height):
        """
        Return the X, Y coordinates of the top left corner for a device in the specified rack unit.
        """
        x = self.legend_width + RACK_ELEVATION_BORDER_WIDTH
        y = RACK_ELEVATION_BORDER_WIDTH
        if self.rack.desc_units:
            y += int((position - self.rack.starting_unit) * self.unit_height)
        else:
            y += (
                int((self.rack.u_height - position + self.rack.starting_unit) * self.unit_height) -
                int(height * self.unit_height)
            )

        return x, y

    def _draw_device(self, device, coords, size, color=None, image=None):
        name = get_device_name(device)
        description = get_device_description(device)
        text_color = f'#{foreground_color(color)}' if color else '#000000'
        text_coords = (
            coords[0] + size[0] / 2,
            coords[1] + size[1] / 2
        )

        # Determine whether highlighting is in use, and if so, whether to shade this device
        is_shaded = self.highlight_devices and device not in self.highlight_devices
        css_extra = ' shaded' if is_shaded else ''

        # Create hyperlink element
        link = Hyperlink(href=f'{self.base_url}{device.get_absolute_url()}', target="_parent")
        link.set_desc(description)

        # Add rect element to hyperlink
        if color:
            link.add(Rect(coords, size, style=f'fill: #{color}', class_=f'slot{css_extra}'))
        else:
            link.add(Rect(coords, size, class_=f'slot blocked{css_extra}'))
        link.add(Text(name, insert=text_coords, fill=text_color, class_=f'label{css_extra}'))

        # Embed device type image if provided
        if self.include_images and image:
            url = f'{self.base_url}{image.url}' if image.url.startswith('/') else image.url
            image = Image(
                href=url,
                insert=coords,
                size=size,
                class_=f'device-image{css_extra}'
            )
            image.fit(scale='slice')
            link.add(image)
            link.add(
                Text(name, insert=text_coords, stroke='black', stroke_width='0.2em', stroke_linejoin='round',
                     class_=f'device-image-label{css_extra}')
            )
            link.add(
                Text(name, insert=text_coords, fill='white', class_=f'device-image-label{css_extra}')
            )

        self.drawing.add(link)

    def draw_device_front(self, device, coords, size):
        """
        Draw the front (mounted) face of a device.
        """
        color = device.role.color
        image = device.device_type.front_image
        self._draw_device(device, coords, size, color=color, image=image)

    def draw_device_rear(self, device, coords, size):
        """
        Draw the rear (opposite) face of a device.
        """
        image = device.device_type.rear_image
        self._draw_device(device, coords, size, image=image)

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
            unit = unit + self.rack.starting_unit - 1
            self.drawing.add(
                Text(str(unit), position_coordinates, class_='unit')
            )

    def draw_margin(self):
        """
        Draw any rack reservations in the right-hand margin alongside the rack elevation.
        """
        for reservation in self.rack.reservations.all():
            for segment in array_to_ranges(reservation.units):
                u_height = 1 if len(segment) == 1 else segment[1] + 1 - segment[0]
                coords = self._get_device_coords(segment[0], u_height)
                coords = (coords[0] + self.unit_width + RACK_ELEVATION_BORDER_WIDTH * 2, coords[1])
                size = (
                    self.margin_width - 3,
                    u_height * self.unit_height
                )
                link = Hyperlink(href=f'{self.base_url}{reservation.get_absolute_url()}', target='_parent')
                link.set_desc(f'Reservation #{reservation.pk}: {reservation.description}')
                link.add(
                    Rect(coords, size, class_='reservation', stroke=STROKE_RESERVED, stroke_width=2)
                )
                self.drawing.add(link)

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
            unit = ru + 1 if self.rack.desc_units else self.rack.u_height - ru
            unit = unit + self.rack.starting_unit - 1
            y_offset = RACK_ELEVATION_BORDER_WIDTH + ru * self.unit_height
            text_coords = (
                x_offset + self.unit_width / 2,
                y_offset + self.unit_height / 2
            )

            link = Hyperlink(href=url_string.format(unit), target='_parent')
            link.add(Rect((x_offset, y_offset), (self.unit_width, self.unit_height), class_='slot'))
            link.add(Text('add device', insert=text_coords, class_='add-device'))

            self.drawing.add(link)

    def draw_face(self, face, opposite=False):
        """
        Draw any occupied rack units for the specified rack face.
        """
        for unit in self.rack.get_rack_units(face=face, expand_devices=False):

            # Loop through all units in the elevation
            device = unit['device']
            height = unit.get('height', decimal.Decimal(1.0))

            device_coords = self._get_device_coords(unit['id'], height)
            device_size = (
                self.unit_width,
                int(self.unit_height * height)
            )

            # Draw the device
            if device and device.pk in self.permitted_device_ids:
                if device.face == face and not opposite:
                    self.draw_device_front(device, device_coords, device_size)
                else:
                    self.draw_device_rear(device, device_coords, device_size)

            elif device:
                # Devices which the user does not have permission to view are rendered only as unavailable space
                self.drawing.add(Rect(device_coords, device_size, class_='blocked'))

    def render(self, face):
        """
        Return an SVG document representing a rack elevation.
        """

        # Initialize the drawing
        self.drawing = self._setup_drawing()

        # Draw the empty rack, legend, and margin
        self.draw_legend()
        self.draw_background(face)
        self.draw_margin()

        # Draw the rack face
        self.draw_face(face)

        # Draw the rack border last
        self.draw_border()

        return self.drawing

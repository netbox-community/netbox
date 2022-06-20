import decimal
import svgwrite
from svgwrite.container import Hyperlink
from svgwrite.image import Image
from svgwrite.gradients import LinearGradient
from svgwrite.shapes import Rect
from svgwrite.text import Text

from django.conf import settings
from django.urls import reverse
from django.utils.http import urlencode

from netbox.config import get_config
from utilities.utils import foreground_color
from dcim.choices import DeviceFaceChoices
from dcim.constants import RACK_ELEVATION_BORDER_WIDTH


__all__ = (
    'RackElevationSVG',
)


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
    return '{} ({}) — {} {} ({}U) {} {}'.format(
        device.name,
        device.device_role,
        device.device_type.manufacturer.name,
        device.device_type.model,
        device.device_type.u_height,
        device.asset_tag or '',
        device.serial or ''
    )


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
        width = self.unit_width + self.legend_width + RACK_ELEVATION_BORDER_WIDTH * 2
        height = self.unit_height * self.rack.u_height + RACK_ELEVATION_BORDER_WIDTH * 2
        drawing = svgwrite.Drawing(size=(width, height))

        # Add the stylesheet
        with open(f'{settings.STATIC_ROOT}/rack_elevation.css') as css_file:
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

    def _draw_device(self, device, coords, size, color=None, image=None):
        name = get_device_name(device)
        description = get_device_description(device)
        text_coords = (
            coords[0] + size[0] / 2,
            coords[1] + size[1] / 2
        )
        text_color = f'#{foreground_color(color)}' if color else '#000000'

        # Create hyperlink element
        link = Hyperlink(
            href='{}{}'.format(
                self.base_url,
                reverse('dcim:device', kwargs={'pk': device.pk})
            ),
            target='_blank',
        )
        link.set_desc(description)
        if color:
            link.add(Rect(coords, size, style=f'fill: #{color}', class_='slot'))
        else:
            link.add(Rect(coords, size, class_='slot blocked'))
        link.add(Text(name, insert=text_coords, fill=text_color))

        # Embed device type image if provided
        if self.include_images and image:
            image = Image(
                href='{}{}'.format(self.base_url, image.url),
                insert=coords,
                size=size,
                class_='device-image'
            )
            image.fit(scale='slice')
            link.add(image)
            link.add(Text(name, insert=text_coords, stroke='black',
                     stroke_width='0.2em', stroke_linejoin='round', class_='device-image-label'))
            link.add(Text(name, insert=text_coords, fill='white', class_='device-image-label'))

        self.drawing.add(link)

    def draw_device_front(self, device, coords, size):
        """
        Draw the front (mounted) face of a device.
        """
        color = device.device_role.color
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

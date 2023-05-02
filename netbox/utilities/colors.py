import colorsys


def hex_to_rgb(hex_str):
    """Returns a tuple representing the given hex string as RGB.
    """
    if hex_str.startswith('#'):
        hex_str = hex_str[1:]
    return tuple([int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)])


def rgb_to_hex(rgb):
    """Converts an rgb tuple to hex string for web.
    """
    return ''.join(["%0.2X" % int(c) for c in rgb])


def adjust_color_lightness(r, g, b, factor):
    hue, luminous, saturation = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    luminous = max(min(luminous * factor, 0.9), 0.1)
    r, g, b = colorsys.hls_to_rgb(hue, luminous, saturation)
    return int(r * 255), int(g * 255), int(b * 255)


def lighten_color(color, factor=0.1):
    color = color.strip('#')
    r, g, b = hex_to_rgb(color)
    return rgb_to_hex(adjust_color_lightness(r, g, b, 1 + factor))


def darken_color(color, factor=0.1):
    color = color.strip('#')
    r, g, b = hex_to_rgb(color)
    return rgb_to_hex(adjust_color_lightness(r, g, b, 1 - factor))

__all__ = (
    'build_coords_url',
    'is_coordinate_map_url',
)


def is_coordinate_map_url(url):
    """Return True if the URL contains GPS coordinate placeholders ({lat} or {lon})."""
    return '{lat}' in url or '{lon}' in url


def build_coords_url(map_url, latitude, longitude):
    """
    Build a GPS map URL from a base URL and coordinate values.

    If the URL contains {lat} or {lon} placeholders they are substituted directly;
    otherwise the coordinates are appended as a comma-separated pair.
    """
    lat_str = str(latitude)
    lon_str = str(longitude)
    if is_coordinate_map_url(map_url):
        return map_url.replace('{lat}', lat_str).replace('{lon}', lon_str)
    return f'{map_url}{lat_str},{lon_str}'

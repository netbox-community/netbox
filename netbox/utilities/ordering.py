import re

INTERFACE_NAME_REGEX = r'(^(?P<type>[^\d\.:]+)?)' \
                       r'((?P<slot>\d+)/)?' \
                       r'((?P<subslot>\d+)/)?' \
                       r'((?P<position>\d+)/)?' \
                       r'((?P<subposition>\d+)/)?' \
                       r'((?P<id>\d+))?' \
                       r'(:(?P<channel>\d+))?' \
                       r'(\.(?P<vc>\d+))?' \
                       r'(?P<remainder>.*)$'


def naturalize(value, max_length, integer_places=8):
    """
    Take an alphanumeric string and prepend all integers to `integer_places` places to ensure the strings
    are ordered naturally. For example:

        site9router21
        site10router4
        site10router19

    becomes:

        site00000009router00000021
        site00000010router00000004
        site00000010router00000019

    :param value: The value to be naturalized
    :param max_length: The maximum length of the returned string. Characters beyond this length will be stripped.
    :param integer_places: The number of places to which each integer will be expanded. (Default: 8)
    """
    if not value:
        return value
    output = []
    for segment in re.split(r'(\d+)', value):
        if segment.isdigit():
            output.append(segment.rjust(integer_places, '0'))
        elif segment:
            output.append(segment)
    ret = ''.join(output)

    return ret[:max_length]


def naturalize_interface(value, max_length):
    """
    Similar in nature to naturalize(), but takes into account a particular naming format adapted from the old
    InterfaceManager.

    :param value: The value to be naturalized
    :param max_length: The maximum length of the returned string. Characters beyond this length will be stripped.
    """
    output = ''
    match = re.search(INTERFACE_NAME_REGEX, value)
    if match is None:
        return value

    # First, we order by slot/position, padding each to four digits. If a field is not present,
    # set it to 9999 to ensure it is ordered last.
    for part_name in ('slot', 'subslot', 'position', 'subposition'):
        part = match.group(part_name)
        if part is not None:
            output += part.rjust(4, '0')
        else:
            output += '9999'

    # Append the type, if any.
    if match.group('type') is not None:
        output += match.group('type')

    # Append any remaining fields, left-padding to six digits each.
    for part_name in ('id', 'channel', 'vc'):
        part = match.group(part_name)
        if part is not None:
            output += part.rjust(6, '0')
        else:
            output += '......'

    # Finally, naturalize any remaining text and append it
    if match.group('remainder') is not None and len(output) < max_length:
        remainder = naturalize(match.group('remainder'), max_length - len(output))
        output += remainder

    return output[:max_length]

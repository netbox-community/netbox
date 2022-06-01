import re


def naturalize(value, max_length, integer_places=8, model_instance=None):
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
    :param model_instance: The netbox model instance. This is required to modify the sort order based on the model characteristics
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


def naturalize_interface(value, max_length, integer_places=5, model_instance=None):
    """
    Similar in nature to naturalize(), but takes into account a particular naming format adapted from the old
    InterfaceManager.

    :param value: The value to be naturalized
    :param max_length: The maximum length of the returned string. Characters beyond this length will be stripped.
    :param integer_places: The number of places to which each integer will be expanded. (Default: 5, minimum: 5)
    :param model_instance: The netbox model instance. This is required to modify the sort order based on the model characteristics
    """

    digit_separators = [':', '/', '-']
    subinterface_separators = ['.']
    interface_remainder_len = 10

    interface_type_weight_list = {
        r'^([fgstx]e|et|lt)-': '05',                        # Group juniper interfaces  (https://www.juniper.net/documentation/us/en/software/junos/interfaces-fundamentals/topics/topic-map/router-interfaces-overview.html). Other Juniper interfaces will come after these and sorted alphabetically
        r'^ethernet': '10',                                 # Group Arista Interfaces Ethernet1, Ethernet2, Ethernet49/1, Ethernet50/1
        r'[' + ''.join(digit_separators) + ']+': '15',      # Group Anything with a digit_separator
        r'eth': '20',                                       # Group Anything with eth in the name
    }

    if integer_places < 5:
        integer_places = 5

    output = value
    parts = re.split(r'(\d+)', value)
    if parts:

        # If the last part of the interface name is non-digit, then this will be added to the naturalized name for sorting purposes. Maxlength is 10 (space padded)
        interface_remainder = ''.ljust(interface_remainder_len, ' ')
        if re.match(r'[^\d]+', parts[-1]):
            interface_remainder = naturalize(parts[-1], interface_remainder_len).ljust(interface_remainder_len, ' ')
            parts.pop()

        interface_type_weight = value[:2].upper()                       # the two character of the interface name will determin the sort order
        if getattr(model_instance, 'mgmt_only', False):
            interface_type_weight = "ZZ"                                # mgmt interfaces are put at the end of the table
        else:
            for regmatch, weigth in interface_type_weight_list.items():  # unless it matches a specific pattern, then the interfaces will be grouped
                if re.search(regmatch, value, re.IGNORECASE):             # first match is applied
                    interface_type_weight = weigth
                    break

        output = interface_type_weight.rjust(2, '9')

        for part in parts:
            if part.isdigit():
                output += part.rjust(integer_places, '0')   # zero-pre-pad the port number. 'integer_places' digits must be at least 5, because subinterfaces can go to 65535.
            elif part in subinterface_separators:           # replace the subinterface separators with a 0
                output += '0'                               # this will group subinterfaces with the master interface, when there are interfaces with more /'s  (ex: Eth1.1 and Eth1/1.5)
            elif part in digit_separators:                  # standardize the digit separators to a 9.
                output += '9'

        output = output.ljust(max_length - interface_remainder_len, '.') + interface_remainder

    return output[:max_length]

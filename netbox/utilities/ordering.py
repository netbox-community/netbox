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

    # See #2872, #3799, #6882, #9368

    digit_separators = [':', '/', '-']
    subinterface_separators = ['.']
    interface_remainder_len = 10
    interface_type_sort_length = 4

    interface_type_weight_list = {                        # First matched expression is used. The order and the assigned weith can be out of order to accomodate correct sortimg
        r'^([fgstx]e|et|lt|st)-': 5,                      # Group Juniper interfaces  (https://www.juniper.net/documentation/us/en/software/junos/interfaces-fundamentals/topics/topic-map/router-interfaces-overview.html). Other Juniper interfaces will come after these and sorted alphabetically
        r'^(embed|eth|fa|gi|ten|hun)[^\d]*\d*': 10,       # Group Cisco/Arista Interfaces (order is a combination of weight+nbr_of_separators, so next weight must be 20)
        r'^[^a-z]*$': 30,                                 # Group Only digits
        r'^[e]?\d+[a-z]*$': 25,                           # Group Netapp Interfaces https://library.netapp.com/ecmdocs/ECMP1155586/html/GUID-60DA02FA-B824-4B4E-862F-6862D1407453.html
        r'[' + '\\'.join(digit_separators) + ']+': 30,    # Group Anything with a digit_separator
    }

    if integer_places < 5:
        integer_places = 5

    output = value
    parts = re.split(r'(\d+)', value)
    if parts:

        # If the last part of the interface name is non-digit, then this will be added to the naturalized name for sorting purposes. Maxlength is 10 (space padded)
        interface_remainder = ''.ljust(interface_remainder_len, '.')
        if len(parts) > 1:
            if re.match(r'[^\d]+', parts[-1]):
                interface_remainder = naturalize(parts[-1], interface_remainder_len).ljust(interface_remainder_len, '.')
                parts.pop()

        interface_type_weight = ''
        if re.match(r'[^\d]+', parts[0]):                                # if the first part is not only numbers, then use that for sorting
            interface_type_weight = parts[0][:interface_type_sort_length].upper()
            parts.pop(0)

        if getattr(model_instance, 'mgmt_only', False):                  # if mgmt_only, then place it as last item
            interface_type_weight = ''.ljust(interface_type_sort_length, 'Z')
        else:
            nbr_of_separators = len(re.findall(r'[' + '\\'.join(digit_separators) + r']\d+?', value, re.IGNORECASE))
            for regmatch, weigth in interface_type_weight_list.items():  # unless it matches a specific pattern, then the interfaces will be grouped
                if re.search(regmatch, value, re.IGNORECASE):            # first match is applied
                    if weigth == 10:
                        weigth += nbr_of_separators                      # for Cisco type, take the nbr of separators into account
                    interface_type_weight = str(weigth).zfill(interface_type_sort_length)
                    break

        output = interface_type_weight.ljust(interface_type_sort_length, '0')

        for part in parts:
            if part.isdigit():
                output += str(int(part) + 1).rjust(integer_places, '0')   # zero-pre-pad the port number. 'integer_places' digits must be at least 5, because subinterfaces can go to 65535. Interface numbers are incremented with one to better sort the '0' interfaces (0:0.0; 0; 0.0)
            elif part in subinterface_separators:           # standardize the subinterface separators to a 0
                output += '0'                               # this will group subinterfaces with the master interface, when there are interfaces with more /'s  (ex: Eth1.1 and Eth1/1.5)
            elif part in digit_separators:                  # standardize the digit separators to a 9.
                output += '9'

        output = output.ljust(max_length - interface_remainder_len, '.') + interface_remainder

    return output[:max_length]

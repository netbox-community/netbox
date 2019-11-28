# IP address families
AF_CHOICES = (
    (4, 'IPv4'),
    (6, 'IPv6'),
)


# IP protocols (for services)
IP_PROTOCOL_TCP = 6
IP_PROTOCOL_UDP = 17
IP_PROTOCOL_CHOICES = (
    (IP_PROTOCOL_TCP, 'TCP'),
    (IP_PROTOCOL_UDP, 'UDP'),
)

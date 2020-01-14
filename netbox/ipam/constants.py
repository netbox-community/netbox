from .choices import IPAddressRoleChoices

IPADDRESS_ROLES_NONUNIQUE = (
    # IPAddress roles which are exempt from unique address enforcement
    IPAddressRoleChoices.ROLE_ANYCAST,
    IPAddressRoleChoices.ROLE_VIP,
    IPAddressRoleChoices.ROLE_VRRP,
    IPAddressRoleChoices.ROLE_HSRP,
    IPAddressRoleChoices.ROLE_GLBP,
    IPAddressRoleChoices.ROLE_CARP,
)

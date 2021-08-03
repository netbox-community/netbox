import graphene

__all__ = (
    'IPAddressesMixin',
    'VLANGroupsMixin',
)


class IPAddressesMixin:
    ip_addresses = graphene.List('ipam.graphql.types.IPAddressType')

    def resolve_ip_addresses(self, info):
        return self.ip_addresses.restrict(info.context.user, 'view')


class VLANGroupsMixin:
    vlan_groups = graphene.List('ipam.graphql.types.VLANGroupType')

    def resolve_vlan_groups(self, info):
        return self.vlan_groups.restrict(info.context.user, 'view')

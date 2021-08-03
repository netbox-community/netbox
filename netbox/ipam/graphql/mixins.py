import graphene

__all__ = (
    'IPAddressesMixin',
)


class IPAddressesMixin:
    ip_addresses = graphene.List('ipam.graphql.types.IPAddressType')

    def resolve_ip_addresses(self, info):
        return self.ip_addresses.restrict(info.context.user, 'view')

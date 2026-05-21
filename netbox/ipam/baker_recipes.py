from model_bakery.recipe import Recipe, foreign_key, seq

#
# RIR
#

rir = Recipe(
    'ipam.RIR',
    name=seq('RIR '),
    slug=seq('rir-'),
)

#
# ASN
#

asn = Recipe(
    'ipam.ASN',
    asn=seq(64512),
    rir=foreign_key(rir),
)

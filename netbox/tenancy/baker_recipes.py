from model_bakery.recipe import Recipe, seq

#
# Tenant
#

tenant = Recipe(
    'tenancy.Tenant',
    name=seq('Tenant '),
    slug=seq('tenant-'),
)

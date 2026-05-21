from model_bakery.recipe import Recipe, seq

#
# Site
#

site = Recipe(
    'dcim.Site',
    name=seq('Site '),
    slug=seq('site-'),
)

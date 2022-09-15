# Regions

[Sites](./site.md) can be arranged geographically using regions. A region might represent a continent, country, city, campus, or other area depending on your use case. Regions can be nested recursively to construct a hierarchy. For example, you might define several country regions, and within each of those several state or city regions to which sites are assigned.

## Fields

### Parent

The parent region, if any.

### Name

The region's name. Must be unique to the parent region, if one is assigned.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)

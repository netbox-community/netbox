import graphene
from .circuits_schema import CircuitsQuery
from .tenancy_schema import TenancyQuery
from .dcim_schema import DcimQuery
from .ipam_schema import IpamQuery

# Root
class RootQuery(
      CircuitsQuery
    , TenancyQuery
    , DcimQuery
    , IpamQuery
    , graphene.ObjectType):
    pass

schema = graphene.Schema(query=RootQuery)

""""
query {
  allCircuits {
    edges {
      node {
        id
        cid
        installDate
        provider {
          id
          name
          slug
        }
      }
    }
  }
}


{
  allCircuits(cid_Icontains: "1") {
    edges {
      node {
        id
        cid
        provider {
          name
        }
      }
    }
  }
}

{
  provider {
    edges {
      node {
        id
        slug
        name
        circuits {
          edges {
            node {
              id
            }
          }
        }
      }
    }
  }
}

{
  allCircuits(cid_Icontains: "1", id: "Q2lyY3VpdE5vZGU6MQ==") {
    edges {
      node {
        id
        cid
        installDate
        commitRate
        description
        commitRate
        comments
        provider {
          name
        }
      }
    }
  }
}

{
  allCircuits(commitRate_Lte: 127, commitRate_Gte: 120) {
    edges {
      node {
        id
        cid
        installDate
        lastUpdated
        commitRate
        provider {
          id
        }
      }
    }
  }
}


{
  allCircuits {
    edges {
      node {
        id
        cid
        comments
        commitRate
        description
        type {
          id
          name
          slug
        }
        tenant {
          id
          slug
          name
          group {
            id
            slug
            name
          }
        }
      }
    }
  }
}

{
  tenantGroups {
    edges {
      node {
        id
        slug
        name
        tenants {
          edges {
            node {
              id
              name
              slug
              circuits {
                edges {
                  node {
                    id
                    cid
                    comments
                    commitRate
                    description
                  }
                }
              }
            }
          }
        }
      }
    }
  }

}


{
  allCircuits {
    edges {
      node {
        id
        cid
        comments
        commitRate
        description
        created
        lastUpdated
        installDate
        provider {
          id
          name
          slug
        }
        type {
          id
          name
          slug
        }
        tenant {
          id
          slug
          name
          group {
            id
            slug
            name
          }
        }
      }
    }
  }
}
"""
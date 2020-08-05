# Aggregates

IP addressing is by nature hierarchical. The first few levels of the IPv4 hierarchy, for example, look like this:

* 0.0.0.0/0
    * 0.0.0.0/1
        * 0.0.0.0/2
        * 64.0.0.0/2
    * 128.0.0.0/1
        * 128.0.0.0/2
        * 192.0.0.0/2

This hierarchy comprises 33 tiers of addressing, from /0 all the way down to individual /32 address (and much, much further to /128 for IPv6). Of course, most organizations are concerned with only relatively small portions of the total IP space, so tracking the uppermost of these tiers isn't necessary.

NetBox allows us to specify the portions of IP space that are interesting to us by defining _aggregates_. Typically, an aggregate will correspond to either an allocation of public (globally routable) IP space granted by a regional authority, or a private (internally-routable) designation. Common private designations include:

* 10.0.0.0/8 (RFC 1918)
* 100.64.0.0/10 (RFC 6598)
* 172.16.0.0/12 (RFC 1918)
* 192.168.0.0/16 (RFC 1918)
* One or more /48s within fd00::/8 (IPv6 unique local addressing)

Each aggregate is assigned to a RIR. For "public" aggregates, this will be the real-world authority which has granted your organization permission to use the specified IP space on the public Internet. For "private" aggregates, this will be a statutory authority, such as RFC 1918. Each aggregate can also annotate that date on which it was allocated, where applicable.

Prefixes are automatically arranged beneath their parent aggregates in NetBox. Typically you'll want to create aggregates only for the prefixes and IP addresses that your organization actually manages: There is no need to define aggregates for provider-assigned space which is only used on Internet circuits, for example.

!!! note
    Because aggregates represent swaths of the global IP space, they cannot overlap with one another: They can only exist side-by-side. For instance, you cannot define both 10.0.0.0/8 and 10.16.0.0/16 as aggregates, because they overlap. 10.16.0.0/16 in this example would be created as a container prefix and automatically grouped under the 10.0.0.0/8 aggregate. Remember, the purpose of aggregates is to establish the root of your IP addressing hierarchy.

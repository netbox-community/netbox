# Aggregates

The first step to documenting your IP space is to define its scope by creating aggregates. Aggregates establish the root of your IP address hierarchy by defining the top-level allocations that you're interested in managing. Most organizations will want to track some commonly-used private IP spaces, such as:

* 10.0.0.0/8 (RFC 1918)
* 100.64.0.0/10 (RFC 6598)
* 172.16.0.0/12 (RFC 1918)
* 192.168.0.0/16 (RFC 1918)
* One or more /48s within fd00::/8 (IPv6 unique local addressing)

In addition to one or more of these, you'll want to create an aggregate for each globally-routable space your organization has been allocated. These aggregates should match the allocations recorded in public WHOIS databases.

Each IP prefix will be automatically arranged under its parent aggregate if one exists. Note that it's advised to create aggregates only for IP ranges actually allocated to your organization (or marked for private use): There is no need to define aggregates for provider-assigned space which is only used on Internet circuits, for example.

Aggregates cannot overlap with one another: They can only exist side-by-side. For instance, you cannot define both 10.0.0.0/8 and 10.16.0.0/16 as aggregates, because they overlap. 10.16.0.0/16 in this example would be created as a prefix and automatically grouped under 10.0.0.0/8. Remember, the purpose of aggregates is to establish the root of your IP addressing hierarchy.

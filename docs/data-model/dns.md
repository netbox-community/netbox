The DNS component of NetBox deals with the management of DNS zones.

# Zones

A zone corresponds to a zone file in a DNS server, it stores the SOA (Start Of Authority) record and other records that are stored as Record objects.

Zone objects handle only forward DNS, reverse DNS is handled by Prefixes (in IPAM section), which also store a SOA record.

Netbox provides two views in the DNS menu to get the exports in BIND format, which is compatible with every DNS server, directly or by import. Those
exports are also accessible as JSON through the REST API. One of these views is the export of all the forward zones in the database,
the second is the export of all the reverse zones.

The reverse zones are correctly merged and/or divided to meet the requirements of a DNS server (for instance, IPv4 reverse zones must be /16 or /24), and
not to duplicate records (for instance if you have in database the prefixes 192.168.0.0/16 and 192.168.1.0/24, only the biggest will be exported) ; however,
only IP addresses which are in an active prefix will be taken into account. Obviously, reverse DNS is supported for both IPv4 and IPv6.

The SOA Serial field is not editable : it's automatically created and managed by Netbox. Each time a zone (forward or reverse) is exported,
if there are changes since the last export or if it's the first export, the serial will be incremented. It's in the following format :
YYYYMMDDNN with Y the year, M the month, D the day and N a two-digit counter.

As zones and their BIND exports are readable through the REST API, it is possible to write some external script to automatically update
your DNS server configuration from Netbox's database.

---

# Record

Each Record object represents a DNS record, i.e. a link between a hostname and a resource, which can be either an IP address or a text value,
for instance another name if the record is of CNAME type.

Records must be linked to an existing zone, and hold either an IP address link or a text value. The "Address" field points to an IP address
in database, but if you want to put an IP in your record but not in your database (if you don't own the IP for instance), it's possible
by putting the IP as text value instead.

You can create, edit or import records with IPs not existing yet in the database. They will be automatically created (but not the prefixes !).
However, the zones must be created first, they won't be so automatically.

Reverse DNS is not supported by Record objects, but by the "PTR" field in IP addresses. If this field is modified and not empty, a corresponding
A/AAAA record is automatically created if the corresponding zone is found in the database. Be careful, if there was A/AAAA records
for the old PTR value, they are not deleted.


# NDX Enrichment

Enrichment holds supplementary data provided by the [NetBox Data Exchange](../../features/ndx.md) catalog for an imported object, beyond what is represented by NetBox's own models. Each [import record](./importrecord.md) may have one enrichment record. Enrichment data is available only for entitled API tokens, and is updated each time the entry is re-imported using such a token. (Re-importing an entry using a token which is not entitled to enrichment data leaves any existing enrichment data unchanged.)

Lifecycle dates are stored as provided by the catalog, which may include partial dates (e.g. `2026-03`).

## Fields

### Thermal

* **TDP** - Thermal design power, in watts
* **Airflow** - Airflow, in cubic feet per minute
* **Cooling Type** - Method of cooling (e.g. fans)

### Lifecycle

* **General Availability** - The date on which the product became available
* **End of Life Announced** - The date on which the product's end of life was announced
* **End of Sale** - The last date on which the product could be ordered
* **End of Software Maintenance** - The last date on which software maintenance is provided
* **End of Security Updates** - The last date on which security updates are provided
* **Last Date of Support** - The last date on which the product is supported by its manufacturer

### Environmental

* **Operating Temperature** - Minimum and maximum operating temperatures, in degrees Celsius
* **Operating Humidity** - Minimum and maximum operating humidity, as a percentage
* **Maximum Operating Altitude** - In meters
* **Ingress Protection** - IP rating (e.g. IP20)
* **MTBF** - Mean time between failures, in hours

### Operational

* **Typical Power Draw** - In watts
* **Maximum Power Draw** - In watts
* **Noise Level** - In A-weighted decibels
* **Power Capacity** - The rated capacity of a power distribution unit, in watts

!!! note
    The catalog records a power distribution unit's rated capacity as the maximum draw of its power ports, which would prevent NetBox from calculating the unit's utilization from its outlets. The capacity is instead stored here, and the maximum and allocated draw of the power port templates are left empty.

### Platform

* **Network OS** - The operating system run by the device
* **Network OS Family** - The family to which the operating system belongs
* **API Types** - The management APIs supported by the device (e.g. NETCONF)

### SNMP

* **sysObjectID** - The device's SNMP sysObjectID
* **Vendor OID Prefix** - The vendor's SNMP enterprise OID

### Availability Flags

Indicate which categories of enrichment data (lifecycle, thermal, environmental, operational, platform, and SNMP) the catalog holds for the entry.

### Extensions

Protocol-specific data (such as Modbus, BACnet, Redfish, IPMI, gNMI, and NETCONF profiles) provided by the catalog.

## Provenance

Each enrichment record may have a set of provenance entries, each of which describes the source of an individual field:

* **Field** - The path of the enrichment field (e.g. `lifecycle.ga_date`)
* **Source** - The source of the data (typically a URL)
* **Type** - The type of source (e.g. vendor datasheet)
* **Confidence** - The confidence in the accuracy of the data
* **Retrieved** - The date on which the data was retrieved
* **Note** - Any additional information

# Search

## Field Weight Guidance

| Weight | Field Role                                       | Examples                                           |
|--------|--------------------------------------------------|----------------------------------------------------|
| 50     | Unique serialized attribute                      | Device.asset_tag                                   |
| 60     | Unique serialized attribute (per related object) | Device.serial                                      |
| 100    | Primary human identifier                         | Device.name, Circuit.cid, Cable.label              |
| 110    | Slug                                             | Site.slug                                          |
| 200    | Secondary identifier                             | Provider.account, DeviceType.part_number           |
| 300    | Highly unique descriptive attribute              | CircuitTermination.xconnect_id, IPAddress.dns_name |
| 500    | Description                                      | Site.description                                   |
| 1000   | Custom field default                             | -                                                  |
| 2000   | Other discrete attribute                         | CircuitTermination.port_speed                      |
| 5000   | Comment field                                    | Site.comments                                      |

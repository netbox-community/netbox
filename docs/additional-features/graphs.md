# Graphs

NetBox does not have the ability to generate graphs natively, but this feature allows you to embed contextual graphs from an external resources (such as a monitoring system) inside the site, provider, and interface views. Each embedded graph must be defined with the following parameters:

* **Type:** Site, provider, or interface. This determines in which view the graph will be displayed.
* **Weight:** Determines the order in which graphs are displayed (lower weights are displayed first). Graphs with equal weights will be ordered alphabetically by name.
* **Name:** The title to display above the graph.
* **Source URL:** The source of the image to be embedded. The associated object will be available as a template variable named `obj`.
* **Link URL (optional):** A URL to which the graph will be linked. The associated object will be available as a template variable named `obj`.

## Examples

You only need to define one graph object for each graph you want to include when viewing an object. For example, if you want to include a graph of traffic through an interface over the past five minutes, your graph source might looks like this:

```
https://my.nms.local/graphs/?node={{ obj.device.name }}&interface={{ obj.name }}&duration=5m
```

You can define several graphs to provide multiple contexts when viewing an object. For example:

```
https://my.nms.local/graphs/?type=throughput&node={{ obj.device.name }}&interface={{ obj.name }}&duration=60m
https://my.nms.local/graphs/?type=throughput&node={{ obj.device.name }}&interface={{ obj.name }}&duration=24h
https://my.nms.local/graphs/?type=errors&node={{ obj.device.name }}&interface={{ obj.name }}&duration=60m
```

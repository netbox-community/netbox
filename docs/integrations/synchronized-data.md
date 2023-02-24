# Synchronized Data

Some NetBox models support automatic synchronization of certain attributes from remote [data sources](../models/core/datasource.md), such as a git repository hosted on GitHub or GitLab. Data from the authoritative remote source is synchronized locally in NetBox as [data files](../models/core/datafile.md).

The following features support the use of synchronized data:

* [Configuration templates](../features/configuration-rendering.md)
* [Configuration context data](../features/context-data.md)
* [Export templates](../customization/export-templates.md)

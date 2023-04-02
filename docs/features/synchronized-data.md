# Synchronized Data

!!! info "This feature was introduced in NetBox v3.5."

Several models in NetBox support the automatic synchronization of local data from a designated remote source. For example, [configuration templates](./configuration-rendering.md) defined in NetBox can source their content from text files stored in a remote git repository. This accomplished using the core [data source](../models/core/datasource.md) and [data file](../models/core/datafile.md) models.

To enable remote data synchronization, the NetBox administrator first designates one or more remote data sources. NetBox currently supports the following source types:

* Git repository
* Amazon S3 bucket (or compatible product)
* Local disk path

(Local disk paths are considered "remote" in this context as they exist outside NetBox's database. These paths could also be mapped to external network shares.)

Each type of remote source has its own configuration parameters. For instance, a git source will ask the user to specify a branch and authentication credentials. Once the source has been created, a synchronization job is run to automatically replicate remote files in the local database.

The following NetBox models can be associated with replicated data files:

* Config contexts
* Config templates
* Export templates

Once a data has been designated for a local instance, its data will be replaced with the content of the replicated file. When the replicated file is updated in the future (via synchronization jobs), the local instance will be flagged as having out-of-date data. A user can then synchronize these objects individually or in bulk to effect the update. This two-stage process ensures that automated synchronization tasks do not immediately affect production data.

# Data Sources

A data source represents some external repository of data which NetBox can consume, such as a git repository. Files within the data source are synchronized to NetBox by saving them in the database as [data file](./datafile.md) objects.

## Fields

### Name

The data source's human-friendly name.

### Type

The type of data source. Supported options include:

* Local directory
* git repository
* Amazon S3 bucket

### URL

The URL identifying the remote source. Some examples are included below.

| Type      | Example URL                                        |
|-----------|----------------------------------------------------|
| Local     | file:///path/to/my/data/                           |
| git       | https://github.com/my-organization/my-repo         |
| Amazon S3 | https://s3.us-east-2.amazonaws.com/my-bucket-name/ |

### Status

The source's current synchronization status. Note that this cannot be set manually: It is updated automatically when the source is synchronized.

### Enabled

If false, synchronization will be disabled.

### Ignore Rules

A set of rules (one per line) identifying filenames to ignore during synchronization. Some examples are provided below. See Python's [`fnmatch()` documentation](https://docs.python.org/3/library/fnmatch.html) for a complete reference.

| Rule           | Description                              |
|----------------|------------------------------------------|
| `README`       | Ignore any files named `README`          |
| `*.txt`        | Ignore any files with a `.txt` extension |
| `data???.json` | Ignore e.g. `data123.json`               |

### Last Synced

The date and time at which the source was most recently synchronized successfully.

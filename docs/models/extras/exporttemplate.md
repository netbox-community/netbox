# Export Templates

Export templates are used to render arbitrary data from a set of NetBox objects. For example, you might want to automatically generate a network monitoring service configuration from a list of device objects. See the [export templates documentation](../../customization/export-templates.md) for more information.

## Fields

### Name

The name of the export template. This will appear in the "export" dropdown list in the NetBox UI.

### Content Type

The type of NetBox object to which the export template applies.

### Data File

Template code may optionally be sourced from a remote [data file](../core/datafile.md), which is synchronized from a remote data source. When designating a data file, there is no need to specify local content for the template: It will be populated automatically from the data file.

### Template Code

Jinja2 template code for rendering the exported data.

### MIME Type

The MIME type to indicate in the response when rendering the export template (optional). Defaults to `text/plain`.

### File Extension

The file extension to append to the file name in the response (optional).

### As Attachment

If selected, the rendered content will be returned as a file attachment, rather than displayed directly in-browser (where supported).

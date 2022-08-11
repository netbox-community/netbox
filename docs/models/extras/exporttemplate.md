# Export Templates

## Fields

### Name

The name of the export template. This will appear in the "export" dropdown list in the NetBox UI.

### Content Type

The type of NetBox object to which the export template applies.

### Template Code

Jinja2 template code for rendering the exported data.

### MIME Type

The MIME type to indicate in the response when rendering the export template (optional). Defaults to `text/plain`.

### File Extension

The file extension to append to the file name in the response (optional).

### As Attachment

If selected, the rendered content will be returned as a file attachment, rather than displayed directly in-browser (where supported).

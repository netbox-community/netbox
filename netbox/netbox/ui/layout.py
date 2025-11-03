from netbox.ui.panels import Panel

__all__ = (
    'Column',
    'Layout',
    'Row',
)


class Layout:

    def __init__(self, *rows):
        for i, row in enumerate(rows):
            if type(row) is not Row:
                raise TypeError(f"Row {i} must be a Row instance, not {type(row)}.")
        self.rows = rows


class Row:

    def __init__(self, *columns):
        for i, column in enumerate(columns):
            if type(column) is not Column:
                raise TypeError(f"Column {i} must be a Column instance, not {type(column)}.")
        self.columns = columns


class Column:

    def __init__(self, *panels):
        for i, panel in enumerate(panels):
            if not isinstance(panel, Panel):
                raise TypeError(f"Panel {i} must be an instance of a Panel, not {type(panel)}.")
        self.panels = panels

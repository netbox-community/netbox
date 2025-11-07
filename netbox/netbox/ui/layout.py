from netbox.ui.panels import Panel, PluginContentPanel

__all__ = (
    'Column',
    'Layout',
    'Row',
    'SimpleLayout',
)


#
# Base classes
#

class Layout:
    """
    A collection of rows and columns comprising the layout of content within the user interface.

    Parameters:
        *rows: One or more Row instances
    """
    def __init__(self, *rows):
        for i, row in enumerate(rows):
            if type(row) is not Row:
                raise TypeError(f"Row {i} must be a Row instance, not {type(row)}.")
        self.rows = rows


class Row:
    """
    A collection of columns arranged horizontally.

    Parameters:
        *columns: One or more Column instances
    """
    def __init__(self, *columns):
        for i, column in enumerate(columns):
            if type(column) is not Column:
                raise TypeError(f"Column {i} must be a Column instance, not {type(column)}.")
        self.columns = columns


class Column:
    """
    A collection of panels arranged vertically.

    Parameters:
        *panels: One or more Panel instances
    """
    def __init__(self, *panels):
        for i, panel in enumerate(panels):
            if not isinstance(panel, Panel):
                raise TypeError(f"Panel {i} must be an instance of a Panel, not {type(panel)}.")
        self.panels = panels


#
# Common layouts
#

class SimpleLayout(Layout):
    """
    A layout with one row of two columns and a second row with one column.

    Plugin content registered for `left_page`, `right_page`, or `full_width_path` is included automatically. Most object
    views in NetBox utilize this layout.

    ```
    +-------+-------+
    | Col 1 | Col 2 |
    +-------+-------+
    |     Col 3     |
    +---------------+
    ```

    Parameters:
        left_panels: Panel instances to be rendered in the top lefthand column
        right_panels: Panel instances to be rendered in the top righthand column
        bottom_panels: Panel instances to be rendered in the bottom row
    """
    def __init__(self, left_panels=None, right_panels=None, bottom_panels=None):
        left_panels = left_panels or []
        right_panels = right_panels or []
        bottom_panels = bottom_panels or []
        rows = [
            Row(
                Column(*left_panels, PluginContentPanel('left_page')),
                Column(*right_panels, PluginContentPanel('right_page')),
            ),
            Row(
                Column(*bottom_panels, PluginContentPanel('full_width_page'))
            )
        ]
        super().__init__(*rows)

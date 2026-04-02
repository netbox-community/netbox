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
            if not isinstance(row, Row):
                raise TypeError(f"Row {i} must be a Row instance, not {type(row)}.")
        self.rows = rows

    def __iter__(self):
        return iter(self.rows)

    def __repr__(self):
        return f"Layout({len(self.rows)} rows)"


class Row:
    """
    A collection of columns arranged horizontally.

    Parameters:
        *columns: One or more Column instances
    """
    def __init__(self, *columns):
        for i, column in enumerate(columns):
            if not isinstance(column, Column):
                raise TypeError(f"Column {i} must be a Column instance, not {type(column)}.")
        self.columns = columns

    def __iter__(self):
        return iter(self.columns)

    def __repr__(self):
        return f"Row({len(self.columns)} columns)"


class Column:
    """
    A collection of panels arranged vertically.

    Parameters:
        *panels: One or more Panel instances
        width: Bootstrap grid column width (1-12). If unset, the column will expand to fill available space.
    """
    def __init__(self, *panels, width=None):
        for i, panel in enumerate(panels):
            if not isinstance(panel, Panel):
                raise TypeError(f"Panel {i} must be an instance of a Panel, not {type(panel)}.")
        if width is not None:
            if type(width) is not int:
                raise ValueError(f"Column width must be an integer, not {type(width)}")
            if width not in range(1, 13):
                raise ValueError(f"Column width must be an integer between 1 and 12 (got {width}).")
        self.panels = panels
        self.width = width

    def __iter__(self):
        return iter(self.panels)

    def __repr__(self):
        return f"Column({len(self.panels)} panels)"


#
# Common layouts
#

class SimpleLayout(Layout):
    """
    A layout with one row of two columns and a second row with one column.

    Plugin content registered for `left_page`, `right_page`, or `full_width_page` is included automatically. Most object
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

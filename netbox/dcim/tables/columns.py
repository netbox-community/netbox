import django_tables2 as tables

__all__ = (
    'SpeedColumn',
)


class SpeedColumn(tables.TemplateColumn):
    """
    Humanize the speed in the column view
    """
    template_code = """
        {% load helpers %}
        {{ value|humanize_speed|placeholder }}
        """

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)

    def value(self, value, **kwargs):
        return super().value(value=value, **kwargs) if value else None

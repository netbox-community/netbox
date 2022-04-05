import django_tables2 as tables

__all__ = (
    'CommitRateColumn',
)


class CommitRateColumn(tables.TemplateColumn):
    """
    Humanize the commit rate in the column view
    """
    template_code = """
        {% load helpers %}
        {{ record.commit_rate|humanize_speed }}
        """

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)

    def value(self, value):
        return str(value) if value else None

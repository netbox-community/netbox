from netbox.views import generic
from utilities.utils import count_related
from utilities.views import register_model_view
from . import filtersets, forms, tables
from .models import *


#
# Data sources
#

class DataSourceListView(generic.ObjectListView):
    queryset = DataSource.objects.annotate(
        file_count=count_related(DataFile, 'source')
    )
    filterset = filtersets.DataSourceFilterSet
    filterset_form = forms.DataSourceFilterForm
    table = tables.DataSourceTable


@register_model_view(DataSource)
class DataSourceView(generic.ObjectView):
    queryset = DataSource.objects.all()


@register_model_view(DataSource, 'edit')
class DataSourceEditView(generic.ObjectEditView):
    queryset = DataSource.objects.all()
    form = forms.DataSourceForm


@register_model_view(DataSource, 'delete')
class DataSourceDeleteView(generic.ObjectDeleteView):
    queryset = DataSource.objects.all()


class DataSourceBulkImportView(generic.BulkImportView):
    queryset = DataSource.objects.all()
    model_form = forms.DataSourceImportForm
    table = tables.DataSourceTable


class DataSourceBulkEditView(generic.BulkEditView):
    queryset = DataSource.objects.annotate(
        count_files=count_related(DataFile, 'source')
    )
    filterset = filtersets.DataSourceFilterSet
    table = tables.DataSourceTable
    form = forms.DataSourceBulkEditForm


class DataSourceBulkDeleteView(generic.BulkDeleteView):
    queryset = DataSource.objects.annotate(
        count_files=count_related(DataFile, 'source')
    )
    filterset = filtersets.DataSourceFilterSet
    table = tables.DataSourceTable


#
# Data files
#

class DataFileListView(generic.ObjectListView):
    queryset = DataFile.objects.defer('data')
    filterset = filtersets.DataFileFilterSet
    filterset_form = forms.DataFileFilterForm
    table = tables.DataFileTable
    actions = ('edit',)

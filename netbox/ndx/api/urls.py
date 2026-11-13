from netbox.api.routers import NetBoxRouter

from . import views

router = NetBoxRouter()
router.APIRootView = views.NDXRootView
router.register('import-records', views.ImportRecordViewSet)
router.register('enrichments', views.EnrichmentViewSet)
router.register('catalog', views.CatalogViewSet, basename='catalog')
router.register('sync', views.SyncViewSet, basename='sync')

app_name = 'ndx-api'
urlpatterns = router.urls

from django.urls import path

from . import views


urlpatterns = (
    path('models/', views.DummyModelsView.as_view(), name='dummy_model_list'),
    path('models/add/', views.DummyModelAddView.as_view(), name='dummy_model_add'),

    path('netboxmodel/', views.DummyNetBoxModelView.as_view(), name='dummynetboxmodel_list'),
    path('netboxmodel/add/', views.DummyNetBoxModelView.as_view(), name='dummynetboxmodel_add'),
    path('netboxmodel/import/', views.DummyNetBoxModelView.as_view(), name='dummynetboxmodel_bulk_import'),
    path('netboxmodel/<int:pk>/', views.DummyNetBoxModelView.as_view(), name='dummynetboxmodel'),
)

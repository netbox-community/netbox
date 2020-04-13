from django.urls import path

from . import views


urlpatterns = (
    path('models/', views.DummyModelsView.as_view(), name='dummy_models'),
)

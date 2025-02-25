from django.urls import include, path

from extras import views
from utilities.urls import get_model_urls


app_name = 'extras'
urlpatterns = [

    path('custom-fields/', include(get_model_urls('extras', 'customfield', detail=False))),
    path('custom-fields/<int:pk>/', include(get_model_urls('extras', 'customfield'))),

    path('custom-field-choices/', include(get_model_urls('extras', 'customfieldchoiceset', detail=False))),
    path('custom-field-choices/<int:pk>/', include(get_model_urls('extras', 'customfieldchoiceset'))),

    path('custom-links/', include(get_model_urls('extras', 'customlink', detail=False))),
    path('custom-links/<int:pk>/', include(get_model_urls('extras', 'customlink'))),

    path('export-templates/', include(get_model_urls('extras', 'exporttemplate', detail=False))),
    path('export-templates/<int:pk>/', include(get_model_urls('extras', 'exporttemplate'))),

    path('saved-filters/', include(get_model_urls('extras', 'savedfilter', detail=False))),
    path('saved-filters/<int:pk>/', include(get_model_urls('extras', 'savedfilter'))),

    path('bookmarks/', include(get_model_urls('extras', 'bookmark', detail=False))),
    path('bookmarks/<int:pk>/', include(get_model_urls('extras', 'bookmark'))),

    path('notification-groups/', include(get_model_urls('extras', 'notificationgroup', detail=False))),
    path('notification-groups/<int:pk>/', include(get_model_urls('extras', 'notificationgroup'))),

    path('notifications/', views.NotificationsView.as_view(), name='notifications'),
    path('notifications/', include(get_model_urls('extras', 'notification', detail=False))),
    path('notifications/<int:pk>/', include(get_model_urls('extras', 'notification'))),

    path('subscriptions/', include(get_model_urls('extras', 'subscription', detail=False))),
    path('subscriptions/<int:pk>/', include(get_model_urls('extras', 'subscription'))),

    path('webhooks/', include(get_model_urls('extras', 'webhook', detail=False))),
    path('webhooks/<int:pk>/', include(get_model_urls('extras', 'webhook'))),

    path('event-rules/', include(get_model_urls('extras', 'eventrule', detail=False))),
    path('event-rules/<int:pk>/', include(get_model_urls('extras', 'eventrule'))),

    path('tags/', include(get_model_urls('extras', 'tag', detail=False))),
    path('tags/<int:pk>/', include(get_model_urls('extras', 'tag'))),

    path('config-contexts/', include(get_model_urls('extras', 'configcontext', detail=False))),
    path('config-contexts/<int:pk>/', include(get_model_urls('extras', 'configcontext'))),

    path('config-templates/', include(get_model_urls('extras', 'configtemplate', detail=False))),
    path('config-templates/<int:pk>/', include(get_model_urls('extras', 'configtemplate'))),

    path('image-attachments/', include(get_model_urls('extras', 'imageattachment', detail=False))),
    path('image-attachments/<int:pk>/', include(get_model_urls('extras', 'imageattachment'))),

    path('journal-entries/', include(get_model_urls('extras', 'journalentry', detail=False))),
    path('journal-entries/<int:pk>/', include(get_model_urls('extras', 'journalentry'))),

    # User dashboard
    path('dashboard/reset/', views.DashboardResetView.as_view(), name='dashboard_reset'),
    path('dashboard/widgets/add/', views.DashboardWidgetAddView.as_view(), name='dashboardwidget_add'),
    path(
        'dashboard/widgets/<uuid:id>/configure/',
        views.DashboardWidgetConfigView.as_view(),
        name='dashboardwidget_config'
    ),
    path(
        'dashboard/widgets/<uuid:id>/delete/',
        views.DashboardWidgetDeleteView.as_view(),
        name='dashboardwidget_delete'
    ),

    # Scripts
    path('scripts/', views.ScriptListView.as_view(), name='script_list'),
    path('scripts/add/', views.ScriptModuleCreateView.as_view(), name='scriptmodule_add'),
    path('scripts/results/<int:job_pk>/', views.ScriptResultView.as_view(), name='script_result'),
    path('scripts/<int:pk>/', views.ScriptView.as_view(), name='script'),
    path('scripts/<str:module>.<str:name>/', views.ScriptView.as_view(), name='script'),
    path('scripts/<int:pk>/source/', views.ScriptSourceView.as_view(), name='script_source'),
    path('scripts/<str:module>.<str:name>/source/', views.ScriptSourceView.as_view(), name='script_source'),
    path('scripts/<int:pk>/jobs/', views.ScriptJobsView.as_view(), name='script_jobs'),
    path('scripts/<str:module>.<str:name>/jobs/', views.ScriptJobsView.as_view(), name='script_jobs'),
    path('script-modules/<int:pk>/', include(get_model_urls('extras', 'scriptmodule'))),

    # Markdown
    path('render/markdown/', views.RenderMarkdownView.as_view(), name="render_markdown"),
]

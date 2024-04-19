from django.urls import path, include

from . import views


urlpatterns = [
    # Site Views

    path('telescopes/', views.TelescopeListView.as_view(), name='telescope.list'),
    path('telescopes/<int:pk>/', views.TelescopeDetailView.as_view(), name='telescope.update'),
    path('telescopes/<int:pk>/ping', views.TelescopeSendPingEventView.as_view(), name='telescope.ping'),
    path('telescopes/<int:pk>/reconfigure', views.TelescopeSendReconfigureEventView.as_view(), name='telescope.reconfigure'),
    path('telescopes/<int:pk>/regenerate-token', views.TelescopeRegenerateTokenView.as_view(), name='telescope.regenerate-token'),
    path('telescopes/<int:pk>/observations', views.TelescopeObservationListView.as_view(), name='telescope.observation-list'),

    path('observations/', views.ObservationListView.as_view(), name='observation.list'),
    path('observations/<int:pk>', views.ObservationDetailView.as_view(), name='observation.update'),
    path('observations/<int:pk>/configurations', views.ObservationConfigurationListView.as_view(), name='observation.configuration-list'),
    path('observations/<int:pk>/samples', views.ObservationSampleListView.as_view(), name='observation.sample-list'),

    path('configurations/<int:pk>', views.ConfigurationDetailView.as_view(), name='configuration.update'),

    # API Views

    path('api/telescope/<int:pk>/health-check', views.TelescopeHealthCheckView.as_view(), name='telescope.health-check'),
    path('api/telescope/<int:pk>/tasks', views.TelescopeAPIView.as_view(), name='telescope.tasks'),

    path('api/observation/<int:pk>/transmit', views.SampleDataTransmitView.as_view(), name='observation.transmit'),
]

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

    # API Views

    path('api/telescope/<int:pk>/health-check', views.TelescopeHealthCheckView.as_view(), name='telescope.health-check'),
    path('api/telescope/<int:pk>/tasks', views.TelescopeAPIView.as_view(), name='telescope.tasks'),

    path('api/telescope/<int:pk>/transmit', views.SampleDataTransmitView.as_view(), name='observation.transmit'),
]

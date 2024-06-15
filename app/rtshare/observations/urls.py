from django.urls import path, include

from . import views


urlpatterns = [
    path('observations/', views.ObservationListView.as_view(), name='observation.list'),
    path('observations/<int:pk>', views.ObservationDetailView.as_view(), name='observation.update'),
    path('observations/<int:pk>/configurations', views.ObservationConfigurationListView.as_view(), name='observation.configuration-list'),
    path('observations/<int:pk>/samples', views.ObservationSampleListView.as_view(), name='observation.sample-list'),
    path('configurations/<int:pk>', views.ConfigurationDetailView.as_view(), name='configuration.update'),
]

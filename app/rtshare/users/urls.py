from django.urls import path

from . import views


urlpatterns = [
    # Site Views

    path(
        'users/<int:pk>/events/',
        views.UserEventsListView.as_view(),
        name='user.events-list',
    ),

    path(
        'users/<int:pk>/',
        views.AccountView.as_view(),
        name='user.account',
    ),
]

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views
from django.contrib import admin
from django.urls import path, include
import django_eventstream
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view()
@permission_classes([IsAuthenticated])
def events(*args, **kwargs):
    # NOTE: This wrapped view allows us to use DRF's Token-Based
    # Authentication Systems on top of the existing Event Stream
    # functionality. Otherwise, it cannot perform Token Auth.
    return django_eventstream.views.events(*args, **kwargs)


urlpatterns = [
    path('', include('public.urls')),
    path('', include('telescope.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('api/events/<channel>', events),
    # path(
    #     'events/<channel>',
    #     django_eventstream.views.events,
    #     name='event-stream',
    # ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

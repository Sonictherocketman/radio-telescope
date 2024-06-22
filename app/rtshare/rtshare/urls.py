from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import authenticate
from django.contrib import admin
from django.urls import path, include
import django_eventstream


def events(request, **kwargs):
    if user := authenticate(request):
        request.user = user
    return django_eventstream.views.events(request, **kwargs)


urlpatterns = [
    path('', include('observations.urls')),
    path('', include('public.urls')),
    path('', include('telescope.urls')),
    path('', include('users.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('api/events/<channel>', events, name='event-stream'),
    path(
        'stream/events/',
        django_eventstream.views.events,
        name='multi-event-stream',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

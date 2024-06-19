from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
import django_eventstream


urlpatterns = [
    path('', include('observations.urls')),
    path('', include('public.urls')),
    path('', include('telescope.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('api/events/<channel>', django_eventstream.views.events),
    # path(
    #     'events/<channel>',
    #     django_eventstream.views.events,
    #     name='event-stream',
    # ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

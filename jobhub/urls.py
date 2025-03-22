from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('django-admin/', admin.site.urls),  # Alternative admin URL for testing
    path('', include('authentication.urls')),
    path('jobs/', views.redirect_to_home, name='redirect_to_jobs'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

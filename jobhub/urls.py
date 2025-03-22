from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = settings.ADMIN_SITE_HEADER

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('jobs/', views.redirect_to_home, name='redirect_to_jobs'),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

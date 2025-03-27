from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

admin.site.site_header = settings.ADMIN_SITE_HEADER

# Non-translatable URLs
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Add URL for language switcher
]

# Translatable URLs
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('jobs/', views.redirect_to_home, name='redirect_to_jobs'),
    prefix_default_language=True,  # Include prefix for default language too
)

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

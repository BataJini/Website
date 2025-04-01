from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import handler404

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

# Catch-all pattern for unmatched URLs
urlpatterns.append(re_path(r'^(?!en/|pl/).*$', views.custom_404))

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'jobhub.views.custom_404'

from django.contrib import admin
from .models import CustomUser, Job

# Temporary simplified admin to debug issues
admin.site.register(CustomUser)
admin.site.register(Job)

# Commenting out the complex admin classes for debugging
'''
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'full_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'password1', 'password2'),
        }),
    )

# Register the CustomUser model with our custom admin class
admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'salary', 'posted_date', 'is_remote', 'is_featured', 'is_archived')
    list_filter = ('is_remote', 'is_featured', 'is_archived', 'type', 'posted_date')
    list_editable = ('is_featured', 'is_archived')
    search_fields = ('title', 'company', 'description', 'location')
    date_hierarchy = 'posted_date'
    
    actions = ['archive_jobs', 'unarchive_jobs']
    
    def get_queryset(self, request):
        # Override to show archived jobs in a separate view
        if 'archived' in request.path:
            return super().get_queryset(request).filter(is_archived=True)
        return super().get_queryset(request).filter(is_archived=False)
    
    def archive_jobs(self, request, queryset):
        queryset.update(is_archived=True)
    archive_jobs.short_description = "Archive selected jobs"
    
    def unarchive_jobs(self, request, queryset):
        queryset.update(is_archived=False)
    unarchive_jobs.short_description = "Unarchive selected jobs"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('archived/', self.admin_site.admin_view(self.archived_jobs_view), name='job-archived'),
        ]
        return custom_urls + urls
    
    def archived_jobs_view(self, request):
        self.is_archived = True
        return self.changelist_view(request)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_archived'] = getattr(self, 'is_archived', False)
        extra_context['archived_count'] = Job.objects.filter(is_archived=True).count()
        return super().changelist_view(request, extra_context=extra_context)
    
    def view_on_site(self, obj):
        return None  # Disable the "View on site" link since we don't have a public view
'''
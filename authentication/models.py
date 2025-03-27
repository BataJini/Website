from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Job(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    company = models.CharField(_('Company'), max_length=255)
    description = models.TextField(_('Description'))
    location = models.CharField(_('Location'), max_length=255)
    salary = models.CharField(_('Salary'), max_length=100, blank=True, null=True)
    job_url = models.URLField(_('Job URL'), blank=True, null=True)
    is_remote = models.BooleanField(_('Remote'), default=False)
    is_featured = models.BooleanField(_('Featured'), default=False)
    is_archived = models.BooleanField(_('Archived'), default=False)
    type = models.CharField(_('Job Type'), max_length=50, choices=[
        ('Full-time', _('Full-time')),
        ('Part-time', _('Part-time')),
        ('Contract', _('Contract')),
        ('Temporary', _('Temporary'))
    ], default='Full-time')
    posted_date = models.DateTimeField(_('Posted Date'), default=timezone.now)
    requirements = models.TextField(_('Requirements'), blank=True, null=True)
    nice_to_have = models.TextField(_('Nice to Have'), blank=True, null=True)
    created_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='jobs', null=True, blank=True, verbose_name=_('Created By'))
    
    # Add company logo field
    company_logo = models.ImageField(_('Company Logo'), upload_to='company_logos/', blank=True, null=True)
    
    # Add skills as tags
    tags = TaggableManager(blank=True, verbose_name=_("Skills"))

    def __str__(self):
        return f"{self.title} at {self.company}"

    class Meta:
        unique_together = ('title', 'company', 'location')
        ordering = ['-posted_date']
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')

class PolishCity(models.Model):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    name_pl = models.CharField(_('Polish Name'), max_length=100, blank=True, null=True)
    voivodeship = models.CharField(_('Voivodeship'), max_length=100, blank=True, null=True)  # województwo
    population = models.IntegerField(_('Population'), blank=True, null=True)

    def __str__(self):
        return self.name
    
    def get_display_name(self, language_code='en'):
        if language_code == 'pl' and self.name_pl:
            return self.name_pl
        return self.name

    class Meta:
        verbose_name = _('Polish City')
        verbose_name_plural = _('Polish Cities')
        ordering = ['name']
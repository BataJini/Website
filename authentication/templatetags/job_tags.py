from django import template
import json
import re
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def parse_requirements(requirements_json):
    try:
        if requirements_json:
            # Try to parse as JSON first
            return json.loads(requirements_json)
    except json.JSONDecodeError:
        # If not valid JSON, return it as is if it's a list
        if isinstance(requirements_json, list):
            return requirements_json
        # If it's a string that's not JSON, return as a single item list
        if requirements_json and isinstance(requirements_json, str):
            return [requirements_json]
    return []

@register.filter
def format_location(location_str):
    """
    Format location string to use commas between locations instead of slashes.
    If there are more than 2 locations, show first 2 followed by '+ X more'
    """
    if not location_str:
        return ""
    
    locations = location_str.split(' / ')
    
    if len(locations) <= 2:
        return ", ".join(locations)
    else:
        first_two = locations[:2]
        remaining = len(locations) - 2
        return f"{', '.join(first_two)} + {remaining} more"

@register.filter
def remove_minutes(timesince_str):
    # Extract the first time unit mentioned
    if 'week' in timesince_str or 'weeks' in timesince_str:
        match = re.search(r'(\d+)\s*(week|weeks)', timesince_str)
        if match:
            num = match.group(1)
            unit = 'week' if num == '1' else 'weeks'
            return f"{num} {unit}"
    elif 'day' in timesince_str or 'days' in timesince_str:
        match = re.search(r'(\d+)\s*(day|days)', timesince_str)
        if match:
            num = match.group(1)
            unit = 'day' if num == '1' else 'days'
            return f"{num} {unit}"
    elif 'hour' in timesince_str or 'hours' in timesince_str:
        match = re.search(r'(\d+)\s*(hour|hours)', timesince_str)
        if match:
            num = match.group(1)
            unit = 'hour' if num == '1' else 'hours'
            return f"{num} {unit}"
    elif 'minute' in timesince_str or 'minutes' in timesince_str:
        match = re.search(r'(\d+)\s*(minute|minutes)', timesince_str)
        if match:
            num = match.group(1)
            unit = 'minute' if num == '1' else 'minutes'
            return f"{num} {unit}"
    return timesince_str

@register.filter
def get_job_tags(job):
    """
    Extract tags from a job object
    """
    if hasattr(job, 'tags'):
        return job.tags.all()
    return []

@register.filter
def format_tag(tag_name):
    """
    Format skill tag name - if it has more than 3 words, truncate it
    to show only the first 3 words followed by '...'
    """
    if not tag_name:
        return ""
    
    words = tag_name.split()
    
    if len(words) > 3:
        return " ".join(words[:3]) + "..."
    else:
        return tag_name

@register.filter
def limit_tags(tags):
    """
    If any tag has long text (>15 chars), return only 3 tags,
    otherwise return all tags
    """
    if not tags:
        return []
    
    has_long_tags = any(len(str(tag.name)) > 15 for tag in tags)
    
    if has_long_tags:
        return tags[:3]
    return tags

@register.filter
def safe_html(html_text):
    """
    Mark HTML text as safe for rendering in templates
    """
    if not html_text:
        return ""
    return mark_safe(html_text) 
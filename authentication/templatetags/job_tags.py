from django import template
import json
import re

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
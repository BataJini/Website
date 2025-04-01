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
    Format location string to show only first location followed by '+ X more'.
    If Remote is one of the locations, it will always be shown first.
    Also handles duplicate Remote locations and multiple separators.
    """
    if not location_str:
        return ""
    
    # First split by comma
    comma_split = [loc.strip() for loc in location_str.split(',')]
    
    # Then split by forward slash and flatten the list
    locations = []
    for loc in comma_split:
        locations.extend([l.strip() for l in loc.split('/')])
    
    # Remove duplicates while preserving order, but prioritize Remote
    seen = set()
    unique_locations = []
    has_remote = False
    
    for loc in locations:
        # Skip empty strings
        if not loc:
            continue
        # Normalize "Remote" variations
        normalized_loc = loc.lower()
        if normalized_loc == "remote":
            if not has_remote:
                has_remote = True
                unique_locations.insert(0, "Remote")
            continue
        if loc not in seen:
            seen.add(loc)
            unique_locations.append(loc)
    
    if len(unique_locations) <= 1:
        return unique_locations[0] if unique_locations else ""
    else:
        first = unique_locations[0]
        remaining = len(unique_locations) - 1
        return f"{first} +{remaining}"

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

@register.filter
def split(value, delimiter=','):
    """
    Split a string by delimiter and return a list
    """
    if not value:
        return []
    return value.split(delimiter)

@register.filter
def extract_tech_tags(job_title, max_tags=None):
    """
    Extract technology tags from job title and limit to max_tags if specified.
    If job title is longer than 40 characters, limit to 3 tags max unless otherwise specified.
    """
    if not job_title:
        return []
    
    # Default max_tags based on title length if not specified
    if max_tags is None:
        max_tags = 3 if len(job_title) > 40 else 999
    
    job_title_lower = job_title.lower()
    tech_tags = []
    
    # List of technology keywords to look for
    technologies = [
        'python', 'django', 'react', 'java', 'kotlin',
        'typescript', 'javascript', 'aws', 'node.js', 'spring boot'
    ]
    
    # Add tags that appear in the title
    for tech in technologies:
        if tech in job_title_lower and len(tech_tags) < max_tags:
            tech_tags.append(tech.title())
    
    return tech_tags

@register.filter
def limit_title_tags(job_title, tags):
    """
    If the job title is longer than 40 characters, limit to 3 tags,
    otherwise return all tags
    """
    if not tags:
        return []
    
    if len(job_title) > 40:
        return tags[:3]
    return tags

@register.filter
def add_utm_params(url, job_title=None):
    """
    Add UTM parameters to job URLs with proper structure
    """
    from datetime import datetime
    import re
    
    # Get current month name in lowercase
    current_month = datetime.now().strftime('%B').lower()
    
    # Clean the job title if provided
    clean_job_title = ""
    if job_title:
        # Remove special characters and convert spaces to hyphens
        clean_job_title = re.sub(r'[^a-zA-Z0-9\s-]', '', job_title)
        clean_job_title = clean_job_title.strip().replace(" ", "-").lower()
    
    # Define UTM parameters
    utm_params = {
        'utm_source': 'jobhub',
        'utm_medium': 'job_post',
        'utm_campaign': f'{current_month}_hiring'
    }
    
    # Add utm_content if we have a job title
    if clean_job_title:
        utm_params['utm_content'] = clean_job_title
    
    # Check if URL already has parameters
    if '?' in url:
        utm_string = '&'
    else:
        utm_string = '?'
    
    # Build UTM string
    utm_string += '&'.join([f'{key}={value}' for key, value in utm_params.items()])
    
    # Remove any trailing slashes from the base URL
    base_url = url.rstrip('/')
    return f'{base_url}{utm_string}'
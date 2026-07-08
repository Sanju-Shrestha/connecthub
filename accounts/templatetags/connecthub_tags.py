from django import template 
from django.utils import timezone 
 
register = template.Library() 
 
 

# SIMPLE TAGS 
 
@register.simple_tag 
def is_following(viewer, target_user): 
    """ 
    Check if viewer's profile follows target_user's profile. 
    Returns True or False. 
 
    Usage in template: 
        {% load connecthub_tags %} 
        {% is_following request.user member as following_status %} 
        {% if following_status %}Following{% else %}Follow{% endif %} 
    """ 
    if not viewer.is_authenticated: 
        return False 
    try: 
        return viewer.profile.is_following(target_user.profile) 
    except Exception: 
        return False 
 
 
@register.simple_tag 
def get_avatar_url(user): 
    """ 
    Return the avatar URL for a user, or a default image path. 
    Usage: {% get_avatar_url member as avatar_url %} 
    """ 
    try: 
        if user.profile.avatar: 
            return user.profile.avatar.url 
    except Exception: 
        pass 
    return "/static/images/default_avatar.png"


# FILTERS

@register.filter(name="format_count") 
def format_count(value): 
    """ 
    Format large numbers with K/M suffix. 
    Usage: {{ post.likes.count|format_count }} 
    Examples: 1500 → 1.5K, 1000000 → 1.0M, 500 → 500 
    """ 
    try: 
        value = int(value) 
        if value >= 1_000_000: 
            return f"{value / 1_000_000:.1f}M" 
        elif value >= 1_000: 
            return f"{value / 1_000:.1f}K" 
        return str(value) 
    except (TypeError, ValueError): 
        return str(value) 
 
 
@register.filter(name="time_since_short") 
def time_since_short(value): 
    """ 
    Returns a short relative time string. 
    Usage: {{ post.created_at|time_since_short }} 
    Examples: "2m ago", "3h ago", "5d ago", "Jan 12" 
    """ 
    now = timezone.now() 
    try: 
        diff = now - value 
    except TypeError: 
        return str(value) 
 
    seconds = diff.total_seconds() 
    if seconds < 60: 
        return "just now" 
    elif seconds < 3600: 
        return f"{int(seconds // 60)}m ago" 
    elif seconds < 86400: 
        return f"{int(seconds // 3600)}h ago" 
    elif seconds < 604800: 
        return f"{int(seconds // 86400)}d ago" 
    else: 
        return value.strftime("%b %d") 
 
 
@register.filter(name="truncate_chars") 
def truncate_chars(value, max_length): 
    """ 
    Truncate a string to max_length characters. 
    Usage: {{ user.profile.bio|truncate_chars:100 }} 
    """ 
    try: 
        if len(value) <= max_length: 
            return value 
        return value[:max_length].rstrip() + "…" 
    except (TypeError, AttributeError): 
        return value
 
from .models import Profile 
 
 
def site_context(request): 
    """ 
    Injects commonly-needed data into EVERY template context. 
    This avoids passing the same variables in every single view. 
 
    Available in all templates: 
        {{ my_profile }}     ← logged-in user's Profile object 
        {{ unread_count }}   ← number of unread notifications (Day 6) 
        {{ total_members }}  ← total number of active ConnectHub members 
    """ 
    context = { 
        "my_profile": None, 
        "unread_count": 0, 
        "total_members": 0, 
    } 
 
    if request.user.is_authenticated: 
        try: 
            context["my_profile"] = request.user.profile 
        except Profile.DoesNotExist: 
            pass 
 
        from django.contrib.auth.models import User 
        context["total_members"] = User.objects.filter(is_active=True).count() 
 
        # Placeholder for notification count (real implementation in Day 6) 
        context["unread_count"] = 0 
 
    return context 
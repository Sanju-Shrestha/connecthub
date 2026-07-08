from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model =Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"
    fields = ("bio", "avatar", "date_of_birth", "location", "website")

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff","is_active","date_joined")
    search_fields = ("username","email","first_name","last_name")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "location")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Users", {"fields": ("user",)}),
        ("Personal Info", {"fields": ("bio","avatar", "date_of_birth", "location", "website")}),
        ("Timestamps", {"fields": ("created_at","updated_at"), "classes": ("collapse",)}),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)




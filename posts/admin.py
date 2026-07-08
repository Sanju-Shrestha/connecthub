from django.contrib import admin 
from .models import Post,Comment
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
 
@admin.register(Post) 
class PostAdmin(admin.ModelAdmin): 
    list_display  = ["id", "author", "status", "created_at", "updated_at"] 
    list_filter   = ["status", "created_at"] 
    search_fields = ["author__username", "content"] 
    readonly_fields = ["created_at", "updated_at"] 
    list_editable = ["status"]   # change status directly from list view 
    ordering      = ["-created_at"] 


###

@admin.register(Comment) 
class CommentAdmin(admin.ModelAdmin): 
    list_display   = ["id", "author", "post", "created_at", "short_content"]
    list_filter    = ["created_at"] 
    search_fields  = ["author__username", "content", "post__id"] 
    readonly_fields = ["created_at"] 
    ordering       = ["-created_at"] 
 
    def short_content(self, obj): 
        """Show first 60 chars of comment in list view.""" 
        return obj.content[:60] + "…" if len(obj.content) > 60 else obj.content 
    short_content.short_description = "Preview" 
###

class ConnectHubAdminSite(admin.AdminSite):
    site_header = "ConnectHub Administration"
    site_tile = "ConnectHub Admin"
    index_title = "Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom = [path("stats/", self.admin_view(self.stats_views), name="stats")]
        return custom + urls
    def stats_views(self, request):
        context = dict(
            self.each_context(request),
            total_users = User.objects.count(),
            total_posts=Post.objects.count(),
            total_comments=Comment.objects.count(),
        )
        return TemplateResponse(request, "admin/stats.html", context)
    
connecthub_admin = ConnectHubAdminSite(name="connecthub_admin")
connecthub_admin.register(Post, PostAdmin)
connecthub_admin.register(Comment, CommentAdmin)



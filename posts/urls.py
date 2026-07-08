 
from django.urls import path 
from . import views 
 
app_name = "posts" 
 
urlpatterns = [ 
    path("",                    views.PostListView.as_view(),  name="post_list"), 
    path("create/",             views.PostCreateView.as_view(),name="post_create"), 
    path("<int:pk>/",           views.PostDetailView.as_view(),name="post_detail"), 
    path("<int:pk>/delete/",    views.PostDeleteView.as_view(),name="post_delete"), 
    path("user/<str:username>/",views.UserPostListView.as_view(),name="user_posts"), 
 
    path("<int:pk>/comment/",    views.add_comment,    name="add_comment"), 
    path("<int:pk>/like/",       views.like_post,      name="like_post"), 
    path("comment/<int:comment_pk>/delete/", 
                                 views.delete_comment, name="delete_comment"),
] 
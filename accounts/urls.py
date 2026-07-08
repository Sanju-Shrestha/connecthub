 
from django.urls import path 
from django.contrib.auth import views as auth_views 
from . import views 
 
app_name = "accounts" 
 
urlpatterns = [ 
    # ─── Registration & Auth (from Day 2) ──────────────────────── 
    path("register/", views.register, name="register"), 
    path("login/", 
         auth_views.LoginView.as_view(template_name="accounts/login.html", 
                                      redirect_authenticated_user=True), 
         name="login"), 
    path("logout/", auth_views.LogoutView.as_view(), name="logout"), 
    path("password-change/", 
         auth_views.PasswordChangeView.as_view( 
             template_name="accounts/password_change.html", 
             success_url="/accounts/password-change/done/"), 
         name="password_change"), 
    path("password-change/done/", 
         auth_views.PasswordChangeDoneView.as_view( 
             template_name="accounts/password_change_done.html"), 
         name="password_change_done"), 
 
    # ─── Dashboard (FBV from Day 2) ─────────────────────────── 
    path("dashboard/", views.dashboard, name="dashboard"), 
 
    # ─── Members Directory (NEW – CBV) ────────────────────── 
    path("members/", 
         views.MemberListView.as_view(), 
         name="member_list"), 
 
    # ─── Profile URLs (CBVs replace FBVs) ────────────────── 
    path("profile/", 
         views.UserDetailView.as_view(), 
         {"username": None},     # handled in get_object() 
         name="profile_detail"), 
    
    path("profile/edit/", 
         views.profile_edit,     # Keep FBV for two-form pattern (Day 2) 
         name="profile_edit"), 

    path("profile/cbv-edit/", 
         views.ProfileUpdateView.as_view(), 
         name="profile_edit_cbv"), 
    path("profile/delete/", 
         views.ProfileDeleteView.as_view(), 
         name="profile_delete"),
    path("profile/<str:username>/", 
         views.UserDetailView.as_view(), 
         name="user_profile"),
     path("follow/<str:username>/", views.toggle_follow, name="toggle_follow"),

] 

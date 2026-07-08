 
from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User 
from django.contrib import messages 
from django.views.generic import TemplateView 
from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm 
from .models import Profile 
###
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from posts.models import Post
from django.views.decorators.http import require_POST
###
 
 
def register(request): 
    """ 
    User registration view. 
    GET:  Show empty registration form 
    POST: Validate form, create user, log them in, redirect to dashboard 
 
    After saving the form, the post_save signal automatically creates
     a Profile for the new user (set up in Day 1). 
    """ 
    # If user is already logged in, redirect to dashboard 
    if request.user.is_authenticated: 
        return redirect("accounts:dashboard") 
 
    if request.method == "POST": 
        form = RegistrationForm(request.POST) 
        if form.is_valid(): 
            # Save the user to the database 
            user = form.save() 
            # Log the user in immediately after registration 
            # (no need to make them log in separately) 
            login(request, user) 
            messages.success( 
                request, 
                f"Welcome to ConnectHub, {user.first_name}! Your account has been created." 
            ) 
            return redirect("accounts:dashboard") 
        else: 
            messages.error( 
                request, 
                "Please correct the errors below." 
            ) 
    else: 
        form = RegistrationForm() 
 
    return render(request, "accounts/register.html", {"form": form}) 
 
 
@login_required 
def dashboard(request): 
    """ 
    Main dashboard view – only accessible to logged-in users. 
    Shows a welcome message and summary cards. 
    The @login_required decorator automatically redirects 
    anonymous users to the login page. 
    """ 
    recent_posts = ( 
    Post.published.all() 
    .select_related("author", "author__profile") 
    .order_by("-created_at")[:5] 
    ) 
    return render(request, "accounts/dashboard.html", { 
    "user": request.user, 
    "recent_posts": recent_posts, 
    }) 
 
 
@login_required 
def profile_detail(request, username=None):
    """ 
    View a user profile by username. 
    If no username given, show the logged-in user's own profile. 
    """ 
    if username: 
        profile_user = get_object_or_404(User, username=username) 
    else: 
        profile_user = request.user 
 
    profile = get_object_or_404(Profile, user=profile_user) 
    return render(request, "accounts/profile_detail.html", { 
        "profile_user": profile_user, 
        "profile": profile, 
        "is_own_profile": profile_user == request.user, 
    }) 
 
 
@login_required 
def profile_edit(request): 
    """ 
    Profile edit view – two forms on one page: 
      1. UserUpdateForm   → updates User.first_name, last_name, email 
      2. ProfileUpdateForm → updates Profile.bio, avatar, location, etc. 
 
    Both forms must be valid before we save either one. 
    enctype="multipart/form-data" is required in the template 
    because we have a file upload (avatar). 
    """ 
    if request.method == "POST": 
        user_form    = UserUpdateForm(request.POST, instance=request.user) 
        profile_form = ProfileUpdateForm( 
            request.POST, 
            request.FILES,          # required for file uploads 
            instance=request.user.profile 
        ) 
        if user_form.is_valid() and profile_form.is_valid(): 
            user_form.save() 
            profile_form.save() 
            messages.success(request, "Your profile has been updated successfully!") 
            return redirect("accounts:profile_detail") 
        else: 
            messages.error(request, "Please correct the errors below.") 
    else: 
        # Pre-fill forms with current data 
        user_form    = UserUpdateForm(instance=request.user) 
        profile_form = ProfileUpdateForm(instance=request.user.profile) 
 
    return render(request, "accounts/profile_edit.html", { 
        "user_form": user_form, 
        "profile_form": profile_form, 
    }) 

# NEW CLASS BASED VIEWS --- FOR MEMBERS

class MemberListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "accounts/member_list.html"
    context_object_name = "members"
    paginate_by = 2

    def get_queryset(self):
        queryset = User.objects.filter(
            is_active = True
        ).exclude(
            pk=self.request.user.pk
        ).select_related("profile").order_by("username")

        self.search_query = self.request.GET.get("q","").strip()
        if self.search_query:
            queryset = queryset.filter(
                Q(username__icontains=self.search_query)
            )
        return queryset

        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = getattr(self, "search_query", "")
        context["total_members"] = User.objects.filter(is_active=True).count()
        
        return context


        
class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/profile_detail.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_object(self):
        username = self.kwargs.get("username")

        if username is None:
            return self.request.user
        return get_object_or_404(User, username=username)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        profile = get_object_or_404(Profile, user=profile_user) 
        context["profile"] = get_object_or_404(Profile, user=profile_user)
        context["is_own_profile"] = profile_user == self.request.user
        #context["is_following"] = False
        ###
        context["is_following"] = ( 
            self.request.user.profile.is_following(profile) 
            if self.request.user != profile_user 
            else False 
        ) 
        context["follower_count"]  = profile.followers.count() 
        context["following_count"] = profile.following.count() 
 
        # Recent posts by this user (for profile page) 
        from posts.models import Post 
        context["user_posts"] = ( 
            Post.published 
            .filter(author=profile_user) 
            .select_related("author", "author__profile") 
            .order_by("-created_at")[:6] 
        )
        ###

        return context
    


###
 
class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView): 
    """ 
    Lets a user update their own profile. 
    UserPassesTestMixin ensures users can only edit THEIR OWN profile. 
 
    Note: We only update Profile fields here. 
    User fields (name/email) still use the FBV from Day 2. 
    """ 
    model = Profile 
    form_class = ProfileUpdateForm 
    template_name = "accounts/profile_edit_cbv.html" 
 
    def test_func(self): 
        """Called by UserPassesTestMixin. Must return True to allow access.""" 
        profile = self.get_object() 
        return self.request.user == profile.user 
 
    def get_object(self): 
        """Return the logged-in user's profile.""" 
        return get_object_or_404(Profile, user=self.request.user) 
 
    def get_success_url(self): 
        messages.success(self.request, "Profile updated successfully!") 
        return reverse_lazy( 
            "accounts:user_profile", 
            kwargs={"username": self.request.user.username} 
        ) 
 
 
class ProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView): 
    """ 
    Lets a user delete their own account. 
    Shows a confirmation page before deletion. 
    On deletion: User is deleted → CASCADE deletes Profile too. 
    """ 
    model = User 
    template_name = "accounts/profile_confirm_delete.html"
    success_url = reverse_lazy("accounts:register") 
 
    def test_func(self): 
        """Users can only delete their own account.""" 
        return self.get_object() == self.request.user 
 
    def get_object(self): 
        return self.request.user 
 
    def form_valid(self, form): 
        """Called when user confirms deletion. Log them out first.""" 
        user = self.get_object() 
        logout(self.request) 
        user.delete() 
        messages.success(self.request, "Your account has been deleted.") 
        return redirect(self.success_url) 


###

@login_required
@require_POST
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        messages.error(request, "You can't follow yourself.")
        return redirect("accounts:user_profile", username=username)
    
    my_profile = request.user.profile
    target_profile = target_user.profile

    if my_profile.following.filter(pk=target_profile.pk).exists():
        my_profile.following.remove(target_profile)
        messages.info(request, f"Unfollowed @{username}.")
    else:
        my_profile.following.add(target_profile)
        messages.success(request, f"You're now following @{username}.")

    return redirect("accounts:user_profile", username=username)

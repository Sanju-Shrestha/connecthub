from django.shortcuts import render, get_object_or_404, redirect 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin 
from django.contrib.auth.decorators import login_required 
from django.views.decorators.http import require_POST 
from django.views.generic import ListView, DetailView, CreateView, DeleteView 
from django.urls import reverse_lazy 
from django.contrib import messages 
from django.contrib.auth.models import User 
from django.db.models import Count, Q 
from .models import Post, Comment 
from .forms import PostForm, CommentForm 

 
class PostListView(LoginRequiredMixin, ListView):  
    """ 
    Feed of all published posts. 
    Now annotated with comment_count and like_count for display. 
    Uses both select_related (FK) and prefetch_related (M2M). 
    """ 
    model = Post 
    template_name = "posts/post_list.html" 
    context_object_name = "posts" 
    paginate_by = 10 
 
    def get_queryset(self): 
        return ( 
            Post.published.all() 
            .select_related("author", "author__profile") 
            .prefetch_related("likes", "comments") 
            .annotate( 
                comment_count=Count("comments", distinct=True), 
                total_likes=Count("likes", distinct=True), 
            ) 
            .order_by("-created_at") 
        ) 
 
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs) 
        # Pass liked post IDs so template can show filled/empty heart 
        if self.request.user.is_authenticated: 
            liked_ids = set( 
                self.request.user.liked_posts 
                .filter(status=Post.Status.PUBLISHED) 
                .values_list("pk", flat=True) 
            ) 
            context["liked_post_ids"] = liked_ids 
        else: 
            context["liked_post_ids"] = set() 
        return context 
 
 
class PostDetailView(LoginRequiredMixin, DetailView): 
    """ 
    Shows a single post with its full comment thread. 
    Passes comment form and like status to the template. 
    """ 
    model = Post 
    template_name = "posts/post_detail.html" 
    context_object_name = "post" 
 
    def get_queryset(self): 
        return ( 
            Post.objects.filter( 
                Q(status=Post.Status.PUBLISHED) | Q(author=self.request.user) 
            ) 
            .select_related("author", "author__profile") 
            .prefetch_related( 
                "likes", 
                "comments", 
                "comments__author", 
                "comments__author__profile", 
            ) 
        ) 
 
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs) 
        post = self.object 
        context["is_author"]      = post.author == self.request.user 
        context["is_liked"]       = post.is_liked_by(self.request.user) 
        context["like_count"]     = post.likes.count() 
        context["comment_form"]   = CommentForm() 
        context["comments"]       = post.comments.select_related( 
            "author", "author__profile" 
        ).order_by("created_at") 
        context["comment_count"]  = post.comments.count() 
        return context 
 
 
class PostCreateView(LoginRequiredMixin, CreateView): 
    model = Post 
    form_class = PostForm 
    template_name = "posts/post_form.html" 
 
    def form_valid(self, form): 
        form.instance.author = self.request.user 
        messages.success(self.request, "Your post has been published!") 
        return super().form_valid(form) 
 
    def form_invalid(self, form): 
        messages.error(self.request, "Please correct the errors below.") 
        return super().form_invalid(form) 
 
    def get_success_url(self): 
        return reverse_lazy("posts:post_detail", kwargs={"pk": self.object.pk}) 
 
 
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView): 
    model = Post 
    template_name = "posts/post_confirm_delete.html" 
    success_url = reverse_lazy("posts:post_list") 
 
    def test_func(self): 
        return self.request.user == self.get_object().author 
 
    def form_valid(self, form): 
        messages.success(self.request, "Your post has been deleted.") 
        return super().form_valid(form) 
 
 
class UserPostListView(LoginRequiredMixin, ListView): 
    model = Post 
    template_name = "posts/user_post_list.html" 
    context_object_name = "posts" 
    paginate_by = 10 
 
    def get_queryset(self): 
        self.post_author = get_object_or_404(User, username=self.kwargs["username"]) 
        return ( 
            Post.published.filter(author=self.post_author) 
            .select_related("author", "author__profile") 
            .prefetch_related("likes", "comments") 
            .annotate(
            comment_count=Count("comments", distinct=True),
            total_likes=Count("likes", distinct=True),
            )
            .order_by("-created_at") 
        ) 
 
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs) 
        context["post_author"] = self.post_author 
        return context 
 
 
 
@login_required 
@require_POST 
def add_comment(request, pk): 
    """ 
    POST-only view: adds a comment to a post. 
    On success or failure, redirects back to the post detail page. 
    Uses commit=False pattern to set post and author before saving. 
    """ 
    ###
    if not request.user.has_perm("posts.can_comment_post"):
        messages.error(request, "You do not have permission to comment.")
        return redirect("posts:post_detail", pk=pk)
    ###
    post = get_object_or_404(Post, pk=pk, status=Post.Status.PUBLISHED) 
    form = CommentForm(request.POST) 
 
    if form.is_valid(): 
        comment = form.save(commit=False) 
        comment.post   = post 
        comment.author = request.user 
        comment.save() 
        messages.success(request, "Comment added successfully.") 
    else: 
        # Show first validation error 
        error_msg = list(form.errors.values())[0][0] if form.errors else "Invalid comment." 
        messages.error(request, error_msg) 
 
    return redirect("posts:post_detail", pk=pk) 
 
 
@login_required 
@require_POST 
def like_post(request, pk): 
    """ 
    POST-only view: toggles like/unlike on a post. 
    If the user has already liked the post, this unlikes it. 
    If not liked, this likes it. 
    Django's M2M handles the unique constraint automatically. 
    """
    ### 
    ###
    post = get_object_or_404(Post, pk=pk, status=Post.Status.PUBLISHED)
    if not request.user.has_perm("posts.can_like_post"):
        messages.error(request, "You do not have permission to like posts.")
        return redirect("posts:post_detail", pk=pk)

    if post.likes.filter(pk=request.user.pk).exists(): 
        post.likes.remove(request.user) 
        messages.info(request, "You unliked this post.") 
    else: 
        post.likes.add(request.user) 
        messages.success(request, "You liked this post!") 
 
    # Redirect to the page that sent the request 
    # This lets like work from both the feed AND the detail page 
    next_url = request.POST.get("next", "") 
    if next_url: 
        return redirect(next_url) 
    return redirect("posts:post_detail", pk=pk)
@login_required 
@require_POST 
def delete_comment(request, comment_pk): 
    """ 
    POST-only view: deletes a comment. 
    Only the comment author or post author can delete a comment. 
    """ 
    comment = get_object_or_404(Comment, pk=comment_pk) 
 
    if request.user == comment.author or request.user == comment.post.author: 
        post_pk = comment.post.pk 
        comment.delete() 
        messages.success(request, "Comment deleted.") 
        return redirect("posts:post_detail", pk=post_pk) 
    else: 
        messages.error(request, "You cannot delete this comment.") 
        return redirect("posts:post_detail", pk=comment.post.pk) 



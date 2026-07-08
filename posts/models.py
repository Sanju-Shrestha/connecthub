from django.db import models 
from django.contrib.auth.models import User 
from django.urls import reverse 
 
 
class PublishedManager(models.Manager): 
    """ 
    Custom manager: Post.published.all() returns only published posts. 
    Use this in all public-facing views to ensure draft posts never appear. 
    """ 
    def get_queryset(self): 
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)
     
class Post(models.Model): 
    """ 
    Core post model for ConnectHub. 
    A post belongs to one author (User) and optionally has an image. 
    Likes (ManyToMany) are added in Day 5. 
    """ 
 
    class Status(models.TextChoices): 
        DRAFT     = "draft",     "Draft" 
        PUBLISHED = "published", "Published" 
 
    author = models.ForeignKey( 
        User, 
        on_delete=models.CASCADE, 
        related_name="posts", 
        verbose_name="Author", 
    ) 
    content = models.TextField( 
        verbose_name="Content", 
        help_text="Write your post here.", 
    ) 
    image = models.ImageField( 
        upload_to="posts/%Y/%m/", 
        blank=True, 
        null=True, 
        verbose_name="Image", 
        help_text="Optional image attachment (max 5MB, JPG/PNG).", 
    ) 
    status = models.CharField( 
        max_length=10, 
        choices=Status.choices, 
        default=Status.PUBLISHED, 
        verbose_name="Status", 
    )
    ### New: Likes
    likes = models.ManyToManyField(
        User,
        related_name="liked_posts",
        blank = True,
        verbose_name="Likes",
    ) 

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
 
    # ─── Managers ───────────────────────────────────────────── 
    objects   = models.Manager()    # default: returns all posts 
    published = PublishedManager()  # custom: returns only published 
 
    class Meta: 
        verbose_name = "Post" 
        verbose_name_plural = "Posts" 
        ordering = ["-created_at"]  # newest first 
        ###
        permissions = [
            ("can_like_post", "Can like posts"),
            ("can_comment_post", "Can comment on posts"),
        ]
        ###
 
    def __str__(self): 
        return f"Post by {self.author.username} at {self.created_at:%Y-%m-%d %H:%M}" 
 
    # ─── Custom model methods ──────────────────────────────── 
    def get_absolute_url(self): 
        """Canonical URL for this post. Used by admin and CreateView.""" 
        return reverse("posts:post_detail", kwargs={"pk": self.pk}) 
 
    def like_count(self): 
        """Number of likes. likes M2M field added""" 
        return self.likes.count()  
 
    def is_liked_by(self, user): 
        """Check if a given user has liked this post.""" 
        if not user.is_authenticated:
            return False
        return self.likes.filter(pk=user.pk).exists()
    
    ###
    def short_content(self, length=60):
        """
        Returns a shortened version of the post content.
        """
        if len(self.content) <= length:
            return self.content
        return self.content[:length].rstrip() + "..."
    ###

 
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name = "comments",
        verbose_name="Post",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Author",
    )
    content = models.TextField(
        max_length = 1000,
        verbose_name="Comment",
        help_text="Write your comment (max 1000 characters).",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural ="Comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on Post # {self.post_id}"

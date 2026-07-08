from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name = "profile",
        verbose_name="User",
    )
    bio = models.TextField(
        max_length= 500,
        blank=True,
        verbose_name="Biography",
        help_text="Write a short bio (max 500 characters)",
        )
    avatar = models.ImageField(
        upload_to="avatars/%Y/%m",
        default="avatars/default.png",
        verbose_name="Profile Picture",
    )
    date_of_birth = models.DateField(
        null = True,
        blank =True,
        verbose_name="Date of Birth",
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Location",
    )
    website = models.URLField(
        blank=True,
        verbose_name="Website",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    ###
    following = models.ManyToManyField(
        "self",
        symmetrical = False,
        related_name="followers",
        blank= True,
        verbose_name= "Following",
    )
    ###

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Profile of {self.user.username}"
    
    def get_absolute_url(self):
        return reverse("accounts:user_profile", kwargs={"username": self.user.username})
    
    ###
    def follower_count(self):
        return self.followers.count()
    
    def following_count(self):
        return self.following.count()
    
    def is_following(self, profile):
        return self.following.filter(pk=profile.pk).exists()
    ###
    







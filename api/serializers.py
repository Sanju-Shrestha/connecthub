from rest_framework import serializers 
from django.contrib.auth.models import User 
from accounts.models import Profile
from posts.models import Post, Comment

class ProfileSerializer(serializers.ModelSerializer):

    avatar_url = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = [
            "bio",
            "avatar_url",
            "date_of_birth",
            "location",
            "website",
        ]
        read_only_fields = ["avatar_url"]
    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None
    

 
class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(
        source="get_full_name",
        read_only=True
    )
    post_count = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "full_name",
            "email",
            "post_count",
            "avatar_url"
        ]

    def get_post_count(self, obj):
        return obj.posts.filter(status="published").count()

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.profile.avatar and request:
            return request.build_absolute_uri(obj.profile.avatar.url)
        return None
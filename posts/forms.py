from django import forms 
from .models import Post,Comment
 
 
class PostForm(forms.ModelForm): 
    """ 
    Form for creating and editing posts. 
    Does NOT include author (set in view) or created_at/updated_at (auto). 
    """ 
 
    class Meta: 
        model = Post 
        fields = ["content", "image", "status"] 
        widgets = { 
            "content": forms.Textarea(attrs={ 
                "class": "form-control", 
                "rows": 5, 
                "placeholder": "What's on your mind?", 
                "maxlength": 2000, 
            }), 
            "image": forms.FileInput(attrs={ 
                "class": "form-control", 
                "accept": "image/jpeg,image/png,image/gif,image/webp", 
            }), 
            "status": forms.Select(attrs={"class": "form-select"}), 
        } 
        labels = { 
            "content": "Post Content", 
            "image":   "Attach Image (optional)", 
            "status":  "Visibility", 
        } 
 
    def clean_content(self): 
        """Validate: content must not be empty or whitespace only.""" 
        content = self.cleaned_data.get("content", "").strip() 
        if not content: 
            raise forms.ValidationError("Post content cannot be empty.") 
        if len(content) < 3: 
            raise forms.ValidationError("Post must be at least 3 characters.") 
        return content 
 
    def clean_image(self): 
        """Validate: image must be under 5MB if provided.""" 
        image = self.cleaned_data.get("image") 
        if image: 
            max_size_mb = 5 
            if image.size > max_size_mb * 1024 * 1024:
                 raise forms.ValidationError( 
                    f"Image file too large. Maximum size is {max_size_mb}MB." 
                ) 
        return image 
    

 
class CommentForm(forms.ModelForm): 
    """ 
    Form for submitting a comment on a post. 
    Only the content field is shown – post and author are set in the view. 
    """ 
    class Meta: 
        model = Comment 
        fields = ["content"] 
        widgets = { 
            "content": forms.Textarea(attrs={ 
                "class": "form-control", 
                "rows": 3, 
                "placeholder": "Write a comment...", 
                "maxlength": 1000, 
            }), 
        } 
        labels = { 
            "content": "",   
        } 
 
    def clean_content(self): 
        """Validate: comment must have actual content, not just whitespace.""" 
        content = self.cleaned_data.get("content", "").strip() 
        if not content: 
            raise forms.ValidationError("Comment cannot be empty.") 
        if len(content) < 2: 
            raise forms.ValidationError("Comment is too short.") 
        return content
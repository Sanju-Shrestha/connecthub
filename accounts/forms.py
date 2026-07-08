 
from django import forms 
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User 
from .models import Profile 
 
 
class RegistrationForm(UserCreationForm): 
    """ 
    Custom registration form that extends Django's UserCreationForm. 
    Adds email, first_name, and last_name fields. 
    The password1/password2 fields (with matching validation) come 
    from UserCreationForm automatically. 
    """ 
    email = forms.EmailField( 
        required=True, 
        widget=forms.EmailInput(attrs={ 
            "class": "form-control", 
            "placeholder": "Enter your email address", 
        }), 
        help_text="Required. Enter a valid email address.", 
    ) 
    first_name = forms.CharField( 
        max_length=50, 
        required=True, 
        widget=forms.TextInput(attrs={ 
            "class": "form-control", 
            "placeholder": "First name", 
        }), 
    ) 
    last_name = forms.CharField( 
        max_length=50, 
        required=True,
         widget=forms.TextInput(attrs={ 
            "class": "form-control", 
            "placeholder": "Last name", 
        }), 
    ) 
 
    class Meta: 
        model = User 
        fields = [ 
            "username", 
            "first_name", 
            "last_name", 
            "email", 
            "password1", 
            "password2", 
        ] 
        widgets = { 
            "username": forms.TextInput(attrs={ 
                "class": "form-control", 
                "placeholder": "Choose a username", 
            }), 
        } 
 
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        # Add Bootstrap classes to the password fields from UserCreationForm 
        self.fields["password1"].widget.attrs.update({"class": "form-control"}) 
        self.fields["password2"].widget.attrs.update({"class": "form-control"}) 
 
    def clean_email(self): 
        """ 
        Custom validation: ensure no two users share the same email. 
        Django's User model does NOT enforce email uniqueness by default. 
        We add this check manually here. 
        """ 
        email = self.cleaned_data.get("email") 
        if User.objects.filter(email=email).exists(): 
            raise forms.ValidationError( 
                "An account with this email address already exists." 
            ) 
        return email 
 
    def save(self, commit=True): 
        """ 
        Override save to also store first_name, last_name, and email 
        on the User object. UserCreationForm.save() only saves 
        username and password by default. 
        """ 
        user = super().save(commit=False) 
        user.email = self.cleaned_data["email"] 
        user.first_name = self.cleaned_data["first_name"] 
        user.last_name = self.cleaned_data["last_name"] 
        if commit: 
            user.save() 
        return user 
 
 
class UserUpdateForm(forms.ModelForm): 
    """ 
    Form to update basic User information (email, first/last name). 
    Used alongside ProfileUpdateForm on the profile edit page. 
    """ 
    email = forms.EmailField( 
        required=True, 
        widget=forms.EmailInput(attrs={"class": "form-control"}), 
    )
    class Meta: 
        model = User 
        fields = ["first_name", "last_name", "email"] 
        widgets = { 
            "first_name": forms.TextInput(attrs={"class": "form-control"}), 
            "last_name":  forms.TextInput(attrs={"class": "form-control"}), 
        } 
 
 
class ProfileUpdateForm(forms.ModelForm): 
    """ 
    Form to update Profile model fields. 
    Used alongside UserUpdateForm on the profile edit page. 
    We use two separate forms on one page to update both 
    User and Profile at the same time. 
    """ 
    class Meta: 
        model = Profile 
        fields = ["bio", "avatar", "date_of_birth", "location", "website"] 
        widgets = { 
            "bio": forms.Textarea(attrs={ 
                "class": "form-control", 
                "rows": 3, 
                "placeholder": "Tell others about yourself...", 
            }), 
            "avatar": forms.FileInput(attrs={"class": "form-control"}), 
            "date_of_birth": forms.DateInput( 
                attrs={"class": "form-control", "type": "date"}, 
                format="%Y-%m-%d", 
            ), 
            "location": forms.TextInput(attrs={ 
                "class": "form-control", 
                "placeholder": "e.g. Kathmandu, Nepal", 
            }), 
            "website": forms.URLInput(attrs={ 
                "class": "form-control", 
                "placeholder": "https://your-website.com", 
            }), 
        } 
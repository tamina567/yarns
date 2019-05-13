from django import forms

from .models import Post, UserProfile

class PostForm(forms.ModelForm):
  class Meta:
    model = Post
    exclude = ['owner', 'date_posted']

class ProfileForm(forms.ModelForm):
  class Meta:
    model = UserProfile
    exclude = ['user', 'date_joined']

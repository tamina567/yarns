from django import forms

from django.contrib.auth.models import User, Group
from .models import Post, UserProfile

class PostForm(forms.ModelForm):
  class Meta:
    model = Post
    exclude = ['poster', 'date_posted', 'comments']

class ProfileForm(forms.ModelForm):
  class Meta:
    model = UserProfile
    exclude = ['user', 'date_joined']

class GroupCreationForm(forms.ModelForm):
  class Meta:
    model = Group
    fields = '__all__'

class AddUserToGroupForm(forms.Form):
  joining_user = forms.ModelChoiceField(queryset=User.objects.all())

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.template.response import TemplateResponse
from django.contrib.messages import error


import datetime

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile, Post
from .forms import PostForm, ProfileForm

class ProfileView(generic.DetailView):
  model = UserProfile;
  template_name = 'story/profile.html'

  error_message = "Profile not found."
  redirect_to = "story:update_profile"

  def get(self, request, *args, **kwargs):
    try:
        self.object = self.get_object()
    except Http404:
        error(request, self.error_message)
        return redirect(self.redirect_to)
    context = self.get_context_data(object=self.object)
    return self.render_to_response(context)

class PostView(generic.DetailView):
  model = Post;
  template_name = 'story/post.html'

  def get_context_data(self, **kwargs):
      context = super(PostView, self).get_context_data(**kwargs)
      user = self.object.owner
      context['profile'] = user.userprofile
      return context

class IndexView(generic.ListView):
  """
  The index page displays the 5 most recent posts.
  """
  template_name = 'story/index.html'
  context_object_name = 'latest_post_list'

  def get_queryset(self):
    return Post.objects.order_by('-date_posted')[:5]

@login_required
def upload_post(request):
  """
  The upload view allows users to upload Posts.
  """
  template_name = 'story/upload_form.html'
  redirect_to = 'story:index'

  if request.method == 'POST':
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
      form = form.save(commit=False)
      form.date_posted = datetime.datetime.now()
      form.owner =  request.user
      form.save()
      return redirect(redirect_to)
  else:
    form = PostForm()
  context = {'form': form}
  return render(request,  template_name, context)

def register(request):
  """
  Registers a new user.
  """
  template_name = 'registration/register.html'
  redirect_to = 'story:update_profile'

  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      form.save()
      username = form.cleaned_data['username']
      password = form.cleaned_data['password1']
      user = authenticate(username=username, password=password)
      login(request, user)
      return redirect(redirect_to)
  else:
    form = UserCreationForm()
  context = {'form' : form}
  return render(request, template_name, context)

@login_required
def update_profile(request):
  """
  Updates the UserProfile for the logged in user.
  """
  template_name = 'story/update_profile.html'
  redirect_to = 'story:index'

  if request.method == 'POST':
    p = UserProfile.objects.get(pk=request.user.id)
    form = ProfileForm(request.POST, instance=p)
    if form.is_valid():
      form = form.save(commit=False)

      # Update date_joined if the user profile is new.
      if p is None:
        form.date_joined = datetime.datetime.now()

      form.user = request.user
      form.save()
      return redirect(redirect_to)
  else:
    form = ProfileForm()
  context = {'form' : form}
  return render(request, template_name, context)

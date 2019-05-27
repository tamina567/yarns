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

from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile, Post
from .forms import PostForm, ProfileForm, GroupCreationForm, AddUserToGroupForm


@login_required
def view_profile(request, pk):
  """
  Displays the profile for the current user
  """
  template_name = 'story/profile.html'
  error_message = "Profile not found."
  redirect_to = "story:update_profile"

  try:
    user = User.objects.get(pk=pk)
    p = user.userprofile
    groups = user.groups.all()
  except AttributeError:
    p = None
    groups = None
    error(request, error_message)
    if(pk == request.user.id):
      return redirect(redirect_to)
  context = {'userprofile' : p, 'groups' : groups}
  return render(request, template_name, context)

class GroupProfileView(generic.DetailView):
  model = Group;
  template_name = 'story/group_profile.html'

  def get_context_data(self, **kwargs):
    context = super(GroupProfileView, self).get_context_data(**kwargs)
    users = self.object.user_set.all()
    context['users'] = users
    return context

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
    try:
      p = User.objects.get(pk=request.user.id).userprofile
      form = ProfileForm(request.POST, instance=p)
    except AttributeError:
      p = None
      form = ProfileForm(request.POST)

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

def register_group(request):
  """
  Creates a new group.
  """
  template_name = 'story/register_group.html'
  redirect_to = request.POST.get('next', '/')

  if request.method == 'POST':
    form = GroupCreationForm(request.POST)
    if form.is_valid():
      group = form.save()
      group.user_set.add(request.user)
      return redirect(redirect_to)
  else:
    form = GroupCreationForm()
  context = {'form' : form}
  return render(request, template_name, context)

def add_group_member(request, pk):
  """
  Adds a user to a group.
  """
  template_name = 'story/add_to_group.html'
  redirect_to = '/group/' + str(pk)
  group = Group.objects.get(pk=pk)

  if request.method == 'POST':
    form = AddUserToGroupForm(request.POST)
    if form.is_valid():
        user = form.cleaned_data['joining_user']
        group.user_set.add(user)
        return redirect(redirect_to)
  else:
    form = AddUserToGroupForm(initial={'user':request.user, 'group':group})
    context = {'form' : form, 'group' : group}
  return render(request, template_name, context)

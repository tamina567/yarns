from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.messages import error
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import UserProfile, Post
from .forms import PostForm, ProfileForm, GroupCreationForm, AddUserToGroupForm
from .access import ObjectPermissionsBackend

class IndexView(generic.ListView):
  """
  The index page displays the 5 most recent posts.
  """
  template_name = 'story/index.html'
  context_object_name = 'latest_post_list'

  def get_queryset(self):
    return Post.objects.order_by('-date_posted')[:5]

class PostView(generic.DetailView):
  """
  Displays a post if the requesting user has permission.

  Arguments:
  pk : the id of the post to be displayed

  Returns:
  context{
    post: the post to be displayed
  }
  """
  model = Post;
  template_name = 'story/post.html'
  error_message = {
    'unauthorised' : 'You are not authorised to view this post.'
  }

  def get_object(self, queryset=None):
    obj = super(PostView, self).get_object(queryset=queryset)
    if not self.request.user.has_perm('story.view_post', obj):
        error(self.request, self.error_message['unauthorised'])
        return None
    return obj

@login_required
def edit_post(request, pk=None):
  """
  The upload view allows users to upload Posts.

  For a non-POST request, the PostForm is returned for a user to fill
  information. For a POST request, the Post is saved.
  Post owner is the current logged in user,
  Date posted is the current timestamp.
  """

  error_message = "Access not authorised."
  redirect_to = 'story:index'

  if pk:
    post = Post.objects.get(pk=pk)
    template_name = 'story/edit_post.html'

    if not request.user.has_perm('story.change_post', post):
      error(request, error_message)
      return redirect(redirect_to)

  else:
    post = None
    template_name = 'story/upload_form.html'

  if request.method == 'POST':
    if post:
      form = PostForm(request.POST, request.FILES, instance=post)
    else:
      form = PostForm(request.POST, request.FILES)

    if form.is_valid():
      form = form.save(commit=False)
      if not post:
        form.date_posted = timezone.now()
        form.poster =  request.user
      form.save()
      return redirect(redirect_to)
  else:
    form = PostForm(instance=post)
  context = {'form': form, 'post':post}
  return render(request,  template_name, context)

def register(request):
  """
  A new user is registered and logged in.
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
def view_profile(request, pk):
  """
  Displays the profile and groups for the given user.

  Arguments:
  pk : the id of the user to be displayed

  Returns:
  context{
    userprofile: the profile for the user,
    groups: the groups that the user belongs to
  }
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

@login_required
def update_profile(request):
  """
  Updates the UserProfile for the logged in user.
  A new UserProfile is created for a user if one does not exist already.
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
        form.date_joined = timezone.now()

      form.user = request.user
      form.save()
      return redirect(redirect_to)
  else:
    form = ProfileForm()
  context = {'form' : form}
  return render(request, template_name, context)

class GroupProfileView(generic.DetailView):
  """
  Displays the profile for the given group and the users that belong to the
  group.

  Arguments:
  pk : the id of the group to be displayed

  Returns:
  context{
    group: the group to be displayed,
    users: the users that belong to the group
  }
  """
  model = Group;
  template_name = 'story/group_profile.html'

  def get_context_data(self, **kwargs):
    context = super(GroupProfileView, self).get_context_data(**kwargs)
    users = self.object.user_set.all()
    context['users'] = users
    return context

@login_required
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

@login_required
def add_group_member(request, pk):
  """
  Adds a user to a group.

  Arguments:
  pk: The id of the group to add the user to.

  Form contains the joining User.
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

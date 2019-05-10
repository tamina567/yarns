from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import User, Post
from .forms import PostForm

class PostView(generic.DetailView):
  model = Post;
  template_name = 'story/post.html'

class IndexView(generic.ListView):
  """
  The index page displays the 5 most recent posts.
  """
  template_name = 'story/index.html'
  context_object_name = 'latest_post_list'

  def get_queryset(self):
    return Post.objects.order_by('-date_posted')[:5]

def upload_post(request):
  """
  The upload view allows users to upload Posts.
  """
  if request.method == 'POST':
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('story:index'))
  else:
    form = PostForm()
    return render(request, 'story/upload_form.html', {'form': form})

def register(request):
  """
  Registers a new user.
  """
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      form.save()
      username = form.cleaned_data['username']
      password = form.cleaned_data['password1']
      user = authenticate(username=username, password=password)
      login(request, user)
      return HttpResponseRedirect(reverse('story:index'))
  else:
    form = UserCreationForm()
    context = {'form' : form}
    return render(request, 'registration/register.html', context)

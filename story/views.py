from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage

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
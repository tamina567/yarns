from django.core.files import File
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse

import datetime
import mock

from django.contrib.auth.models import User, Group
from .models import UserProfile, Post

def login(client, user):
  client.force_login(user)

def logout(client):
  client.logout()

class EditPostViewTest(TestCase):
  """
  Edit post view handles the uploading and the editing of post.
  Users are required to be logged in to access this view.

  Any logged in user can upload a post.
  Only users that belong in the 'knower' group of a post can edit the post.
  """
  def setUp(self):
    self.upload_url = reverse('story:upload_post')
    self.group1 = Group.objects.create(name='group1')
    self.group2 = Group.objects.create(name='group2')
    self.user = User.objects.create(username='user')
    self.group1.user_set.add(self.user)
    login(self.client, self.user)

  def upload_post(self, description, knower):
    form = {
      'description' : description,
      'knower' : knower.id,
      'viewed_by' : 'all',
    }
    return self.client.post(self.upload_url, form)

  def edit_post(self, pk, description, knower):
    url = reverse('story:edit_post', kwargs={'pk':pk})
    form = {
      'description' : description,
      'knower' : knower.id,
      'viewed_by' : 'all',
    }
    return self.client.post(url, form)

  def test_post_view_get(self):
    """
    PostForm is returned for a GET.
    """
    response = self.client.get(self.upload_url)
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.context['form'])

  def test_post_view_post(self):
    """
    Post is added when form is returned.
    """
    with self.assertRaises(Post.DoesNotExist):
      post = Post.objects.get(knower = self.group1.id)

    form = {
      'description' : "Test.",
      'knower' : self.group1.id,
      'viewed_by' : 'all',
    }
    response = self.client.post(
                    self.upload_url,
                    form)

    self.assertEqual(response.status_code, 302) # Redirect message
    self.assertEqual(response.url, "/")
    post = Post.objects.get(knower = self.group1.id)
    self.assertIsNotNone(post)

  def test_login_required(self):
    """
    Redirected to login view if no user is logged in.
    """
    logout(self.client)
    response = self.client.get(self.upload_url)
    self.assertEqual(response.status_code, 302) # Redirect message
    self.assertEqual(response.url, "/accounts/login/?next=/upload_post/")
    login(self.client, self.user)

  def test_edit_post_authorised(self):
    # User is a member of group1
    # User is authorised to edit the post
    knower = self.group1

    with self.assertRaises(Post.DoesNotExist):
      post = Post.objects.get(pk=1)

    description = "Test1"
    self.upload_post(description, knower)
    post = Post.objects.get(pk=1)
    self.assertEqual(post.description, description)

    description = "Test2"
    self.edit_post(1, description, knower)
    post = Post.objects.get(pk=1)
    self.assertEqual(post.description, description)

  def test_edit_post_unauthorised(self):
    # User is a NOT member of group1
    # User is NOT authorised to edit the post
    knower = self.group2

    with self.assertRaises(Post.DoesNotExist):
      post = Post.objects.get(pk=1)

    description = "Test1"
    self.upload_post(description, knower)
    post = Post.objects.get(pk=1)
    self.assertEqual(post.description, description)

    description = "Test2"
    response = self.edit_post(1, description, knower)
    post = Post.objects.get(pk=1)
    self.assertNotEqual(post.description, description)
    # TODO an ERROR should be raised here too.

class IndexViewTest(TestCase):
  """
  At the index page, the user can see a list of posts.
  The user should have view permission to see each post.
  """

  def setUp(self):
    self.user = User.objects.create(username='user')
    login(self.client, self.user)

  # TODO implement Index View properly
  def test_logged_in(self):
    return True

  def test_logged_out(self):
    return True

class PostViewTest(TestCase):
  """
  The user can view a post.
  Only users in the 'viewers' of a post can access this view.
  """
  def setUp(self):
    self.user = User.objects.create(username='user')
    login(self.client, self.user)

  def test_post_view(self):
    return True

  # TODO implement Index View properly
  def test_logged_in(self):
    return True

  def test_logged_out(self):
    return True

  def test_non_viewer(self):
    return True

class RegisterViewTest(TestCase):
  """
  Any person can register.
  After registration, the user should be logged in and be directed to create a
  profile.
  """
  def setUp(self):
    self.url = reverse('story:register')
    self.success_url = reverse('story:update_profile')

  def register_user(self, name):
    password = "GoodPassword123"
    form = {
      'username' : name,
      'password1' : password,
      'password2' : password
    }
    return self.client.post(self.url, form)

  def test_register_user(self):
    name = "test_register_user"
    response = self.register_user(name)
    self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
    self.assertEqual(response.url, self.success_url)

    user = User.objects.get(username=name)
    # The user should be logged in for the next request
    response = self.client.get('/')
    self.assertEqual(response.context['user'], user)

  def test_get_form(self):
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, HttpResponse.status_code)
    self.assertIsNotNone(response.context['form'])

class ProfileViewTest(TestCase):
  def setUp(self):
    self.url = reverse('story:profile', kwargs={'pk' : 1})
    self.user = User.objects.create(username='user')
    self.user.userprofile = UserProfile.objects.create(
        name = 'Name',
        user = self.user,
        dob = timezone.now(),
        date_joined = timezone.now(),
    )
    login(self.client, self.user)

  def test_login_required(self):
    """
    User is required to log in to access this view.
    """
    logout(self.client)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
    self.assertEqual(response.url, reverse('login') + '?next='+ self.url)
    login(self.client, self.user)

  def test_get_profile(self):
    """
    User is required to log in to access this view.
    """
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, HttpResponse.status_code)
    self.assertEqual(response.context['userprofile'], self.user.userprofile)

class UpdateProfileViewTest(TestCase):
  """
  Update profile allows the user to update their own profile.
  The user must be logged in to access this view.
  """
  def setUp(self):
    self.url = reverse('story:update_profile')
    self.success_url = reverse('story:index')
    self.user = User.objects.create(username='user')
    login(self.client, self.user)

  def update_profile(self, name):
    form = {
      # TODO it actually doesn't make sense to have the user in the form???
      # remove
      'user' : self.user,
      'name' : name,
      'dob' : "06/01/93",
    }
    return self.client.post(self.url, form)

  def test_login_required(self):
    logout(self.client)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
    self.assertEqual(response.url, reverse('login') + '?next='+ self.url)
    login(self.client, self.user)

  def test_get_form(self):
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, HttpResponse.status_code)
    self.assertIsNotNone(response.context['form'])

  def test_create_profile(self):
    """
    Creates a new user profile for the user.
    """
    with self.assertRaises(UserProfile.DoesNotExist):
      profile = UserProfile.objects.get(user=self.user.id)

    name = "Name"
    response = self.update_profile(name)
    self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
    # TODO change the success url
    self.assertEqual(response.url, self.success_url)

    profile = UserProfile.objects.get(user=self.user.id)
    self.assertIsNotNone(profile)
    self.assertEqual(profile.name, name)

  def test_edit_profile(self):
    with self.assertRaises(UserProfile.DoesNotExist):
      profile = UserProfile.objects.get(user=self.user.id)

    name = "Name"
    response = self.update_profile(name)
    self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
    self.assertEqual(response.url, self.success_url)

    profile = UserProfile.objects.get(user=self.user.id)
    self.assertIsNotNone(profile)
    self.assertEqual(profile.name, name)

    name = "NewName"
    response = self.update_profile(name)
    self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
    self.assertEqual(response.url, self.success_url)

    profile = UserProfile.objects.get(user=self.user.id)
    self.assertIsNotNone(profile)
    self.assertEqual(profile.name, name)

# class GroupProfileView(generic.DetailView):
#   """
#   Displays the profile for the given group and the users that belong to the
#   group.
#
#   Arguments:
#   pk : the id of the group to be displayed
#
#   Returns:
#   context{
#     group: the group to be displayed,
#     users: the users that belong to the group
#   }
#   """
#   model = Group;
#   template_name = 'story/group_profile.html'
#
#   def get_context_data(self, **kwargs):
#     context = super(GroupProfileView, self).get_context_data(**kwargs)
#     users = self.object.user_set.all()
#     context['users'] = users
#     return context
#
# @login_required
# def register_group(request):
#   """
#   Creates a new group.
#   """
#   template_name = 'story/register_group.html'
#   redirect_to = request.POST.get('next', '/')
#
#   if request.method == 'POST':
#     form = GroupCreationForm(request.POST)
#     if form.is_valid():
#       group = form.save()
#       group.user_set.add(request.user)
#       return redirect(redirect_to)
#   else:
#     form = GroupCreationForm()
#   context = {'form' : form}
#   return render(request, template_name, context)
#
# @login_required
# def add_group_member(request, pk):
#   """
#   Adds a user to a group.
#
#   Arguments:
#   pk: The id of the group to add the user to.
#
#   Form contains the joining User.
#   """
#   template_name = 'story/add_to_group.html'
#   redirect_to = '/group/' + str(pk)
#   group = Group.objects.get(pk=pk)
#
#   if request.method == 'POST':
#     form = AddUserToGroupForm(request.POST)
#     if form.is_valid():
#         user = form.cleaned_data['joining_user']
#         group.user_set.add(user)
#         return redirect(redirect_to)
#   else:
#     form = AddUserToGroupForm(initial={'user':request.user, 'group':group})
#     context = {'form' : form, 'group' : group}
#   return render(request, template_name, context)

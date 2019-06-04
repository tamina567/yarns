from django.core.files import File
from django.db.utils import IntegrityError
from django.test import TestCase, Client
from django.utils import timezone

from django.contrib.auth.models import User, Group
from .models import Post
from .access import ObjectPermissionsBackend

class PermissionsTests(TestCase):
  def setUp(self):
    self.backend = ObjectPermissionsBackend()

    user1 = User.objects.create(username='user1')
    user2 = User.objects.create(username='user2')

    group1 = Group.objects.create(name='group1')
    group1.user_set.add(user1)

    group2 = Group.objects.create(name='group2')
    group2.user_set.add(user2)

    group3 = Group.objects.create(name='group3')
    group3.user_set.add(user1)
    group3.user_set.add(user2)

  def test_has_view_perm_some(self):
    group1 = Group.objects.get(name='group1')
    p = Post.objects.create(
      date_posted = timezone.now(),
      knower = group1,
      viewed_by = 'some',
    )
    p.viewers.add(group1)

    # User 1 should have access as a member of group 1
    user1 = User.objects.get(username='user1')
    self.assertTrue(
      self.backend.has_perm(user1, 'story.view_post', p)
    )

    # User 2 should NOT have access
    user2 = User.objects.get(username='user2')
    self.assertFalse(
      self.backend.has_perm(user2, 'story.view_post', p)
    )

    # User 2 will have permission if group3 is added to viewers.
    group3 = Group.objects.get(name='group3')
    p.viewers.add(group3)
    self.assertTrue(
      self.backend.has_perm(user2, 'story.view_post', p)
    )

  def test_has_view_perm_all(self):
    group1 = Group.objects.get(name='group1')
    p = Post.objects.create(
      date_posted = timezone.now(),
      knower = group1,
      viewed_by = 'all',
    )
    user1 = User.objects.get(username='user1')
    self.assertTrue(
      self.backend.has_perm(user1, 'story.view_post', p)
    )
    user2 = User.objects.get(username='user2')
    self.assertTrue(
      self.backend.has_perm(user2, 'story.view_post', p)
    )

  def test_has_change_perm_all(self):
    group1 = Group.objects.get(name='group1')
    p = Post.objects.create(
      date_posted = timezone.now(),
      knower = group1,
      viewed_by = 'all',
    )
    user1 = User.objects.get(username='user1')
    self.assertTrue(
      self.backend.has_perm(user1, 'story.change_post', p)
    )


    user2 = User.objects.get(username='user2')
    self.assertFalse(
      self.backend.has_perm(user2, 'story.change_post', p)
    )

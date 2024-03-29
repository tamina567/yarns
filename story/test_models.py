from django.core.files import File
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse

import datetime
import mock
import requests

from django.contrib.auth.models import User, Group
from .models import UserProfile, Post, Comment

class UserProfileModelTests(TestCase):
  def setUp(self):
    user = User.objects.create(username='test')

  def test_attributes(self):
    """
    UserProfile should contain attributes as expected.
    """
    user = User.objects.get(username='test')
    p = UserProfile.objects.create(
    user = user,
    name = "name",
    dob = timezone.now(),
    gender = "Woman",
    date_joined = timezone.now(),
    )

    self.assertEqual(p.user, user)
    self.assertEqual(user.userprofile, p)

    self.assertEqual(p.name, "name")
    self.assertEqual(p.gender, "Woman")

  def test_required_attributes(self):
    """
    UserProfile creation should fail without required attributes.
    """
    user = User.objects.get(username='test')
    p1 = UserProfile.objects.create(
      user = user,
      name = "name",
      dob = timezone.now(),
      date_joined = timezone.now(),
      # Optional field 'gender' is not included
      # No exception should be raised.
    )

    with self.assertRaises(IntegrityError):
      p2 = UserProfile.objects.create(
        name = "name"
      )

class PostModelTests(TestCase):
  def setUp(self):
    user1 = User.objects.create(username='user1')
    group1 = Group.objects.create(name='group1')

  def test_attributes(self):
    """
    Post should contain attributes as expected.
    """
    poster = User.objects.get(username='user1')
    knower = Group.objects.get(name='group1')
    file_mock = mock.MagicMock(spec=File)
    file_mock.name = 'file'
    p = Post.objects.create(
      date_posted = timezone.now(),
      description = "Test.",
      file = file_mock,
      poster = poster,
      knower = knower,
      viewed_by = 'all',
    )

    self.assertEqual(p.description, "Test.")
    self.assertIsNotNone(p.file)
    self.assertEqual(p.poster, poster)
    self.assertEqual(p.knower, knower)
    self.assertEqual(p.viewed_by, 'all')

  def test_required_attributes(self):
    knower = Group.objects.get(name='group1')
    p = Post.objects.create(
      # Omit all optional fields, test should still pass
      date_posted = timezone.now(),
      knower = knower,
      viewed_by = 'all',
    )

  def test_requires_date(self):
    knower = Group.objects.get(name='group1')
    with self.assertRaises(IntegrityError):
      p = Post.objects.create(
        # Omit date posted
        knower = knower,
        viewed_by = 'all',
      )

  def test_requires_knower(self):
    with self.assertRaises(IntegrityError):
      p = Post.objects.create(
        date_posted = timezone.now(),
        # Omit knower
        viewed_by = 'all',
      )

  def test_default_viewed_by(self):
    knower = Group.objects.get(name='group1')
    p = Post.objects.create(
      date_posted = timezone.now(),
      knower = knower,
      # Omit viewed_by
    )
    self.assertEqual(p.viewed_by, 'all')

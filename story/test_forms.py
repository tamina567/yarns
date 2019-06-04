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
from .forms import PostForm

class PostFormTest(TestCase):
  def setUp(self):
    self.user1 = User.objects.create(username='user')
    self.group1 = Group.objects.create(name='group')

  def test_post_form(self):
    """
    A Form is valid if the excluded fields are not included.
    """
    file_mock = mock.MagicMock(spec=File)
    data = {
      'description' : "Test.",
      'file' : file_mock,
      'knower' : self.group1.id,
      'viewed_by' : 'all',
    }
    form = PostForm(data=data)
    self.assertTrue(form.is_valid())

  def test_post_form_some_knowers(self):
    """
    A Form is valid if the excluded fields are not included.
    """
    file_mock = mock.MagicMock(spec=File)
    data = {
      'description' : "Test.",
      'file' : file_mock,
      'knower' : self.group1.id,
      'viewed_by' : 'some',
      'viewers' : [self.group1.id]
    }
    form = PostForm(data=data)
    self.assertTrue(form.is_valid())

from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils import timezone

import datetime

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

from django.db import models
from django.contrib.auth.models import User

MAX_NAME_LENGTH=300

class UserProfile(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=MAX_NAME_LENGTH)
  dob = models.DateTimeField('date of birth')
  gender = models.CharField(max_length=MAX_NAME_LENGTH, blank=True)
  def __str__(self):
    return self.name

class Post(models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE)
  date_posted = models.DateTimeField('date posted')
  description = models.TextField(blank=True)
  file = models.FileField(upload_to='uploads/', blank=True)
  # TODO Upload files elsewhere

  def __str__(self):
    return self.description

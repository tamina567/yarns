from django.db import models
from django.contrib.auth.models import User

MAX_NAME_LENGTH=300

class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=MAX_NAME_LENGTH)
  dob = models.DateTimeField('date of birth')
  gender = models.CharField(max_length=MAX_NAME_LENGTH, blank=True)
  date_joined = models.DateTimeField('date_joined', blank=True)

  def __str__(self):
    return "Name: " + self.name + ", DOB: " + str(self.dob)

class Post(models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE)
  date_posted = models.DateTimeField('date posted')
  description = models.TextField(blank=True)
  file = models.FileField(upload_to='uploads/', blank=True)
  # TODO Upload files elsewhere

  def __str__(self):
    return "Post by " + str(self.owner) \
            + ", on " + str(self.date_posted) \
            + ". Description: " + self.description

from django.db import models
from django.contrib.auth.models import User, Group

MAX_NAME_LENGTH=300

class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=MAX_NAME_LENGTH)
  dob = models.DateTimeField('date of birth')
  gender = models.CharField(max_length=MAX_NAME_LENGTH, blank=True)
  date_joined = models.DateTimeField('date_joined', blank=True)

  def __str__(self):
    return self.name

class Comment(models.Model):
  text = models.TextField(blank=True)
  date_posted = models.DateTimeField('date posted')
  poster = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return "Comment by " + str(self.poster) \
          + ", on " + str(self.date_posted) \
          + ". Text: " + self.text

class Post(models.Model):
  date_posted = models.DateTimeField('date posted')
  description = models.TextField(blank=True)
  file = models.FileField(upload_to='uploads/', blank=True)

  poster = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    blank=True,
    null=True
  )
  knower = models.ForeignKey(
    Group,
    on_delete=models.CASCADE,
    related_name = 'knows'
  )

  view_types = [
    ('all', 'all'),
    ('some', 'some')
  ]
  viewed_by = models.CharField(
    max_length = 4,
    choices = view_types,
    default = 'A',
  )

  viewers = models.ManyToManyField(
    Group,
    blank=True,
    related_name = 'views'
  )

  comments = models.ManyToManyField(Comment)

  def __str__(self):
    return "Post by " + str(self.poster) \
            + ", on " + str(self.date_posted) \
            + ". Description: " + self.description

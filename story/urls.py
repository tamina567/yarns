from django.urls import path

from . import views

app_name='story'
urlpatterns = [
  path('', views.IndexView.as_view(), name='index'),
  path('post/<int:pk>', views.PostView.as_view(), name='post'),
  path('upload_post/', views.edit_post, name='upload_post'),
  path('edit_post/<int:pk>', views.edit_post, name='edit_post'),
  path('register', views.register, name='register'),
  path('profile/<int:pk>', views.view_profile, name="profile"),
  path('update_profile', views.update_profile, name='update_profile'),
  path('register_group', views.register_group, name='register_group'),
  path('group/<int:pk>', views.GroupProfileView.as_view(), name='group_profile'),
  path('add_to_group/<int:pk>', views.add_group_member, name='add_to_group'),
]

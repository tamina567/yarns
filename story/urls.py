from django.urls import path

from . import views

app_name='story'
urlpatterns = [
  path('', views.IndexView.as_view(), name='index'),
  path('post/<int:pk>/', views.PostView.as_view(), name='post'),
  path('upload/', views.upload_post, name='upload_post'),
  path('register/', views.register, name='register'),
]

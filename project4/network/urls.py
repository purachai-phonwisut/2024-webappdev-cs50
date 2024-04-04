
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following" , views.following, name="following"),
    path("profile/<int:userID>", views.profile, name="profile"),
    path("post/<int:postID>", views.post, name="post"),
    path("post/<int:postID>/edit", views.edit, name="edit"),
    path("new", views.new, name="new"),
]

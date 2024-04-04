from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'posts')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering = ['-timestamp']

    
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='likes')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="liked_posts")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post','user')

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="following_user")
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE,related_name="follower_user")

    def __str__(self):
        return f"{self.user} is following {self.user_follower}"
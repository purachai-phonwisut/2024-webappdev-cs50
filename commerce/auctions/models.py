from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    cname = models.CharField(max_length = 96)

    def __str__(self):
        return self.cname

class Listing(models.Model):
    title = models.CharField(max_length=96)
    desc = models.CharField(max_length=256)
    category = models.ForeignKey(Category, on_delete = models.CASCADE, blank = True, null = True )
    price = models.FloatField()
    imageURL = models.CharField(max_length = 999, default=None, blank=True)
    seller = models.ForeignKey(User, blank=True,null = True, related_name="user", on_delete = models.CASCADE)
    created_time = models.DateTimeField(auto_now_add = True)
    isactive = models.BooleanField(default = True)

    def __str__(self):
        return self.title

# class Bid(models.Model):
#     bidder = models.CharField(max_length=96)
#     title = models.CharField(max_length=96)
#     listing_id = models.IntegerField()
#     bid = models.FloatField()

# class Comment(models.Model):
#     user = models.CharField(max_length=96)
#     comment = models.CharField(max_length=256)
#     listing_id = models.IntegerField()
#     datetime = models.DateTimeField(auto_now_add = True)

class Watchlist:
    user = models.ForeignKey(User, blank=True,null = True, related_name="user", on_delete = models.CASCADE)
    listing_id = models.IntegerField()
    iswatchlist = models.BooleanField(default = False)
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass
class Category(models.Model):
    cname = models.CharField(max_length=96)

    def __str__(self):
        return self.cname

class Listing(models.Model):
    title = models.CharField(max_length=96)
    desc = models.CharField(max_length=256)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    startbid = models.FloatField()
    currentbid = models.ForeignKey('Bid', blank=True, null = True, on_delete=models.SET_NULL)
    imageURL = models.CharField(max_length=999, blank=True, default="")
    seller = models.ForeignKey(User, blank=True, null=True, related_name="listings", on_delete=models.CASCADE)
    isactive = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.IntegerField()

    def __str__(self):
        return f"{self.bidder.username} - {self.bid}"

class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ownercomment",blank=True, null= True)
    comment = models.CharField(max_length=999)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name = "listingcomment",blank=True, null= True)

    def __str__(self):
        return f"{self.owner} commented on {self.listing}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"
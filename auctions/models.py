from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Categories(models.Model):
    category = models.CharField(max_length=69)

    def __str__(self):
        return f"{self.category}"
    
class Bid(models.Model):
    amount = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")

    def __str__(self):
        return f"{self.amount}"

class Items(models.Model):
    name = models.CharField(max_length=69)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    description = models.CharField(max_length=420)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bid_amount")
    url = models.CharField(max_length=420)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="classification")
    listed = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="watcher")

    def __str__(self):
        return f"{self.name}"

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    item = models.ForeignKey(Items, on_delete=models.CASCADE, related_name="item")
    comment = models.CharField(max_length=420)

    def __str__(self):
        return f"{self.user}'s comment"


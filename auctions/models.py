from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    name = models.CharField(max_length=64)
    init_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    final_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    descr = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, models.SET_NULL, blank=True, null=True, related_name="listings")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField(default=True)
    img = models.URLField(blank=True, null=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases", blank=True, null=True)

    @classmethod
    def create(cls, name, init_price, descr, category, seller, img):
        newListing = cls(name=name, init_price=init_price, descr=descr, category=category, seller=seller, img=img)
        return newListing

    def getCurrentBid(self):
        currentBid = self.init_price
        if self.bids.all():
            for bid in self.bids.all():
                if bid.amount > currentBid:
                    currentBid = bid.amount
        return currentBid

    def getCurrentBidder(self):
        bidder = ""
        if self.bids.all():
            for bid in self.bids.all():
                if bid.amount > self.init_price:
                    bidder = bid.bidder.username
        return bidder

    def __str__(self):
        return f"{self.name}: by {self.seller}"

class Comment(models.Model):
    comment = models.CharField(max_length=1000)
    date_time = models.DateTimeField(auto_now_add=True)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    @classmethod
    def create(cls, comment, commenter, listing):
        newComment = cls(comment=comment, commenter=commenter, listing=listing)
        return newComment

    def __str__(self):
        return f"{self.commenter}: {self.comment}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    @classmethod
    def create(cls, bidder, amount, listing):
        bid = cls(bidder=bidder, amount=amount, listing=listing)
        return bid

    def __str__(self):
        return f"{self.amount} by {self.bidder.username}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    listings = models.ManyToManyField(Listing, blank=True, related_name="watchers")

    @classmethod
    def create(cls, user):
        watchlist = cls(user=user)
        return watchlist

    def __str__(self):
        return f"Watchlist of {self.user}"

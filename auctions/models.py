from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Auction(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction")
    title = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    image = models.URLField()
    content = models.TextField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Auction number {self.id} : {self.title} published on {self.date} by {self.author}. Starting price : ${self.starting_price} - Category : {self.category}"

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bid")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Bid for auction number {self.auction.id} - {self.auction.title} of ${self.amount} made by {self.author} on {self.date}"

class Comment(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comment")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        return f"{self.author} commented on {self.auction.title} : {self.content}"

class Watchlist(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ManyToManyField(Auction, blank=True)

    def __str__(self):
        return f"Watchlist of user {self.owner}"
from django.contrib import admin
from .models import User, Category, Auction, Bid, Comment, Watchlist

class WatchlistAdmin(admin.ModelAdmin):
    filter_horizontal = ("product",)



admin.site.site_header = "Auction Admin"
admin.site.site_title = "Auction Admin Area"
admin.site.index_title = "Welcome to the Auction Admin Area"
  
  
# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist, WatchlistAdmin)
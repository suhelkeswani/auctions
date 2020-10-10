from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Listing, Comment, Bid, Watchlist

class ListingAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "seller", "init_price", "active", "winner", "final_price")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("commenter", "comment", "date_time")

class BidAdmin(admin.ModelAdmin):
    list_display = ("listing", "amount", "bidder")

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Watchlist)

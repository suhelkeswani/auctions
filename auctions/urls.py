from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category"),
    path("create_listing", views.createListing, name="create_listing"),
    path("close_listing/<int:listing_id>/<str:name>", views.closeListing, name="close_listing"),
    path("submit_bid/<int:listing_id>/<str:name>", views.submitBid, name="submit_bid"),
    path("add_to_watchlist/<int:listing_id>/<str:name>", views.addToWatchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<int:listing_id>/<str:name>", views.removeFromWatchlist, name="remove_from_watchlist"),
    path("<int:listing_id>/<str:listing>", views.listing, name="listing")
]

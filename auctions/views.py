from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.urls import reverse
from .models import Listing
from .models import User, Watchlist, Comment, Category, Bid
from decimal import Decimal

class commentForm(forms.Form):
    comment = forms.CharField(label="", widget=forms.Textarea(attrs={'rows':'5', 'style': 'width: 100%'}), max_length=1000)

class listingForm(forms.Form):
    name = forms.CharField(label="", widget=forms.TextInput(attrs={'size': '50', 'placeholder': 'Listing Name'}))
    init_price = forms.FloatField(label="", max_value=999999999999, min_value=0.01, widget=forms.NumberInput(attrs={'placeholder': 'Starting Bid'}))
    descr = forms.CharField(label="", widget=forms.Textarea(attrs={'rows':'5', 'style': 'width: 100%', 'placeholder': 'Description'}), max_length=1000)

    def CategoriesAsTuple():
        return [(Category.objects.all()[i], Category.objects.all()[i]) for i in range(0, len(Category.objects.all()))]

    category = forms.TypedChoiceField(choices = CategoriesAsTuple())
    img = forms.URLField(required=False, label="", widget=forms.URLInput(attrs={'style': 'width: 80%', 'placeholder': 'Image URL'}))

#This form is only used to copy data onto as a template and validate. An html form is used for this because it allows for dynamicly chaning the minimum.
class bidForm(forms.Form):
    bid = forms.DecimalField(max_value=999999999999, min_value=0.01)

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.exclude(active=False).all()
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

def category(request, category):
    return render(request, "auctions/category.html", {
        "category": Category.objects.get(name=category),
        "activeCategoryListing": Category.objects.get(name=category).listings.exclude(active=False)
    })

@login_required
def createListing(request):
    if request.method == "POST":
        newListing = listingForm(request.POST)

        if newListing.is_valid():
            name = newListing.cleaned_data["name"]
            init_price = newListing.cleaned_data["init_price"]
            descr = newListing.cleaned_data["descr"]
            category = newListing.cleaned_data["category"]
            img = newListing.cleaned_data["img"]
            seller = request.user

            saveListing = Listing.create(name=name, init_price=init_price, descr=descr, category=Category.objects.get(name=category), seller=seller, img=img)
            saveListing.save()

        else:
            return HttpResponse("Error: You have incorrectly entered some information. Go back and correct your form before resubmitting.")

        return HttpResponseRedirect(reverse(listing, args=(saveListing.id, saveListing.name,)))

    return render(request, "auctions/createListing.html", {
        "form": listingForm
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()

            # create a new watchlist for the user
            watchlist = Watchlist.create(user)
            watchlist.save()

        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def listing(request, listing_id, listing):
    if request.method == "POST":
        newComment = commentForm(request.POST)
        if newComment.is_valid():
            commentTxt = newComment.cleaned_data["comment"]

            saveComment = Comment.create(commentTxt, request.user, Listing.objects.get(id=listing_id))
            saveComment.save()

            return HttpResponseRedirect(reverse("listing", args=(listing_id, listing,)))

    isOnWL = False
    if request.user.is_authenticated:
        for item in Watchlist.objects.get(user=request.user).listings.all():
            if item.name == listing:
                isOnWL = True

    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.get(id=listing_id),
        "isOnWL": isOnWL,
        "commentForm": commentForm,
        "minBid": round((float(Listing.objects.get(id=listing_id).getCurrentBid()) + 0.01), 2)
    })

@login_required
def addToWatchlist(request, listing_id, name):
    if request.method == "POST":
        userWatchlist = Watchlist.objects.get(user = request.user)
        userWatchlist.listings.add(listing_id)
        return HttpResponseRedirect(reverse("listing", args=(listing_id, name,)))

@login_required
def removeFromWatchlist(request, listing_id, name):
    if request.method == "POST":
        userWatchlist = Watchlist.objects.get(user = request.user)
        userWatchlist.listings.remove(listing_id)
        return HttpResponseRedirect(reverse("listing", args=(listing_id, name,)))

@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlist": Watchlist.objects.get(user=request.user).listings.all()
    })

@login_required
def closeListing(request, listing_id, name):
    if request.method == "POST":
        if (request.user == Listing.objects.get(pk=listing_id).seller):
            closeListing = Listing.objects.get(id = listing_id)
            closeListing.active = False
            if (closeListing.getCurrentBidder()):
                closeListing.winner = User.objects.get(username=closeListing.getCurrentBidder())
                closeListing.final_price = closeListing.getCurrentBid()
            closeListing.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id, name,)))
    else:
        return HttpResponse("Error: POST to try and close a listing without authentication.")

@login_required
def submitBid(request, listing_id, name):
    if request.method == "POST":
        newBid = bidForm(request.POST)
        print(newBid)
        if newBid.is_valid():
            bid = newBid.cleaned_data["bid"]
            #if bid >= (float(Listing.objects.get(id=listing_id).getCurrentBid()) + 0.01):
            saveBid = Bid.create(request.user, bid, Listing.objects.get(id=listing_id))
            saveBid.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id, name,)))
            #else:
                #return HttpResponse("Error: You have incorrectly entered a Bid.")
        else:
            return HttpResponse("Error: You have incorrectly entered a Bid.")

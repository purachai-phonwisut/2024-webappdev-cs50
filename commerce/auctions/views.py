from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import *


def index(request):
    open =Listing.objects.all().filter(isactive=True)
    return render(request, "auctions/index.html",{
        "open" : open
    })

def closed(request):
    close = Listing.objects.all().filter(isactive=False)
    return render(request, "auctions/closed.html",{
        "close" : close
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
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def activelisting(request):
    products = Listing.objects.all()

def category(request, category_id=None):
    categories = Category.objects.all()
    if category_id:
        listings = Listing.objects.filter(category_id=category_id, isactive=True)
        selected_category = get_object_or_404(Category, pk=category_id)
    else:
        listings = Listing.objects.filter(isactive=True)
        selected_category = None
    
    return render(request, "auctions/category.html", {
        "categories": categories,
        "listings": listings,
        "selected_category": selected_category,
    })

@login_required
def newlisting(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        return render(request, "auctions/newlisting.html", {
            "categories": categories
        })
    else:
        title = request.POST["title"]
        desc = request.POST["desc"]
        startbid = float(request.POST["startbid"])
        imageURL = request.POST["imageURL"]
        category = request.POST["category"]
        now_user = request.user

        catedata = Category.objects.get(cname=category)
        newlist = Listing(
            title = title,
            desc = desc,
            startbid = startbid,
            imageURL = imageURL,
            category = catedata,
            seller = now_user
        )

        newlist.save()
        return HttpResponseRedirect(reverse(index))
    
@login_required
def watchlist(request):
    user_watchlist_items = Watchlist.objects.filter(user=request.user)
    return render(request, 'auctions/watchlist.html', {'watchlist_items': user_watchlist_items})

@login_required
def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    isinwatchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    return render(request, 'auctions/listing.html', {'listing': listing, 'isinwatchlist': isinwatchlist})

@login_required
def comment(request, listing_id):
    if request.method == "POST":
        user_comment = request.POST.get("comment")
        listing = get_object_or_404(Listing, pk=listing_id)
        if user_comment:  # Make sure the comment is not empty
            comment = Comment(owner=request.user, comment=user_comment, listing=listing)  # Use `owner` here
            comment.save()
            return redirect('listing', listing_id=listing_id)
    else:
        return redirect('index')  # Redirect if not a POST request

@login_required
def addwatchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    Watchlist.objects.create(user=request.user, listing=listing)
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def removewatchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    watchlist_item = Watchlist.objects.filter(user=request.user, listing=listing)
    watchlist_item.delete()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def bid(request):
    return
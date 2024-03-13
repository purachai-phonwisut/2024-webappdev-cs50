from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *


def index(request):
    active =Listing.objects.filter(isactive=True)
    return render(request, "auctions/index.html",{
        "listings" : active
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

def createlisting(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        return render(request, "auctions/create_listing.html", {
            "categories": categories
        })
    else:
        title = request.POST["title"]
        desc = request.POST["desc"]
        price = float(request.POST["price"])
        imageURL = request.POST["imageURL"]
        category = request.POST["category"]
        now_user = request.user

        catedata = Category.objects.get(cname=category)
        newlist = Listing(
            title = title,
            desc = desc,
            price = price,
            imageURL = imageURL,
            category = catedata,
            seller = now_user
        )

        newlist.save()
        return HttpResponseRedirect(reverse(index))
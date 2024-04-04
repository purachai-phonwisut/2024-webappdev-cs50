from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from .models import User,Post


def index(request):
    posts = Post.objects.all().order_by('-timestamp')
    return render(request, "network/index.html", {'posts':posts})

def following(request):
    return render(request, "network/following.html")

@login_required
def new(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            Post.objects.create(
                content=form.cleaned_data['content'],
                user=request.user
            )

        return redirect('index')

    else:
        return render(request, "network/new.html")


def get_follower_count(user):
    return Relationship.objects.filter(following=user).count()

def get_following_count(user):
    return Relationship.objects.filter(follower=user).count()


@login_required
def profile(request, userID):
    userProfile = get_object_or_404(User, pk=userID)
    userPosts = Post.objects.filter(user=userProfile).order_by('-timestamp')


    context = {
        'userProfile': userProfile,
        'userPosts': userPosts,
    }

    return render(request, "network/profile.html", context)

def post(request,postID):
       
    return

def edit(request,postID):
    return

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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
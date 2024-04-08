from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect,JsonResponse,HttpResponseForbidden
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from .models import User,Post,Follow, Like
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

import json



def index(request):
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)  # Show 10 posts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {'page_obj': page_obj})

@login_required
def following(request):
    # Get the list of users that the current user is following
    user_following = Follow.objects.filter(user=request.user).values_list('user_follower', flat=True)

    # Filter posts to only include those created by followed users
    posts = Post.objects.filter(user__in=user_following).order_by('-timestamp')

    paginator = Paginator(posts, 10)  # Show 10 posts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {'page_obj': page_obj})

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




@login_required
def profile(request, userID):
    # Get the user profile using the userID or return 404 if not found
    userProfile = get_object_or_404(User, pk=userID)

    # Fetch the posts made by the user and order them by timestamp
    userPosts = Post.objects.filter(user=userProfile).order_by('-timestamp')

    # Check if the current user is following the userProfile
    is_following = Follow.is_following(request.user, userProfile)


    # Prepare the context with all necessary information
    context = {
        'userProfile': userProfile,
        'userPosts': userPosts,
        'is_following': is_following,  # Add the is_following flag to the context
        'current_user' : request.user
    }

    # Render the profile page with the context
    return render(request, "network/profile.html", context)



@login_required
def follow_toggle(request):
    if request.method == 'POST':
        other_user_id = request.POST.get('other_user_id')
        other_user = get_object_or_404(User, id=other_user_id)

        follow_obj, created = Follow.objects.get_or_create(user=request.user, user_follower=other_user)

        if not created:
            # The follow relationship already existed, so unfollow
            follow_obj.delete()
            action = 'unfollowed'
        else:
            action = 'followed'

        return JsonResponse({"status": "ok", "action": action})
    else:
        return JsonResponse({"status": "error"}, status=400)



@require_POST
@csrf_exempt
def edit(request, postID):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required."}, status=403)

    try:
        data = json.loads(request.body)
        post = Post.objects.get(id=postID, user=request.user)
        post.content = data.get('content')
        post.save()
        return JsonResponse({"success": True})
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@require_POST
def like(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        post_id = data.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        like_qs = Like.objects.filter(user=request.user, post=post)

        if like_qs.exists():
            like_qs[0].delete()
            action = 'unliked'
        else:
            Like.objects.create(user=request.user, post=post)
            action = 'liked'

        return JsonResponse({"status": "ok", "action": action})
    else:
        return JsonResponse({"status": "error"}, status=400)

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
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from .models import User, Post, Follow, Like
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


def index(request):
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        return redirect('?page=1')

    return render(request, "network/index.html", {'page_obj': page_obj})


@login_required
def following(request):
    user_following = Follow.objects.filter(user=request.user).values_list('user_follower', flat=True)
    posts = Post.objects.filter(user__in=user_following).order_by('-timestamp')

    paginator = Paginator(posts, 10)

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
    userProfile = get_object_or_404(User, pk=userID)
    userPosts = Post.objects.filter(user=userProfile).order_by('-timestamp')
    is_following = Follow.is_following(request.user, userProfile)

    paginator = Paginator(userPosts, 10)
    page_number = request.GET.get('page', 1)

    follower_count = Follow.objects.filter(user_follower=userProfile).count()
    following_count = Follow.objects.filter(user=userProfile).count()

    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        return redirect('?page=1')

    context = {
        'userProfile': userProfile,
        'userPosts': userPosts,
        'is_following': is_following,
        'current_user': request.user,
        'page_obj': page_obj,
        'follower_count': follower_count,
        'following_count': following_count,
    }

    return render(request, "network/profile.html", context)


def get_follow_counts(request, userID):
    if request.is_ajax():
        userProfile = get_object_or_404(User, pk=userID)
        follower_count = Follow.objects.filter(user_follower=userProfile).count()
        following_count = Follow.objects.filter(user=userProfile).count()
        return JsonResponse({'follower_count': follower_count, 'following_count': following_count})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def follow_toggle(request):
    if request.method == 'POST':
        other_user_id = request.POST.get('other_user_id')
        other_user = get_object_or_404(User, id=other_user_id)

        follow_obj, created = Follow.objects.get_or_create(user=request.user, user_follower=other_user)

        if not created:
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
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

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
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

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

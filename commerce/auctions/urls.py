from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("closed", views.closed, name="closed"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", views.newlisting, name="newlisting"),
    path("category/", views.category, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("addwatchlist/<int:listing_id>", views.addwatchlist, name= "addwatchlist"),
    path("removewatchlist/<int:listing_id>", views.removewatchlist, name= "removewatchlist"),
    path("category/<int:category_id>", views.category, name="category_with_id"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/<int:listing_id>/comment", views.comment, name="comment"),
    path("listing/<int:listing_id>/bid", views.bid, name="bid")


]

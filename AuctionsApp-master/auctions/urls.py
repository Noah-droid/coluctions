from django.urls import path

from . import views

app_name="auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("list/<int:list_id>", views.getlist, name="list"),
    path("<int:list_id>/watchlist_add", views.watchlist_add, name="watchlist_add"),
    path("<int:list_id>/watchlist_remove", views.watchlist_remove, name="watchlist_remove"),
    path("<int:list_id>/comment", views.comment, name="comment"),
    path("<int:list_id>/bid", views.bid, name="bid"),
    path("<int:list_id>/close", views.close, name="close"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:cat_id>", views.getcategory, name="getcategory"),
    path("mylist", views.mylist, name="mylist"),
    path("search", views.search, name="search")
]

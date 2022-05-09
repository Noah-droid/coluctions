from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Category, Auction, Bid, Comment, Watchlist
from .forms import CreateForm, CommentForm, BidForm, SearchForm

def index(request):
    auctions = Auction.objects.filter(active=True).order_by("-date")
    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "searchform": SearchForm()
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
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            messages.add_message(request, message.ERROR, 'Invalid username and/or password.')
            return HttpResponseRedirect(reverse("auctions:login"))
    else:
        return render(request, "auctions/login.html", {
            "searchform": SearchForm()
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.add_message(request, message.ERROR, 'Passwords must match.')
            return HttpResponseRedirect(reverse("auctions:register"))

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.add_message(request, message.ERROR, 'Username already taken.')
            return HttpResponseRedirect(reverse("auctions:register"))
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html", {
            "searchform": SearchForm()
        })


@login_required(redirect_field_name='')
def create(request):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.author = request.user
            data.save()
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/create.html", {
                "createform": form,
                "searchform": SearchForm()
            })

    else:
        return render(request, "auctions/create.html", {
        "createform": CreateForm()
        })

@login_required(redirect_field_name='')
def getlist(request, list_id):
    auction = Auction.objects.get(pk=list_id)
    comments = Comment.objects.filter(auction_id=list_id).order_by('-date')
    highestbid = Bid.objects.filter(auction_id=list_id).order_by('-amount').first()
    return render(request, "auctions/list.html", {
        "auction": auction,
        "comments": comments,
        "commentform": CommentForm(),
        "bidform": BidForm(),
        "highestbid": highestbid,
        "searchform": SearchForm()
    })

@login_required(redirect_field_name='')
def watchlist_add(request, list_id):
    if request.method == "POST":
        auction = Auction.objects.get(pk=list_id)
        check = Watchlist.objects.filter(id=request.user.id, product=list_id).first()
        if check is not None:
            messages.add_message(request, messages.WARNING, 'This auction is already in your watchlist.')
            return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
        else:
            try:
                usrlist = Watchlist.objects.get(id=request.user.id)
                usrlist.product.add(auction)
                usrlist.save()
                messages.add_message(request, messages.SUCCESS, 'Successfully added to your watchlist.')
                return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
            except ObjectDoesNotExist:
                usrlist = Watchlist(id=request.user.id, owner_id=request.user.id)
                usrlist.save()
                usrlist.product.add(auction)
                messages.add_message(request, messages.SUCCESS, 'Successfully added to your watchlist.')
                return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
        

@login_required(redirect_field_name='')
def watchlist_remove(request, list_id):
    if request.method == "POST":
        auction = Auction.objects.get(pk=list_id)
        check = Watchlist.objects.filter(id=request.user.id, product=list_id).first()
        if check is None:
            messages.add_message(request, messages.WARNING, 'This auction is not in your watchlist.')
            return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
        else:
            try:
                usrlist = Watchlist.objects.get(id=request.user.id)
                usrlist.product.remove(auction)
                usrlist.save()
                messages.add_message(request, messages.ERROR, 'Successfully removed from your watchlist.')
                return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
            except ObjectDoesNotExist:
                messages.add_message(request, messages.WARNING, 'This auction is not in your watchlist.')
                return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
                
@login_required(redirect_field_name='')
def comment(request, list_id):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            auction = Auction.objects.get(pk=list_id)
            data = form.save(commit=False)
            data.author = request.user
            data.auction = auction
            data.save()
            messages.add_message(request, messages.SUCCESS, "Your comment was successfully posted.")
            return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
        else:
            messages.add_message(request, messages.ERROR, "Your comment form is invalid.")
            return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))

@login_required(redirect_field_name='')
def bid(request, list_id):
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bidamount = form.cleaned_data["amount"]
            auction = Auction.objects.get(pk=list_id)
            if request.user.id == auction.author_id:
                messages.add_message(request, messages.ERROR, "You can't bid on your own auction.")
                return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
            if not auction.active:
                messages.add_message(request, messages.ERROR, "You can't bid on a closed auction.")
                return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
            if bidamount <= auction.starting_price:
                messages.add_message(request, messages.ERROR, "You must place a higher bid than the current price.")
                return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
            higherbid = Bid.objects.filter(auction_id=list_id).order_by('-amount').first()
            if higherbid is not None:
                if bidamount <= higherbid.amount:
                    messages.add_message(request, messages.ERROR, "You must place a higher bid than the current price.")
                    return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
                else:
                    data = form.save(commit=False)
                    auction.current_price = bidamount
                    data.author_id = request.user.id
                    data.auction_id = list_id
                    data.save()
                    auction.save()
                    messages.add_message(request, messages.SUCCESS, "Your bid was successfully placed :)")
                    return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
            else:
                data = form.save(commit=False)
                auction.current_price = bidamount
                data.author_id = request.user.id
                data.auction_id = list_id
                data.save()
                auction.save()
                messages.add_message(request, messages.SUCCESS, "Your bid was successfully placed :)")
                return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
        else:
            messages.add_message(request, messages.ERROR, "Your form is invalid.")
            return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))

def categories(request):
    categories = Category.objects.all().order_by("name")
    return render(request, "auctions/categories.html", {
        "categories": categories,
        "searchform": SearchForm()
    })

@login_required(redirect_field_name='')
def mylist(request):
    auctions = Auction.objects.filter(watchlist__id=request.user.id, active=True)
    return render(request, "auctions/mylist.html", {
        "auctions": auctions,
        "searchform": SearchForm()
    })

def getcategory(request, cat_id):
    auctions = Auction.objects.filter(category_id=cat_id).order_by('-date')
    category = Category.objects.get(id=cat_id)
    return render(request, "auctions/category.html", {
        "auctions": auctions,
        "category": category,
        "searchform": SearchForm()
    })

@login_required(redirect_field_name='')
def close(request, list_id):
    if request.method == "POST":
        auction = Auction.objects.get(pk=list_id)
        if request.user.id == auction.author_id:
            auction.active = False
            auction.save()
            messages.add_message(request, messages.SUCCESS, "Your auction was successfully closed.")
            return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))
        else:
            messages.add_message(request, messages.ERROR, "You did not create this auction.")
            return HttpResponseRedirect(reverse("auctions:list", args=(list_id,)))

def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            usrsearch = form.cleaned_data["search"]
            result = Auction.objects.filter(title__icontains=usrsearch) | Auction.objects.filter(category__name__icontains=usrsearch)
            return render(request, "auctions/search.html", {
                "auctions": result,
                "search_str": usrsearch,
                "searchform": SearchForm()
            })
        else:
            messages.add_message(request, messages.ERROR, "Your search is invalid.")
            return HttpResponseRedirect(reverse("auctions:index"))
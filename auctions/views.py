from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Categories, Items, Bid, Comments

def index(request):
    items = Items.objects.all()

    return render(request, "auctions/index.html", {
        "items": items
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
    
def create(request):
    if request.method == "POST":
        title = request.POST['listingTitle']
        description = request.POST['listingDescr']
        starting_bid = request.POST['startingBid']
        img_url = request.POST['imgURL']
        category = request.POST['listingCategory']

        bid = Bid(amount="%0.2f" % float(starting_bid), user=request.user)
        bid.save()

        listings = Items(name = title, user = request.user, description = description, price = bid, url = img_url, category = Categories.objects.get(category = category), listed = True)
        listings.save()

        return HttpResponseRedirect(reverse(index)) #,{
            #"items": Items,
            #"title": Items.objects.title,
            #"description": Items.objects.description,
            #"image": Items.objects.url,
            #"price": "%0.2f" % int(Items.objects.price),
            #"category": Categories.objects.category
        #})
    else:
        category = Categories.objects.all()
        return render(request, "auctions/create.html", {
            "categories": category
        })

def listing(request, id):
    listing = Items.objects.get(id=id)

    title = listing.name
    image = listing.url
    description = listing.description
    price = listing.price
    category = listing.category
    user = request.user
    watchlist = "Yes"
    close = 0
    comments = Comments.objects.filter(item = listing)

    if listing.user == user:
        close += 1

    if user not in listing.watchlist.all():
        watchlist = "No"

    if request.method == "GET":
        return render(request, "auctions/listing.html", {
            "title": title,
            "image": image,
            "description": description,
            "price": price,
            "category": category,
            "watchlist": watchlist,
            "id": int(id),
            "close": close,
            "comments": comments,
            "name": listing.user
        })

def add(request, id):
    listing = Items.objects.get(id=id)

    title = listing.name
    image = listing.url
    description = listing.description
    price = listing.price
    category = listing.category
    user = request.user

    listing.watchlist.add(user)
    watchlist = "Yes"

    return HttpResponseRedirect(reverse("listing", args=(id, )))
    #return render(request, "auctions/listing.html", {
        #"title": title,
        #"image": image,
        #"description": description,
        #"price": price,
        #"category": category,
        #"watchlist": watchlist,
        #"id": int(id)
    #})

def remove(request, id):
    listing = Items.objects.get(id=id)

    title = listing.name
    image = listing.url
    description = listing.description
    price = listing.price
    category = listing.category
    user = request.user

    listing.watchlist.remove(user)
    watchlist = "No"

    return HttpResponseRedirect(reverse("listing", args=(id, )))
        #return HttpResponseRedirect(reverse("listing"))

def watchlist(request):
    user = request.user
    empty = []
    items = user.watcher.all()

    return render(request, "auctions/watchlist.html", {
        "items": items,
        "empty": empty
    })

def bid(request, id):
    listing = Items.objects.get(id=id)
    amount = "%0.2f" % float(request.POST['amount'])
    current_bid = float(request.POST['price'])
    starting_bid = Bid.objects.get(id=id)

    if request.method == "POST":
        if float(amount) >= float(current_bid):
            starting_bid.amount = amount
            starting_bid.user = request.user
            
            starting_bid.save()

            listing.price = starting_bid
            listing.save()

            return HttpResponseRedirect(reverse("listing", args=(id, )))
    
        else:
            return render(request, "auctions/error.html")
        
def close(request, id):
    listing = Items.objects.get(id=id)
    closer = listing.user
    you = request.user
    bid = Bid.objects.get(id=id)
    winner = bid.user

    if request.method == "POST":
        listing.listed = False
        listing.save()
        return render(request, "auctions/close.html", {
            "title": listing.name,
            "image": listing.url,
            "description": listing.description,
            "price": listing.price,
            "category": listing.category,
            "watchlist": listing.watchlist,
            "id": int(id),
            "closer": closer,
            "you": you,
            "winner": winner
        })
    
    else:
        return render(request, "auctions/close.html", {
            "title": listing.name,
            "image": listing.url,
            "description": listing.description,
            "price": listing.price,
            "category": listing.category,
            "watchlist": listing.watchlist,
            "id": int(id),
            "closer": closer,
            "you": you,
            "winner": winner
        })
    
def comments(request, id):
    listing = Items.objects.get(id=id)
    user = request.user
    comment = request.POST['comment']

    new_comment = Comments(user = user, item = listing, comment = comment)
    new_comment.save()

    return HttpResponseRedirect(reverse("listing", args=(id, )))

def categories(request):
    categories = Categories.objects.all()
    items = Items.objects.all()

    if request.method == "GET":
        return render(request, "auctions/categories.html", {
            "categories": categories,
            "items": items,
            "request": request.method
        })
    
    elif request.method == "POST":
        input = request.POST['view']
        category = Categories.objects.get(category=input)
        match = Items.objects.filter(listed=True, category=category)
        return render(request, "auctions/categories.html", {
            "request": request.method,
            "items": match
        })
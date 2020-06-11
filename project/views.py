from math import acos, sin, cos
from algoliasearch.search_client import SearchClient
from django.shortcuts import render, redirect
from google.auth.transport import requests
from requests.exceptions import HTTPError
from .models import MapPoint
from django.contrib import auth
from django.db.models import Max
import gmplot
import geocoder
import pyrebase
import re

API_KEY = "AIzaSyBb8naJyiLvTPtVyU4MrYeUxPtEH7aaXjU"
user_location = geocoder.ip('me')
print(user_location)
user_location = [27.054, 56.463]
user_lat_location = user_location[0]
user_long_location = user_location[1]
lat_max_range = user_lat_location + 0.008983 * 5
lat_min_range = user_lat_location - 0.008983 * 5
config = {
    'apiKey': "AIzaSyBb8naJyiLvTPtVyU4MrYeUxPtEH7aaXjU",
    'authDomain': "mapploting.firebaseapp.com",
    'databaseURL': "https://mapploting.firebaseio.com",
    'projectId': "mapploting",
    'storageBucket': "mapploting.appspot.com",
    'messagingSenderId': "845625156693",
    'appId': "1:845625156693:web:162b82d22aeb57992fe0dc",
    'measurementId': "G-T5EVBNC4EP"
}
firebase = pyrebase.initialize_app(config)
firebase_auth = firebase.auth()
db = firebase.database()
regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


def map_point(request):
    query_set = MapPoint.objects.filter(lat__range=(lat_min_range, lat_max_range)).values_list('lat', 'long')
    avaialble_location = list(query_set)
    search_result = len(avaialble_location)
    lat_location_list = []
    long_location_list = []
    for item in avaialble_location:
        lat_location_list.append(item[0])
        long_location_list.append(item[1])
    # gmap = gmplot.GoogleMapPlotter(user_lat_location, user_long_location, 13, apikey=)
    # scatter method of map object
    # scatter points on the google map
    # gmap.scatter(latitude_list, longitude_list, '# FF0000',
    #               size=40, marker=False)

    # Plot method Draw a line in
    # between given coordinates
    # gmap3.plot(latitude_list, longitude_list,
    #            'cornflowerblue', edge_width=2.5)

    # gmap.draw('/home/arnab/Documents/pakiza/map/project/templates/project/map_plot.html')
    return render(request, 'project/base.html', {
        'user_lat_location': user_lat_location,
        'user_long_location': user_long_location,
        'lat_location_list': lat_location_list,
        'long_location_list': long_location_list,
        'search_result': search_result,
        'map_key': 0
    })


def map_with_key(request):
    key = request.POST.get('search','')
    query_set = MapPoint.objects.filter(product=key, lat__range=(lat_min_range, lat_max_range)).values_list('lat', 'long')
    avaialble_location = list(query_set)
    print(avaialble_location)
    search_result = len(avaialble_location)
    lat_location_list = []
    long_location_list = []
    for item in avaialble_location:
        lat_location_list.append(item[0])
        long_location_list.append(item[1])
    return render(request, 'project/base.html', {
        'user_lat_location': user_lat_location,
        'user_long_location': user_long_location,
        'lat_location_list': lat_location_list,
        'long_location_list': long_location_list,
        'search_result': search_result,
        'map_key': 1
    })


def listProduct(request):
    query_set = MapPoint.objects.filter(lat__range=(lat_min_range, lat_max_range)).values_list('lat', 'long')
    avaialble_location = list(query_set)
    search_result = len(avaialble_location)
    lat_location_list = []
    long_location_list = []
    for item in avaialble_location:
        lat_location_list.append(item[0])
        long_location_list.append(item[1])
    # return render(request, 'project/productListView.html', {})
    return render(request, 'project/productListView.html', {
            'user_lat_location': user_lat_location,
            'user_long_location': user_long_location,
            'lat_location_list': lat_location_list,
            'long_location_list': long_location_list,
            'search_result': search_result,
            'map_key': 0
        })


def signIn(request):
    # client = SearchClient.create('B63JMYDZ2L', '3d38a871869ebbd41ce21d5841490ff3')
    # index = client.init_index('prod_Name')
    # data = { "product_name":"John", "store_id":30, "city":"New York"}
    try:
        user = request.session['uid']
        return redirect('mappoint')
    except:
        return render(request, 'project/signin.html', {})


def authCheck(request):
    email = request.POST.get('email', '')
    password = request.POST.get('password','')
    try:
        user = firebase_auth.sign_in_with_email_and_password(email, password)
    except:
        message = 'Invalid Credentials'
        return render(request, 'project/signin.html', {'message': message})
    session_id = user['idToken']
    request.session['uid'] = str(session_id)
    return redirect('mappoint')


def logout(request):
    auth.logout(request)
    return redirect('login')


def signup(request):
    return render(request, 'project/signup.html', {})


def signup_request(request):
    store_name = request.POST.get('store_name', '')
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')
    status = request.POST.get('status', '')
    if not re.search(regex, email):
        message = "Invalid email"
        return render(request, 'project/signup.html', {"message": message})
    if status == '1':
        if store_name is "":
            message = "Enter store name"
            return render(request, 'project/signup.html', {"message": message})

    if len(password) < 6:
        message = "Password should be at least 6 characters"
        return render(request, 'project/signup.html', {"message": message})
    if password != confirm_password:
        message = "Password doesn't match"
        return render(request, 'project/signup.html', {"message": message})
    try:
        user = firebase_auth.create_user_with_email_and_password(email, password)
    except HTTPError as e:
        message = "Email exists"
        return render(request, 'project/signup.html', {"message": message})
    uid = user['localId']
    if status == "1":
        data = {
            "store_name": store_name,
            "lat": user_lat_location,
            "long": user_long_location,
            "status": "business_user"
        }
    else:
        data = {
            "status": "user"
        }
    db.child("users").child(uid).child("details").set(data)
    return render(request, 'project/signin.html', {})


def product_details(request):
    return render(request, 'project/product_details.html', {})


def business_list(request):
    return render(request, 'project/businessList.html', {})


def add_product(request):
    return render(request, 'project/addproduct.html', {})


def business_map(request):
    query_set = MapPoint.objects.filter(lat__range=(lat_min_range, lat_max_range)).values_list('lat', 'long')
    avaialble_location = list(query_set)
    search_result = len(avaialble_location)
    lat_location_list = []
    long_location_list = []
    for item in avaialble_location:
        lat_location_list.append(item[0])
        long_location_list.append(item[1])
    return render(request, 'project/businessMap.html', {
        'user_lat_location': user_lat_location,
        'user_long_location': user_long_location,
        'lat_location_list': lat_location_list,
        'long_location_list': long_location_list,
        'search_result': search_result,
        'map_key': 0
    })


def update_info(request):
    return render(request, 'project/updateinfo.html', {})


def store_details(request):
    return render(request, 'project/store_details.html', {})


def dashboard(request):
    return render(request, 'project/dashboard.html', {})


def store_products(request):
    return render(request, 'project/store_products.html', {})


def change_password(request):
    return render(request, 'project/change_password.html', {})
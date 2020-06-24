from math import acos, sin, cos
from django.core.files.images import ImageFile
from algoliasearch.search_client import SearchClient
from django.http import HttpResponse
from django.shortcuts import render, redirect
from google.auth.transport import requests
import math
from requests.exceptions import HTTPError
from .models import MapPoint
from django.contrib import auth
from django.db.models import Max
from datetime import datetime
import gmplot
import geocoder
import pyrebase
import re
import base64
import json


API_KEY = "AIzaSyBhoFFaf8hZHabaiTJjG2VXPz907Em-26Q"
user_location = geocoder.ip('me').latlng
user_lat_location = -33.864736
user_long_location = 151.2043333
lat_max_range = user_lat_location + 0.008983 * 5
lat_min_range = user_lat_location - 0.008983 * 5

config = {
    'apiKey': "AIzaSyBhoFFaf8hZHabaiTJjG2VXPz907Em-26Q",
    'authDomain': "mainies.firebaseapp.com",
    'databaseURL': "https://mainies.firebaseio.com",
    'projectId': "mainies",
    'storageBucket': "mainies.appspot.com",
    'messagingSenderId': "851721809201",
    'appId': "1:851721809201:web:aa038ed270e0d8bb86d410",
    'measurementId': "G-W61PYZL1JM"
}

firebase = pyrebase.initialize_app(config)
firebase_auth = firebase.auth()
db = firebase.database()
# storage = firebase.storage()
regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


def distance(lat1, lon1, lat2, lon2):
    radius = 6371
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return round(d, 1)


def map_point(request):
    lat_list = []
    long_list = []
    store_name = ''
    store_address = ''
    product_names = ''
    all_users = db.child().get()
    if request.method == 'POST':
        search_string = request.POST.get('search', '').lower()
        for product in all_users.each():
            try:
                name = product.val().get('user_info').get('store_name')
                lat = float(product.val().get('user_info').get('lat'))
                long = float(product.val().get('user_info').get('long'))
                address = product.val().get('user_info').get('address')
                u_product = product.val().get('products')
                if u_product:
                    for key, value in u_product.items():
                        product_name = value.get('product_name').lower()
                        product_name = product_name.split(' ')
                        flag = False
                        for item in product_name:
                            if item == search_string:
                                flag = True
                                break
                        if not flag:
                            continue
                        product_names = product_names + value.get('product_name') + '+'
                        distance_km = distance(
                            lat,
                            long,
                            user_lat_location,
                            user_long_location
                        )
                        if distance_km >= 0:
                            lat_list.append(lat)
                            long_list.append(long)
                            store_name = store_name + name + '+'
                            store_address = store_address + address + '+'
            except:
                pass
        print(lat_list)
        return render(request, 'project/base.html', {
            'user_lat_location': user_lat_location,
            'user_long_location': user_long_location,
            'lat_location_list': lat_list,
            'long_location_list': long_list,
            'store_name': store_name,
            'store_address': store_address,
            'product_names': product_names,
            'map_key': 0
        })

    for product in all_users.each():
        try:
            lat = float(product.val().get('user_info').get('lat'))
            long = float(product.val().get('user_info').get('long'))
            name = product.val().get('user_info').get('store_name')
            address = product.val().get('user_info').get('address')
            u_product = product.val().get('products')
            if u_product:
                for key, value in u_product.items():
                    product_names = product_names + value.get('product_name') + '+'
                    distance_km = distance(
                        lat,
                        long,
                        user_lat_location,
                        user_long_location
                    )
                    if distance_km >= 0:
                        lat_list.append(lat)
                        long_list.append(long)
                        store_name = store_name + name + '+'
                        store_address = store_address + address + '+'
                    break
        except:
            pass

    search_result = len(lat_list)
    print(product_names)
    print(lat_list)
    return render(request, 'project/base.html', {
        'user_lat_location': user_lat_location,
        'user_long_location': user_long_location,
        'lat_location_list': lat_list,
        'long_location_list': long_list,
        'store_name': store_name,
        'store_address': store_address,
        'product_names': product_names,
        'search_result': search_result,
        'map_key': 0
    })


def map_with_key(request):
    key = request.POST.get('search', '')
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
    send_dict = {}
    all_products = db.child().get()
    for product in all_products.each():
        u_product = product.val().get('products')
        if u_product:
            for key, value in u_product.items():
                send_dict[key] = value
    return render(request, 'project/productListView.html', {"data": send_dict})


def signIn(request):
    # client = SearchClient.create('B63JMYDZ2L', '3d38a871869ebbd41ce21d5841490ff3')
    # index = client.init_index('prod_Name')
    # data = { "product_name":"John", "store_id":30, "city":"New York"}
    try:
        user = request.session['uid']
        print(user)
        return redirect('mappoint')
    except:
        return render(request, 'project/signin.html', {})


def authCheck(request):
    email = request.POST.get('email', '')
    password = request.POST.get('password','')
    print(email, password)
    try:
        user = firebase_auth.sign_in_with_email_and_password(email, password)
        print(user)
    except:
        message = 'Invalid Credentials'
        return render(request, 'project/signin.html', {'message': message})

    session_id = user['localId']
    print(user['idToken'])
    request.session['uid'] = str(session_id)
    request.session['idToken'] = str(user['idToken'])
    return redirect('mappoint')


def logout(request):
    auth.logout(request)
    return redirect('login')


def signup(request):
    return render(request, 'project/signup.html', {})


def signup_request(request):
    # store_name = request.POST.get('store_name', '')
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')

    if not re.search(regex, email):
        message = "Invalid email"
        return render(request, 'project/signup.html', {"message": message})

    if len(password) < 6:
        message = "Password should be at least 6 characters"
        return render(request, 'project/signup.html', {"message": message})

    if password != confirm_password:
        message = "Password doesn't match"
        return render(request, 'project/signup.html', {"message": message})

    try:
        user = firebase_auth.create_user_with_email_and_password(email, password)
        print(user)
    except HTTPError as e:
        message = "Email exists"
        return render(request, 'project/signup.html', {"message": message})

    return render(request, 'project/signin.html', {})


def product_details(request, key, uid):
    product = db.child(uid).child("products").child(key).get().val()
    product = json.loads(json.dumps(product))
    store_data = db.child(uid).child('user_info').get().val()
    store_data = json.loads(json.dumps(store_data))

    data = db.child("user_confirmation").child(key).get().val()
    output_dict = json.loads(json.dumps(data))
    like_counter = 0
    dislike_counter = 0
    if output_dict is not None:
        for k, value in output_dict.items():
            if value.get('val') == 1:
                like_counter += 1
            elif value.get('val') == 0:
                dislike_counter += 1
    print('key here', key)
    return render(request, 'project/product_details.html', {
        "like": like_counter,
        'dislike': dislike_counter,
        "p_id": str(key),
        "data": product,
        "store_name": store_data.get('store_name')
    })


def business_list(request):
    send_dict = {}
    all_users = db.child().get()
    for product in all_users.each():
        try:
            user_info = product.val().get('user_info')
            distance_km = distance(
                float(product.val().get('user_info').get('lat')),
                float(product.val().get('user_info').get('long')),
                float(user_lat_location),
                float(user_long_location)
            )
            user_info['distance'] = distance_km
            if distance_km >= 0:
                send_dict[product.key()] = user_info
        except:
            pass
    return render(request, 'project/businessList.html', {"data": send_dict})


def add_product(request):
    return render(request, 'project/addproduct.html', {})


def add_product_firebase(request):
    uid = request.session.get('uid')
    data = db.child(uid).get().val()
    dict = json.loads(json.dumps(data))
    store_name = dict.get('user_info').get('store_name')
    lat = dict.get('user_info').get('lat')
    long = dict.get('user_info').get('long')
    name = request.POST.get('name', '')
    price = request.POST.get('price', '')
    description = request.POST.get('description', '')
    image = request.FILES['image']
    encoded_string = base64.b64encode(image.read())
    imgdata = encoded_string.decode("utf-8")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at = created_at
    product = {
        "product_name": name,
        "product_price": price,
        "product_image": imgdata,
        "product_description": description,
        "lat": lat,
        "long": long,
        "uid": uid,
        "store_name":store_name,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    product_firebase = db.child(uid).child("products").push(product)
    if product_firebase:
        return redirect('submitproduct')
    return redirect('addproduct')


def submitproduct(request):
    return render(request, 'project/submitproduct.html', {})


def add_business_firebase(request):
    store_name = request.POST.get('store_name', '')
    address = request.POST.get('address', '')
    phone = request.POST.get('phone', '')
    country = request.POST.get('country', '')
    city = request.POST.get('city', '')
    postal = request.POST.get('postal', '')
    category = request.POST.get('category', '')
    price_range = request.POST.get('price_range', '')
    open_time = request.POST.get('open_time', '')
    close_time = request.POST.get('close_time', '')
    days = request.POST.getlist('days')
    image = request.FILES['image']
    lat = request.POST.get('lat', '')
    long = request.POST.get('long', '')
    facebook = request.POST.get('facebook', '')
    website = request.POST.get('website', '')
    twitter = request.POST.get('twitter', '')
    encoded_string = base64.b64encode(image.read())
    imgdata = encoded_string.decode("utf-8")
    days_data = ""
    for item in days:
        days_data += item+', '
    uid = request.session.get('uid')
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at = created_at
    data = {
        "store_name": store_name,
        "address": address,
        "phone": phone,
        "country": country,
        "city": city,
        "postal": postal,
        "category": category,
        "price_range": price_range,
        "open_time": open_time,
        "close_time": close_time,
        "days": days_data,
        "img": imgdata,
        "lat": lat,
        "long": long,
        "facebook": facebook,
        "website": website,
        "twitter": twitter,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    name = db.child(uid).child("user_info").set(data)
    return redirect('storedetails/'+uid)


def business_map(request):
    lat_list = []
    long_list = []
    store_name = ''
    store_address = ''
    all_users = db.child().get()
    if request.method == 'POST':
        search_string = request.POST.get('search', '').lower()
        for product in all_users.each():
            try:
                name = product.val().get('user_info').get('store_name')
                lower_name = name.lower()
                name_split = lower_name.split(' ')
                flag = False
                for item in name_split:
                    if item == search_string:
                        flag = True
                        break
                if not flag:
                    continue
                lat = float(product.val().get('user_info').get('lat'))
                long = float(product.val().get('user_info').get('long'))
                address = product.val().get('user_info').get('address')
                distance_km = distance(
                    lat,
                    long,
                    float(user_lat_location),
                    float(user_long_location)
                )
                if distance_km >= 0:
                    lat_list.append(lat)
                    long_list.append(long)
                    store_name = store_name + name + '+'
                    store_address = store_address + address + '+'
            except:
                print('error')
                pass
        return render(request, 'project/businessMap.html', {
            'user_lat_location': user_lat_location,
            'user_long_location': user_long_location,
            'lat_location_list': lat_list,
            'long_location_list': long_list,
            'store_name': store_name,
            'store_address': store_address,
            'map_key': 1
        })
    for product in all_users.each():
        try:
            lat = float(product.val().get('user_info').get('lat'))
            long = float(product.val().get('user_info').get('long'))
            name = product.val().get('user_info').get('store_name')
            address = product.val().get('user_info').get('address')
            distance_km = distance(
                lat,
                long,
                user_lat_location,
                user_long_location
            )
            if distance_km >= 0:
                lat_list.append(lat)
                long_list.append(long)
                store_name = store_name + name + '+'
                store_address = store_address + address + '+'
        except:
            print('error')
            pass
    search_result = len(lat_list)
    return render(request, 'project/businessMap.html', {
        'user_lat_location': lat_list[1],
        'user_long_location': long_list[1],
        'lat_location_list': lat_list,
        'long_location_list': long_list,
        'store_name': store_name,
        'store_address': store_address,
        'search_result': search_result,
        'map_key': 1
    })


def update_info(request):
    return render(request, 'project/updateinfo.html', {})


def store_details(request, key):
    uid = request.session.get('uid')
    data = db.child(key).child('user_info').get().val()
    output_dict = json.loads(json.dumps(data))
    return render(request, 'project/store_details.html', {
        "data": output_dict
    })


def dashboard(request):
    uid = request.session.get('uid')
    data = db.child(uid).child('user_info').get().val()
    output_dict = json.loads(json.dumps(data))
    return render(request, 'project/dashboard.html', {
        "data": output_dict
    })


def store_products(request):
    uid = request.session.get('uid')
    print(uid)
    data = db.child(uid).child("products").get().val()
    data = json.loads(json.dumps(data))
    return render(request, 'project/store_products.html', {
        "data": data,
        "total": len(data)
    })


def change_password(request):
    return render(request, 'project/change_password.html', {})


def user_confirmation(request):
    product_id = request.GET['product_id']
    val = int(request.GET['val'])
    uid = request.session.get('uid')
    print(product_id, val, uid)
    data = db.child("user_confirmation").child(product_id).child(uid).get().val()
    if data is None:
        db.child("user_confirmation").child(product_id).child(uid).set({'val': val})
    elif data is not None and data != val:
        print('updated')
        # db.child("user_confirmation").child(product_id).child(uid).remove()
        db.child("user_confirmation").child(product_id).child(uid).update({'val': val})

    data = db.child("user_confirmation").child(product_id).get().val()
    output_dict = json.loads(json.dumps(data))
    like_counter = 0
    dislike_counter = 0
    print(output_dict)
    for key, value in output_dict.items():
        if value.get('val') == 1:
            like_counter += 1
        elif value.get('val') == 0:
            dislike_counter += 1

    print(like_counter, dislike_counter)
    return HttpResponse(str(like_counter) + '-' + str(dislike_counter))
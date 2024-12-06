from django.contrib import admin
from django.contrib import messages
import json
import re
import requests
from django.shortcuts import render,redirect,get_object_or_404

from marketplaceapp.forms import ProductForm,ContactForm
from marketplaceapp.models import Farmer, Product, Customer, Delivery,Contact
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db import transaction
from marketplaceapp.credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.http import HttpResponse
from pip._vendor.requests.auth import HTTPBasicAuth

# Create your views here.
def index(request):
    return render(request,'index.html')

def services(request):
    return render(request,'service-details.html')

def portfolio(request):
    return render(request,'portfolio-details.html')

def starter(request):
    return render(request,'starter-page.html')

def about(request):
    return render(request,'about.html')

def service(request):
    return render(request,'service.html')

def contact(request):
    if request.method == "POST":
        contact=Contact(
            name = request.POST['name'],
            email = request.POST['email'],
            subject = request.POST['subject'],
            message = request.POST['message'],
        )
        contact.save()
        return redirect('contact')
    else:
        return render(request,'contact.html')

def terms(request):
    return render(request,'terms.html')

def error(request):
    return render(request,'error.html')

def register_farmer(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        location = request.POST['location']
        password = request.POST['password']  # Hash passwords in production

        # Check for existing username or email
        if Farmer.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register-farmer')
        if Farmer.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register-farmer')

        # Save the farmer to the database
        Farmer.objects.create(
            full_name=full_name,
            username=username,
            email=email,
            phone=phone,
            location=location,
            password=password
        )
        messages.success(request, "Registration successful!")
        return redirect('login-farmer')  # Redirect to login page

    return render(request, 'register-farmer.html')

def login_farmer(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            farmer = Farmer.objects.get(username=username)
            if farmer.password == password:  # Use hashed passwords in production
                request.session['username'] = farmer.username  # Save farmer username in session
                return redirect('farmer-dashboard')
            else:
                messages.error(request, "Invalid password")
        except Farmer.DoesNotExist:
            messages.error(request, "Farmer not found")

    return render(request, 'login-farmer.html')

def farmer_dashboard(request):
    username = request.session.get('username')  # Retrieve farmer username from session
    if not username:
        return redirect('login-farmer')  # Redirect to login if session is empty

    try:
        farmer = Farmer.objects.get(username=username)
        return render(request, 'farmer-dashboard.html', {'username': farmer.username})
    except Farmer.DoesNotExist:
        return redirect('login-farmer')  # Redirect if farmer ID is invalid

def logout_farmer(request):
    return redirect('index')


def create_account(request):
    if request.method == 'POST':
        customer=Customer(
            email=request.POST['email'],
            password=request.POST['password']
        )
        customer.save()
        return redirect('login-customer')
    return render(request,'create-account.html')

def login_customer(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        customer = authenticate(request, email=email, password=password)
        if customer is not None:
            login(request, customer)
            messages.success(request, "Login successful!")
            return redirect('marketplace')  # Redirect to the home page
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('/login-customer')
    else:
        return render(request, 'login-customer.html')

def post_product(request):
    farmer = get_object_or_404(Farmer, username=request.session.get('username'))
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = farmer
            product.save()
            return redirect('farmer-dashboard')  # Redirect to farmer's dashboard after posting
    else:
        form = ProductForm()
    return render(request, 'post-product.html', {'form': form})

def marketplace(request):
    products = Product.objects.all()
    return render(request, 'marketplace.html', {'products': products})

def search_results(request):
    query = request.GET.get('query', '')  # Get the search term from the URL
    results = []

    if query:
        # Perform a search in the database (case-insensitive)
        results = Product.objects.filter(name__icontains=query)

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search-results.html', context)

def product_details(request, product_id):
    # Fetch the product using its unique product_id
    product = get_object_or_404(Product, product_id=product_id)
    return render(request, 'product-details.html', {'product': product})

def buy_product(request):
    return render(request,'buy-product.html')


def checkout(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == "POST":
        quantity = int(request.POST.get('quantity'))
        county = request.POST.get('county')
        town = request.POST.get('town')

        # Extract price as a number
        price = float(re.findall(r"\d+\.?\d*", product.price)[0])  # Extract numeric part of price
        subtotal = price * quantity

        # Save delivery details
        delivery = Delivery.objects.create(
            product=product,
            customer_name=request.POST.get('name'),
            customer_email=request.POST.get('email'),
            county=county,
            town=town,
            quantity=quantity,
            subtotal=subtotal,
        )

        # Store the delivery details in the session as a JSON object
        delivery_data = {
            'customer_name': delivery.customer_name,
            'customer_email': delivery.customer_email,
            'county': delivery.county,
            'town': delivery.town,
            'quantity': delivery.quantity,
            'subtotal': delivery.subtotal,
        }

        request.session['delivery_data'] = json.dumps(delivery_data)

        messages.success(request, "Your order has been placed successfully!")
        return redirect('purchase-summary', product_id=product_id)

    return render(request, 'checkout.html', {'product': product})

def purchase_summary(request, product_id):
    # Retrieve the product
    product = get_object_or_404(Product, product_id=product_id)

    # Get the delivery data from the session
    delivery_data = request.session.get('delivery_data')

    if not delivery_data:
        messages.error(request, "No delivery information found for this product.")
        return redirect('marketplace')  # Redirect to the marketplace if no delivery details are found

    # Deserialize the delivery data
    delivery = json.loads(delivery_data)

    # Pass data to the template
    return render(request, 'purchase-summary.html', {
        'product': product,
        'customer_name': delivery['customer_name'],
        'customer_email': delivery['customer_email'],
        'county': delivery['county'],
        'town': delivery['town'],
        'quantity': delivery['quantity'],
        'subtotal': delivery['subtotal'],
    })

def token(request):
    consumer_key = 'J1zAGl8atkQeOEOC0CQ6Qp6nkj2ORP4Yub8c2iUtybJ0NImz'
    consumer_secret = 'ho1BaRGGtyVdQFmS2bsk5RXrhrqfE2v9LrxG6NxAw0MHpo5GNpAQ9krnlo4i2QxH'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})


def pay(request, product_id):
    # Fetch the product (optional, but ensures valid ID)
    product = get_object_or_404(Product, product_id=product_id)

    # Get the delivery data from the session
    delivery_data = request.session.get('delivery_data')

    if not delivery_data:
        messages.error(request, "No delivery information found for this product.")
        return redirect('marketplace')  # Redirect to the marketplace if no delivery details are found

    # Deserialize the delivery data
    delivery = json.loads(delivery_data)

    # Pass the product and subtotal to the template
    context = {
        "product_id": product.product_id,  # You can pass the ID or full product object
        "product_name": product.name,  # Optional: additional product info
        "subtotal": delivery['subtotal'],  # Pass the subtotal here
    }

    return render(request, 'pay.html', context)

def stk(request, product_id):
    if request.method == "POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        # Assuming product_id is passed via GET or POST
        product_id = request.POST.get('product_id')  # Or request.GET['product_id']

        # Fetch the product and its related farmer's username
        product = get_object_or_404(Product, product_id=product_id)
        farmer_username = product.farmer.username  # Adjust to your field name

        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}

        # Prepare the STK request payload
        request = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": farmer_username,  # Use farmer's username here
            "TransactionDesc": f"Payment for {product.name}"
        }

        response = requests.post(api_url, json=request, headers=headers)
        return HttpResponse("Payment Request sent Successfully")

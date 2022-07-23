from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from numpy import product
from .utils import cookieCart,guestOrder
from .forms import *
import uuid
import json
import datetime
# Create your views here.

def registerPage(request):
    form = CreateUserForm()
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password1')
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        try:
            if User.objects.filter(username=username).first():
                messages.success(request, 'Username is taken.')
                return redirect('/register')

            elif User.objects.filter(email=email).first():
                messages.success(request, 'This Email is taken.')
                return redirect('/register')

            if form.is_valid():
                user_obj = User.objects.create(username =username,email=email)
                user_obj.set_password(password)
                user_obj.save()
                Customer.objects.create(
                    user = user_obj
                )
                messages.success(request,'Account was created for ' + username)
                user = authenticate(request,username=username, password=password)

                if user is not None:
                    login(request,user)
                    return redirect('/store')
                else:
                    messages.info(request,'Something went wrong!')

            return redirect('/store')
        
        except Exception as e:
            print(e)

    context = {'form':form}
    return render(request,'accounts/register.html',context)

def loginPage(request):
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('store')
        else:
            messages.info(request,'Username or Password is incorrect')
    context = {}
    return render(request,'accounts/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')



def viewAccount(request, pk = None):
    try:
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            cartItems = order.get_cart_items
        else:
            order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
    except:
        cartItems = 0
    if pk:
        user = User.objects.get(pk=pk)
    else:
        user = request.user
    args = {'cartItems':cartItems,'user':user}
    return render(request,'accounts/account.html',args)

def accountSettings(request):
    try:
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            cartItems = order.get_cart_items
        else:
            order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
    except:
        cartItems = 0

    customer = request.user.customer
    form = CustomerForm(instance=customer)

    form2 = UpdateProfileForm(instance=request.user)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        form2 = UpdateProfileForm(request.POST, instance=request.user)

        if (form and form2).is_valid():
            form.save()
            form2.save()
            return redirect('/account')
    context = {'form':form,'cartItems':cartItems,'form2':form2}
    return render(request,'accounts/account_settings.html',context)

def change_password(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect(reverse('accouns:view_profile'))
        else:
            return redirect(reverse('accounts:change_password'))
    else:
        form = PasswordChangeForm(user=request.user)

        args = {'cartItems':cartItems,'form': form}
        return render(request, 'accounts/change_password.html', args)

def store(request):
    total_products = Product.objects.all().count()
    latest_products = Product.objects.all()[:10]
    if total_products > 10:
        after_latest = Product.objects.all()[10:]
    else:
        after_latest = Product.objects.all()[:10]

    for i in latest_products:
        i.images = ProductImages.objects.filter(product = i)[:1]
        i.total_review = Review.objects.filter(product = i).count()
    
    for j in after_latest:
        j.images = ProductImages.objects.filter(product = j)[:1]
        j.total_review = Review.objects.filter(product = j).count()
    
    featured_products1 = Product.objects.filter(featured = 'True')[:1]
    featured_products2 = Product.objects.filter(featured = 'True')[1:2]
    featured_products3 = Product.objects.filter(featured = 'True')[2:3]

    for k in featured_products1:
        k.images = ProductImages.objects.filter(product = k)
        k.big_image = ProductImages.objects.filter(product = k)[:1]
        k.total_review = Review.objects.filter(product = k).count()
    
    for k in featured_products2:
        k.images = ProductImages.objects.filter(product = k)
        k.big_image = ProductImages.objects.filter(product = k)[:1]
        k.total_review = Review.objects.filter(product = k).count()
    
    for k in featured_products3:
        k.images = ProductImages.objects.filter(product = k)
        k.big_image = ProductImages.objects.filter(product = k)[:1]
        k.total_review = Review.objects.filter(product = k).count()
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
    
    reviews = Review.objects.all().order_by('-created_at')
    total_reviews = reviews.count()

    context = {
        'reviews':reviews,
        'total_reviews':total_reviews,
        'featured_products1':featured_products1,
        'featured_products2':featured_products2,
        'featured_products3':featured_products3,
        'after_latest':after_latest,
        'cartItems':cartItems,
        'latest_products':latest_products,
        'i.images':i.images,
        'i.total_review':i.total_review,
        'j.images':j.images,
        'j.total_review':j.total_review,
        'k.images':k.images,
        'k.big_image':k.big_image,
        'k.total_review':k.total_review,
    }
    return render(request, 'store/store.html',context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        for item in items:
            product = Product.objects.get(id = item.product.id)
            sizes = product.size.all()
            colors = product.color.all()
            item.image = ProductImages.objects.filter(product = product)[:1]
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
        for item in items:
            product = Product.objects.get(id = item.product.id)
            sizes = product.size.all()
            colors = product.color.all()
            item.image = ProductImages.objects.filter(product = product)[:1]
    context = {'items':items,'cartItems':cartItems,'order':order,'item.image':item.image,'sizes':sizes,'colors':colors}
    return render(request, 'store/cart.html',context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        for item in items:
            product = Product.objects.get(id = item.product.id)
            item.image = ProductImages.objects.filter(product = product)[:1]
        cartItems = order.get_cart_items
        delivery_charge = Delivery_charge.objects.all()
        for i in delivery_charge:
            chrge = i.fee
            discount = i.discount
        if order.get_cart_total < 500:
            delivery_chrg = float(chrge)
        elif order.get_cart_total >= 500 and order.get_cart_total < 1500:
            delivery_chrg = float(chrge-(chrge*(discount/100)))
        elif order.get_cart_total >= 1500:
            delivery_chrg = float(chrge-(chrge*((2*discount)/100)))

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
        for item in items:
            product = Product.objects.get(id = item.product.id)
            item.image = ProductImages.objects.filter(product = product)[:1]
        delivery_charge = Delivery_charge.objects.all()
        for i in delivery_charge:
            chrge = i.fee
            discount = i.discount
        if order['get_cart_total'] < 500:
            delivery_chrg = float(chrge)
        elif order['get_cart_total'] >= 500 and order['get_cart_total'] < 1500:
            delivery_chrg = float(chrge-(chrge*(discount/100)))
        elif order['get_cart_total'] >= 1500:
            delivery_chrg = float(chrge-(chrge*((2*discount)/100)))
    context = {'delivery_chrg':delivery_chrg,'items':items,'order':order,'cartItems':cartItems,'item.image':item.image}
    return render(request, 'store/checkout.html',context)



def updateItem(request):
    data = json.loads(request.body)
    productId = data['productID']
    action = data['action']
    color = data['color']
    size = data['size']
    print(color,size)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(customer=customer, order=order, product=product, status='Pending')

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    elif action == 'delete':
        orderItem.quantity = 0
    
    elif action == 'color':
        orderItem.color = color
    
    elif action == 'size':
        orderItem.size = size
            
    orderItem.save()

    if orderItem.quantity <= 0:
                orderItem.delete()
    

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        email = request.user.email
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        

    else:
        customer,order = guestOrder(request,data)
                
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
        delivery_charge = Delivery_charge.objects.all()
        for i in delivery_charge:
            chrge = i.fee
            discount = i.discount
        if total < 500:
            delivery_chrg = float(chrge)
        elif total >= 500 and total < 1500:
            delivery_chrg = float(chrge-(chrge*(discount/100)))
        elif total >= 1500:
            delivery_chrg = float(chrge-(chrge*((2*discount)/100)))
        
        order.delivery_fee = delivery_chrg
        order.total = total + delivery_chrg
    order.save()
    
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
        )
        
    return JsonResponse('Order completed!', safe=False)

def productView(request,pk,*args,**kwargs):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']
    c_for = kwargs.pop('c_for')
    category = Category.objects.get(id = kwargs.pop('category') )
    product = Product.objects.get(id = pk)
    images = ProductImages.objects.filter(product = product)
    big_image = ProductImages.objects.filter(product = product)[:1]
    demo_price = product.price + product.discount_amount

    review = product.review_set.all().order_by('-created_at')
    total_review = review.count()
    total_rate = 0
    for i in review:
        total_rate += i.rate
    try:
        avg_rating = total_rate/total_review
        product.rate = avg_rating
        product.save()
    except:
        avg_rating = 0
        product.rate = avg_rating
        product.save()
    form = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        form.save()
        messages.success(request, 'Review Added')
        return redirect(reverse('view', kwargs={'pk':pk}))
    
    else:
        form = ReviewForm()

    stock = product.stock
    context = {'c_for':c_for,'category':category,'images':images,'big_image':big_image,'demo_price':demo_price,'stock':stock,'avg_rating':avg_rating,'review':review,'total_review':total_review,
    'form':form,'product':product,'cartItems':cartItems}
    return render(request, "store/view.html",context)

def deleteReview(request, pk):
    review = Review.objects.get(id=pk)
    if request.method == "POST":
        review.delete()
        return redirect('/')

    context = {'item':review}
    return render(request,'store/delete.html',context)

def categoryView(request,*args,**kwargs):
    products = Product.objects.filter(*args,**kwargs)
    categorys = Category.objects.all()
    c_for = kwargs.pop('c_for')
    
    for i in categorys:
        i.products = products.filter(category = i)
        for j in i.products:
            j.images = ProductImages.objects.filter(product = j)[:1]
            j.total_review = Review.objects.filter(product = j).count()

    context = {
        'c_for':c_for,
        'categorys':categorys,
        'i.products':i.products,
        'j.images':j.images,
        'j.total_review':j.total_review
        }
    return render(request, "store/categoryview.html",context)

def insideCategory(request,*args,**kwargs):
    category = Category.objects.get(id = kwargs.pop('category'))
    products = Product.objects.filter(*args,**kwargs)
    number = 0
    c_for = kwargs.pop('c_for')
    
    for i in products:
        i.images = ProductImages.objects.filter(product = i)
        i.big_image = ProductImages.objects.filter(product = i)[:1]
        i.total_review = Review.objects.filter(product = i).count()
        i.no = number + 1

    context = {
        'c_for':c_for,
        'category':category,
        'products':products,
        'i.images':i.images,
        'i.big_image':i.big_image,
        'i.total_review':i.total_review,
        'i.no':i.no,
    }
    return render(request, "store/insidecategory.html",context)
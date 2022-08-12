from multiprocessing import context
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticted_user, allowed_users,shopowner_only
from .utils import cookieCart,guestOrder
from .forms import *
from .filters import *
import uuid
import json
import datetime
from django.utils import timezone
from datetime import timedelta
# Create your views here.

@unauthenticted_user
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
                auth_token=str(uuid.uuid4())
                profile_obj = UserProfile.objects.create(user = user_obj,auth_token=auth_token)
                profile_obj.save()
                group = Group.objects.get(name = 'customer')
                user_obj.groups.add(group)
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

@unauthenticted_user
def shopOwnerRegisterPage(request):
    form = CreateUserForm()
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password1')
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        try:
            if User.objects.filter(username=username).first():
                messages.success(request, 'Username is taken.')
                return redirect('/shopregister')

            elif User.objects.filter(email=email).first():
                messages.success(request, 'This Email is taken.')
                return redirect('/shopregister')

            if form.is_valid():
                user_obj = User.objects.create(username =username,email=email,is_staff = True)
                user_obj.set_password(password)
                user_obj.save()
                auth_token=str(uuid.uuid4())
                profile_obj = UserProfile.objects.create(user = user_obj,auth_token=auth_token)
                profile_obj.save()
                group = Group.objects.get(name = 'shopowner')
                user_obj.groups.add(group)
                ShopOwner.objects.create(
                    user = user_obj
                )
                messages.success(request,'Account was created for ' + username)
                return redirect('/token')
        
        except Exception as e:
            print(e)

    context = {'form':form}
    return render(request,'accounts/shopregister.html',context)

@unauthenticted_user
def loginPage(request):
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username=username, password=password)

        if user is not None:
            login(request,user)
            group = request.user.groups.all()[0].name
            if group == 'customer':
                return redirect('store:store')
            else :
                return redirect('store:home')
        else:
            messages.info(request,'Username or Password is incorrect')
    context = {}
    return render(request,'accounts/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('store:login')

@login_required(login_url='login')
def viewAccount(request, pk = None):
    try:
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            cartItems = order.get_cart_items
        else:
            cookieData = cookieCart(request)
            cartItems = cookieData['cartItems']
    except:
        cartItems = 0
    if pk:
        user = User.objects.get(pk=pk)
    else:
        user = request.user
    print(user)
    args = {'cartItems':cartItems,'user':user}
    return render(request,'accounts/account.html',args)

@login_required(login_url='login')
def accountSettings(request):
    try:
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            cartItems = order.get_cart_items
        else:
            cookieData = cookieCart(request)
            cartItems = cookieData['cartItems']

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
    except:
        cartItems = 0

        shopowner = request.user.shopowner
        form = ShopOwnerForm(instance=shopowner)

        form2 = UpdateProfileForm(instance=request.user)
        if request.method == 'POST':
            form = ShopOwnerForm(request.POST, request.FILES, instance=shopowner)
            form2 = UpdateProfileForm(request.POST, instance=request.user)

            if (form and form2).is_valid():
                form.save()
                form2.save()
                return redirect('/account')
    
    context = {'form':form,'cartItems':cartItems,'form2':form2}
    return render(request,'accounts/account_settings.html',context)

@login_required(login_url='login')
def change_password(request):
    try:
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            cartItems = order.get_cart_items
        else:
            cookieData = cookieCart(request)
            cartItems = cookieData['cartItems']
            
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
    except:
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

        args = {'form': form}
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

def products(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    

    products = Product.objects.all().order_by('-discount_amount','-discount','-stock','-date_created')
    categorys = Category.objects.all()
    
    for i in categorys:
        i.products = products.filter(category = i)
        
        for j in i.products:
            i.products.c_for = j.c_for
            j.images = ProductImages.objects.filter(product = j)[:1]
            j.total_review = Review.objects.filter(product = j).count()

    
    product_week = Product.objects.filter(date_created__gt=(datetime.datetime.now()- timedelta(days=7))).order_by('-date_created')
    top_reviewed = Product.objects.all().order_by('-rate')

    context = {
        'i.products.c_for':i.products.c_for,
        'categorys':categorys,
        'i.products':i.products,
        'j.images':j.images,
        'j.total_review':j.total_review,
        'top_reviewed':top_reviewed,
        'product_week':product_week,
        'cartItems':cartItems
        }
    return render(request, "store/products.html",context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
        items = order.orderitem_set.all()
        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                sizes = product.size.all()
                colors = product.color.all()
                item.image = ProductImages.objects.filter(product = product)[:1]

        
            context = {
                'items':items,
                'cartItems':cartItems,
                'order':order,
                'item.image':item.image,
                'sizes':sizes,
                'colors':colors
            }
        else:
            context = {
                'items':items,
                'cartItems':cartItems,
                'order':order,
            }

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
        print(items)
        for item in items:
            product = Product.objects.get(id = item['product']['id'])
            sizes = product.size.all()
            colors = product.color.all()
            item['image'] = ProductImages.objects.filter(product = product)[:1]
        context = {
            'items':items,
            'cartItems':cartItems,
            'order':order,
            'item.image':item['image'],
            'sizes':sizes,
            'colors':colors
            }
    return render(request, 'store/cart.html',context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
        items = order.orderitem_set.all()
        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                item.image = ProductImages.objects.filter(product = product)[:1]
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

            context = {
                'delivery_chrg':delivery_chrg,
                'items':items,
                'order':order,
                'cartItems':cartItems,
                'item.image':item.image
            }
        else:
            context = {
                'items':items,
                'order':order,
                'cartItems':cartItems,
            }

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
        for item in items:
            product = Product.objects.get(id = item['product']['id'])
            item['image'] = ProductImages.objects.filter(product = product)[:1]
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

        context = {
            'delivery_chrg':delivery_chrg,
            'items':items,
            'order':order,
            'cartItems':cartItems,
            'item.image':item['image']
            }
    return render(request, 'store/checkout.html',context)



def updateItem(request):
    data = json.loads(request.body)
    productId = data['productID']
    action = data['action']
    color = data['color']
    size = data['size']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    shopowner = product.shopowner
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order.shop.add(shopowner)

    orderItem, created = OrderItem.objects.get_or_create(customer=customer, order=order,shop=shopowner,  product=product, status='Pending')
    orderItem.rate = product.price

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
    
    orderItem.total = (orderItem.quantity * product.price)
            
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
        
        order.delivery_fee = chrge
        order.total = total + chrge
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

def productView(request,pk):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
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
        return redirect(reverse('store:view', kwargs={'pk':pk}))
    
    else:
        form = ReviewForm()

    stock = product.stock
    context = {'images':images,'big_image':big_image,'demo_price':demo_price,'stock':stock,'avg_rating':avg_rating,'review':review,'total_review':total_review,
    'form':form,'product':product,'cartItems':cartItems}
    return render(request, "store/view.html",context)

def deleteReview(request, pk):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    
    review = Review.objects.get(id=pk)
    if request.method == "POST":
        review.delete()
        return redirect('/')

    context = {'item':review,'cartItems':cartItems}
    return render(request,'store/delete.html',context)

def categoryView(request,*args,**kwargs):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

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
        'j.total_review':j.total_review,
        'cartItems':cartItems
        }
    return render(request, "store/categoryview.html",context)

def insideCategory(request,*args,**kwargs):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

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
        'cartItems':cartItems
    }
    return render(request, "store/insidecategory.html",context)

def shops(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

    shopowner = ShopOwner.objects.all()

    context = {'shopowner':shopowner,'cartItems':cartItems}
    return render(request,'store/shops.html',context)

def view_shops(request,pk):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

    shop = ShopOwner.objects.get(id=pk)
    products = Product.objects.filter(shopowner=shop)
    product_week = products.filter(date_created__gt=(datetime.datetime.now()- timedelta(days=7))).order_by('-date_created')
    top_reviewed = products.order_by('-rate')

    categorys = Category.objects.all()
    
    for i in categorys:
        i.products = products.filter(category = i)
        
        for j in i.products:
            i.products.c_for = j.c_for
            j.images = ProductImages.objects.filter(product = j)[:1]
            j.total_review = Review.objects.filter(product = j).count()

    context = {
        'shop':shop,
        'i.products.c_for':i.products.c_for,
        'categorys':categorys,
        'i.products':i.products,
        'j.images':j.images,
        'j.total_review':j.total_review,
        'top_reviewed':top_reviewed,
        'product_week':product_week,
        'cartItems':cartItems
        }
    return render(request,'store/view_shop.html',context)

@login_required(login_url='login')
def userDashboard(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
    
    orders = Order.objects.filter(customer = request.user.customer,complete = True).order_by('-date_added')

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    myFilter = OrderFilter(request.GET,queryset=orders)
    orders = myFilter.qs

    context = {
        'cartItems':cartItems,
        'orders':orders,
        'total_orders':total_orders,
        'delivered':delivered,
        'pending':pending,
        'myFilter':myFilter
    }
    return render(request, 'store/user-dashboard.html',context)

@login_required(login_url='login')
def viewOrder(request,pk):
    order_y = Order.objects.get(id = pk)
    shop = order_y.shop
    orders = OrderItem.objects.filter(order = order_y)
    address = ShippingAddress.objects.get(order=order_y)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

    context = {'order':order_y,'orders':orders,'address':address,'cartItems':cartItems,'shop':shop}
    return render(request,'store/view_order.html',context)

@login_required(login_url='login')
@shopowner_only
@allowed_users(allowed_roles=['shopowner'])
def updateOrder(request,pk):
    total = 0
    paid = 0
    due = 0
    order_y = Order.objects.get(id = pk)
    o_advance = order_y.advance
    print(o_advance)
    shop = request.user.shopowner
    orders = OrderItem.objects.filter(order = order_y, shop =shop)
    for i in orders:
        total += float(i.total)
        paid = i.advance

    delivery_charge = Delivery_charge.objects.all()
    for i in delivery_charge:
        chrge = i.fee
        discount = i.discount
    
    total += chrge
    
    due = float(total) - float(paid)

    form = UpdateOrderForm(instance=order_y)
    if request.method =='POST':
        form = UpdateOrderForm(request.POST,instance=order_y)
        advance = request.POST.get('advance')
        status = request.POST.get('status')
        if form.is_valid():
            order_y.status = status
            o_advance += float(advance)
            order_y.advance = o_advance
            order_y.due = order_y.total - float(order_y.advance)
            order_y.save()
            for j in orders:
                j.advance += float(advance)
                j.save()
            if order_y.status == 'Delivered':
                for i in orders:
                    i.product.stock -= 1
                    i.product.save()
            
            elif order_y.status == 'Take':
                order_y.taken_user = request.user
                order_y.save()
                return redirect('/track_order')

        return redirect(reverse('store:update_order', kwargs={'pk':pk}))
    if order_y.customer:
        address = ShippingAddress.objects.get(order=order_y)
        context = {'total':total,'due':due,'paid':paid,'order':order_y,'orders':orders,'address':address,'shop':shop,'form':form,}
    else:
        context = {'order':order_y,'orders':orders,'shop':shop,'form':form,}

    return render(request,'shop/update_order.html',context)

@login_required(login_url='login')
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    action = 'delete_order'
    if request.method == "POST":
        order.delete()
        return redirect('/totalOrders')

    context = {'item':order,'action':action}
    return render(request,'store/delete.html',context)

@login_required(login_url='login')
@shopowner_only
def home(request):
    shopowner = request.user.shopowner
    order = Order.objects.filter(complete=True, shop=shopowner)
    orders = Order.objects.filter(complete=True, shop=shopowner,status='Pending').order_by('-date_created')
    total_orders = order.count()
    delivered = order.filter(status='Delivered').count()
    pending = order.filter(status='Pending').count()

    context = {'orders':orders,'total_orders':total_orders,
    'delivered':delivered,'pending':pending
    }

    return render(request,'shop/dashboard.html',context)

@login_required(login_url='login')
@shopowner_only
def offlineOrder(request):
    shop = request.user.shopowner
    products = Product.objects.filter(shopowner=shop)
    total_products = products.count()
    if total_products <= 0:
        return redirect('store:home')

    
    if request.method == 'POST' and 'product' in request.POST:
        item = request.POST.get('product')
        quantity = request.POST.get('quantity')
        product = Product.objects.get(id = item)
        order, created = Order.objects.get_or_create( complete=False)
        order.shop.add(shop)
        orderItem, created = OrderItem.objects.get_or_create( order=order,shop=shop,  product=product, status='pending')
        orderItem.quantity = quantity

        orderItem.rate = product.price
        orderItem.total = int(orderItem.quantity) * product.price

        order.save()

        orderItem.save()
        return redirect('store:offline-order')   
    
    if request.method == 'POST' and 'save' in request.POST:
        order_x = Order.objects.get(shop=shop, complete=False)
        order_x.complete = True
        order_x.status = "Delivered"
        order_x.save()
        orderItem_x = OrderItem.objects.filter(order = order_x)
        for i in orderItem_x:
            i.status = "Delivered"
            i.product.stock -= 1
            i.product.save()
            i.save()
        return redirect('store:memo-print', pk=order_x.id)
    
    if request.method == 'POST' and 'amount' in request.POST:
        amount = request.POST.get('amount')
        order_z = Order.objects.get(shop=shop, complete=False)
        order_z.advance = float(amount)
        order_z.due = float(order_z.total) - float(order_z.advance)
        order_z.save()
    
    order_check = Order.objects.filter(shop=shop, complete=False).count()
    if order_check == 0:
        context ={
            'shop':shop,
            'products':products,
        }
    else:
        order_y = Order.objects.get(shop=shop, complete=False)
        orders = OrderItem.objects.filter(order = order_y)
        total = 0
        for i in orders:
            total += i.total
            order_y.total = total
            order_y.due = total - float(order_y.advance)
            order_y.save()
    


        context ={
            'order':order_y,
            'orders':orders,
            'shop':shop,
            'products':products,
        }
    return render(request,'shop/offlineOrder.html',context)


@login_required(login_url='login')
@shopowner_only
def memoPrint(request,pk):
    order_y = Order.objects.get(id = pk)
    shop = order_y.shop
    orders = OrderItem.objects.filter(order = order_y)
    address_check  = ShippingAddress.objects.filter(order=order_y).count()
    if address_check >0 :
        address = ShippingAddress.objects.get(order=order_y)
        context ={
            'order':order_y,'orders':orders,'address':address,'shop':shop,
        }
    else:
         context ={
            'order':order_y,'orders':orders,'shop':shop,
        }
    return render(request,'shop/memoPrint.html',context)


@login_required(login_url='login')
@shopowner_only
def addProducts(request):
    shopowner = request.user.shopowner
    form = ProductForm()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        images = request.FILES.getlist('images')
        total_images = len(images)
        if total_images > 3:
            messages.info(request,'You cannot upload more than 3 images!')
            return redirect('store:add-product')
        category = request.POST.getlist('category')
        color = request.POST.getlist('color')
        size = request.POST.getlist('size')
        stock = request.POST.get('stock')
        description = request.POST.get('description')

        product = Product.objects.create(
            shopowner = shopowner,
            name = name,
            price = price,
            stock = stock,
            description = description
        )
        for i in category:
            product.category.add(i)
        for i in color:
            product.color.add(i)
        for i in size:
            product.size.add(i)
        for i in images:
            image = ProductImages.objects.create( product = product, img= i)
        
        product.save()
        
        
        messages.success(request,'Product added ..')
            
        return redirect('store:add-product')
            

    context ={'form':form}
    return render(request,'shop/addProducts.html',context)

@login_required(login_url='login')
@shopowner_only
def shopProducts(request):
    shopowner = request.user.shopowner
    products = Product.objects.filter(shopowner = shopowner)

    context={
        'products':products
    }
    return render(request,'shop/products.html',context)


@login_required(login_url='login')
def totalOrders(request):
    try:
        user = request.user.customer
        orders = Order.objects.filter(complete=True, customer=user).order_by('-date_created')
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            cartItems = order.get_cart_items
        else:
            cookieData = cookieCart(request)
            cartItems = cookieData['cartItems']
    except:
        user = request.user.shopowner
        orders = Order.objects.filter(complete=True, shop=user).order_by('-date_created')
        cartItems = 0

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    myFilter = OrderFilter(request.GET,queryset=orders)
    orders = myFilter.qs

    context = {
        'orders':orders,
        'total_orders':total_orders,
        'delivered':delivered,
        'pending':pending,
        'myFilter':myFilter,
        'cartItems':cartItems,

    }
    return render(request,'totalOrders.html',context)

@login_required(login_url='login')
@shopowner_only
@allowed_users(allowed_roles=['shopowner'])
def addColors(request):
    form = ColorForm()
    if request.method == "POST":
        form =  ColorForm(request.POST)
        if form.is_valid:
            form.save()
        else:
            form = ColorForm()

        return redirect('store:shop-product')
    
    context = {
        'form':form
    }
    return render(request,'shop/addColors.html',context)


@login_required(login_url='login')
@shopowner_only
@allowed_users(allowed_roles=['shopowner'])
def shopProductView(request,pk):
    product = Product.objects.get(id = pk)
    demo_price = float(product.price) + float(product.discount_amount)
    category = product.category.all()
    size = product.size.all()
    color = product.color.all()
    images = ProductImages.objects.filter(product=product)
    big_image = ProductImages.objects.filter(product = product)[:1]
    if request.method == 'POST' and 'stock' in request.POST:
        stock =  request.POST.get('stock')
        product.stock += int(stock)
        product.save()
        return redirect(reverse('store:shop-product-view', kwargs={'pk':pk}))

    if request.method == 'POST' and 'discount' in request.POST:
        if product.discount > 0:
            return redirect(reverse('store:shop-product-view', kwargs={'pk':pk}))
        discount =  int(request.POST.get('discount'))
        discount_amount = product.price * (discount/100)
        product.price -= discount_amount
        product.discount = discount
        product.discount_amount = discount_amount
        product.save()
        return redirect(reverse('store:shop-product-view', kwargs={'pk':pk}))

    if request.method == 'POST' and 'discount_amount' in request.POST:
        product.price += product.discount_amount
        product.discount = 0
        product.discount_amount = 0
        product.save()
        return redirect(reverse('store:shop-product-view', kwargs={'pk':pk}))

    context ={
        'demo_price':demo_price,
        'size':size,
        'color':color,
        'category':category,
        'product':product,
        'images':images,
        'big_image':big_image
    }
    return render(request,'shop/productView.html',context)


@login_required(login_url='login')
@shopowner_only
@allowed_users(allowed_roles=['shopowner'])
def shopProductEdit(request,pk):
    product = Product.objects.get(id = pk)
    images = ProductImages.objects.filter(product = product)
    total_images = images.count()
    form = ProductForm(instance=product)
    if request.method == "POST" and 'name' in request.POST:
        form = ProductForm(request.POST,instance=product)
        if form.is_valid():
            form.save()
            product.shopowner = request.user.shopowner
            product.quantity = ""
            product.save()
            return redirect(reverse('store:shop-product-view', kwargs={'pk':pk}))
        else:
            print(form.errors)
            form = ProductForm(instance=product)
    
    if request.method == "POST" and 'remove' in request.POST:
        for i in images:
            i.delete()
        return redirect(reverse('store:shop-product-edit', kwargs={'pk':pk}))
    
    
    if request.method == "POST" and 'images' in request.POST:
        images =  request.POST.getlist('images')
        total_img = len(images)
        in_total = int(total_images) + int(total_img)
        if in_total > 3:
            return redirect(reverse('store:shop-product-edit', kwargs={'pk':pk}))
        else:
            for i in images:
                images = ProductImages.objects.create(product = product,img=i)
        
        return redirect(reverse('store:shop-product-edit', kwargs={'pk':pk}))
        

    if total_images > 0: 
        big_image = ProductImages.objects.filter(product = product)[:1]
        context= {
            'total_images':total_images,
            'big_image':big_image,
            'product':product,
            'images':images,
            'form':form
        }
    
    else:
        context= {
            'product':product,
            'form':form
        }
    return render(request,'shop/productEdit.html',context)
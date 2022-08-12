import json
import uuid
from .models import *
from django.contrib.auth import login
from django.contrib.auth.models import Group

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except: 
        cart = {}
    items = []
    order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
    cartItems = order['get_cart_items']
    
    for i in cart :
        try:
            cartItems += cart[i]["quantity"]
            
            product = Product.objects.get(id = i)
            total = (product.price * cart[i]['quantity'])
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']
            
            item = {
                'product' : {
                    'id' : product.id,
                    'name': product.name,
                    'price': product.price,
                },
                'quantity' : cart[i]["quantity"],
                'get_total': total,
                'color' : cart[i]['color'],
                'size' : cart[i]['size'],
            }
            
            items.append(item)
            if product.digital == False:
                order['shipping'] = True
    
        except:
            pass
    
    return {"cartItems":cartItems,"order":order,"items":items}

def guestOrder(request,data):
    name = data['form']['name']
    phone = data['form']['phone']
    
    cookieData = cookieCart(request)
    items = cookieData['items']
    
    customer, created = Customer.objects.get_or_create(
        phone = phone,
    )
    if created:
        username = phone
        user = User.objects.create(username= username,first_name = name)
        customer.user = user
        customer.save()
        auth_token=str(uuid.uuid4())
        profile_obj = UserProfile.objects.create(user = user,auth_token=auth_token)
        profile_obj.save()
        group = Group.objects.get(name = 'customer')
        user.groups.add(group)
        login(request,user)
    else:
        user = customer.user
        login(request,user)

    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        shopowner = product.shopowner
        order, created = Order.objects.get_or_create(customer=customer,shop=shopowner, complete=False)
        
        orderItem = OrderItem.objects.get_or_create(
            product=product,
            order = order,
            shop=shopowner,
            quantity = item['quantity']
            )
    return customer,order
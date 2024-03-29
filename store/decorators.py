from django.http import HttpResponse
from django.shortcuts import redirect,render

def unauthenticted_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('store:home')
        else:
            return view_func(request, *args, **kwargs) 
    
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return render(request,'authorizeResponse.html')
        return wrapper_func
    return decorator

def shopowner_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        if group == 'customer':
            return redirect('store:store')
        if group == 'shopowner':
            return view_func(request, *args, **kwargs)
    
    return wrapper_function
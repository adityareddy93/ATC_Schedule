from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect

def userauthentication(user_func):
    def wrapper(request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return user_func(request,*args,**kwargs)
    return wrapper

def allowed_users(allowed_roles=[]):
    def decorator(user_func):
        def wrapper(request,*args,**kwargs):
            group=None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                print('working',allowed_roles)
                return user_func(request,*args,**kwargs)
            else:
                return render(request,'unauthorized_user.html',{})
        return wrapper
    return decorator
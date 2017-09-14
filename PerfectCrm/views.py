from django.shortcuts import render,redirect,HttpResponse

#login用于用户登录认证，logout用于用户注销，authenticate用于验证用户输入的账号密码是否有效
from django.contrib.auth import login,logout,authenticate

#用于给法添加认证装饰器
from django.contrib.auth.decorators import login_required
# Create your views here.

from django.urls import reverse
def access_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        #其实这个方法就是云UserProfile认证类中进行数据的认证,认证成功则返回一个UserProfile对象，否则返回为空
        user = authenticate(request,email=email,password=password)
        if user:
            #Post提交数据也可以有Get提交的数据
            login(request,user)
            next_url = request.GET.get("next","/crm/")
            return redirect(next_url)

    return render(request,"login.html")

def access_logout(request):
    if request.method == "GET":
        logout(request)
        return redirect("/account/login/")
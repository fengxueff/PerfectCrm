#!/usr/bin/env python3
#-*- coding:utf-8 -*-
'''

'''
__author__ = "wpxiao"
from crm.permissions import perm_list
from django.core.urlresolvers import resolve
from django.shortcuts import HttpResponse,redirect

def check_permission(func):

    def wrapper(*args,**kwargs):
        print("----------------permission-------------")
        check_flag = perm_check(*args,**kwargs)
        if check_flag:
            return func(*args,**kwargs)
        else:
            return HttpResponse("没有权限访问")

    return wrapper

def perm_check(*args,**kwargs):
    request = args[0]
    perm_dict = perm_list.perm_dict
    #判定用户是否已登录
    if request.user.is_authenticated():
        for perm_name,value in perm_dict.items():
            # 第一步：进行url判定
            url_matched = False
            if value["url_type"] == 1:#绝对
                if request.path == value["url"]:
                    url_matched = True
            else:#相对
                #将请求的绝对路径转转化为urls.py中的别名
                url_alias = resolve(request.path)
                if url_alias.url_name == value["url"]:
                    url_matched = True

            #第二步：进行请求方法判定
            method_matched = False
            if value["method"] == request.method:
                   method_matched = True

            #第三步： 进行请求参数判定
            args_matched = True
            request_method_func = getattr(request,request.method)
            for arg in value["args"]:
                if not request_method_func.get(arg):
                    args_matched = False

            #如果前三步判定都为True,仅表示当前访问的页面参数与权限字典中定义的页面参数一致
            if url_matched and method_matched and args_matched:
                #判定用户自己的权限表里面是否有这一条权限，如果有就返回为真
                if request.user.has_perm("perm_name"):
                    return True
    else:
        return redirect("/account/login/")






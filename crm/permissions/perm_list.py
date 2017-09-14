#!/usr/bin/env python3
#-*- coding:utf-8 -*-
'''
    定义权限字典
    url_type 0为相对（基于正则表达式的白名单），1为绝对（基于具体url的白名单）
    注：如果是相对的，那权限装饰器会影响到views中指定的函数，而如果是绝对的那仅会影响到这一个url，而不会影响到正则表达式匹配的其他路径
    如：url(r"^(\w+)/(\w+)/$",views.display_table_objs,name="table_objs")
        而如果在下面写访问客户库时url使用相对的话，那就不光会影响到/king_admin/crm/customer/，还会影响到/king_admin/crm/[其他表]/
    上述逻辑其实和permssion.py中的对url判定代码有关
'''
__author__ = "wpxiao"

perm_dict = {
    #访问我的课程
    "crm.can_access_my_class":{
        "url_type":0,
        "url":"my_class", #urls.py中的name
        "method":"GET",
        "args":[]
    },
    #访问客户库
    "crm.can_access_customer_list":{
        "url_type":1,
        "url":"/king_admin/crm/customer/",
        "method":"GET",
        "args":[]
    },
    #访问客户详情
    "crm.can_access_customer_detail":{
        "url_type": 0,
        "url": "change_table_obj",  # urls.py中的name
        "method": "GET",
        "args": []
    },
     #修改客户详情
    "crm.can_change_customer_detail": {
        "url_type": 0,
        "url": "change_table_obj",  # urls.py中的name
        "method": "POST",
        "args": []
    },
}
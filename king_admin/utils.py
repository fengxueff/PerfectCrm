#!/usr/bin/env python3
#-*- coding:utf-8 -*-
'''

'''
__author__ = "wpxiao"

def search_filter(request):
    filters = {}
    for key,value in request.GET.items():
        if key == "page" or key=="o" or key=="search_text" or key=="show_all":
            pass
        else:
            if value:
                filters[key] = value
    return filters

def table_order(request,contact_list):
    order_key = request.GET.get("o")
    order_key_dict = {}
    if order_key:
        if order_key.startswith("-"):
            order_key = order_key.strip("-")
            contact_list = contact_list.order_by(order_key)
            order_key_dict[order_key] = order_key
        else:
            order_key = "-" + order_key
            contact_list = contact_list.order_by(order_key)
            order_key_dict[request.GET.get("o")] = order_key

    return contact_list,order_key_dict

from django.db.models import Q
def table_search(request,contact_list,admin_class):
    search_key = request.GET.get("search_text")
    if search_key:
        q_obj = Q()
        q_obj.connector = "OR"
        #多个字段的动态查询
        for column in admin_class.search_field:
            q_obj.children.append(("%s__contains"%column,search_key))

        search_result = contact_list.filter(q_obj)
        print(contact_list.filter(q_obj).query)
        return search_result
    else:
        return contact_list

def build_delete_obj_content_show(obj):
    many_to_one_list = obj._meta.related_objects
    many_to_many_list =  obj._meta.local_many_to_many
    table_name = obj._meta.verbose_name_plural
    ul_ele = "<ul>"
    
    li_ele = """<li><b>{table_name}</b>:<a href='../{tablename}/{url}/change'>{obj}</a></li>""".format(table_name=table_name,tablename=obj._meta.model_name,obj=obj,url=obj.id)
    ul_ele =ul_ele+li_ele
    #对象对应的所有正向多对多关系的字段
    for m2m_field in many_to_many_list:
        #获取反向查询的关键字：
        field_name = m2m_field.name
        #通过反射获取反向查询的queryset
        back_query_queryset = getattr(obj,field_name).all()
        ul_ele += "<ul>"


        for back_query in back_query_queryset:
            li_ele = """<li>{table_name}-relationship:{obj}</li>""".\
                format(table_name=back_query._meta.verbose_name_plural,tablename=back_query._meta.model_name, obj=back_query,url=back_query.id)

            print("bakck_query:",back_query)
            ul_ele += li_ele
        ul_ele += "</ul>"
    # if len(many_to_many_list)>0:
    #     ul_ele = "<ul>"+ul_ele+"</ul>"

    #对象对应的所有多对一关系列表(包含了反向的多对多关系)
    for many_to_one in many_to_one_list:
        # 当是反身多对多时，只循环第一层，不做递归查询
        if "ManyToManyRel" in many_to_one.__repr__():
            # 获取反向查询的关键字：如enrollment_set
            back_query_key = many_to_one.get_accessor_name()
            # 通过反射获取反向查询的queryset
            back_query_queryset = getattr(obj, back_query_key).all()
            ul_ele += "<ul>"
            for back_query in back_query_queryset:
                nodes = """<li>{table_name}:<a href='../{tablename}/{url}/change'>{obj}</a></li>""". \
                    format(table_name=back_query._meta.verbose_name_plural, tablename=back_query._meta.model_name,
                           obj=back_query, url=back_query.id)
                ul_ele +=nodes
            ul_ele +="</ul>"

        else:
            #获取反向查询的关键字：如enrollment_set
            back_query_key = many_to_one.get_accessor_name()
            #通过反射获取反向查询的queryset
            back_query_queryset = getattr(obj,back_query_key).all()

            for back_query in back_query_queryset:
                nodes =build_delete_obj_content_show(back_query)
                ul_ele += nodes
    ul_ele = ul_ele+"</ul>"
    print(ul_ele)
    return ul_ele
from django.shortcuts import render,redirect,HttpResponse

# Create your views here.
from king_admin import king_admin
#用于给第一个方法添加认证装饰器
from django.contrib.auth.decorators import login_required
from crm.permissions import permission
@login_required
def index(request):
    # ##print(king_admin.enable_admin["crm"]["customer"].model)
    return render(request,"king_admin/index.html",{"table_list":king_admin.enable_admin})
def app_index(request,app_name):
    return redirect("/king_admin/")

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from king_admin import utils
# @login_required
@permission.check_permission
def display_table_objs(request,app_name,table_name):
    admin_class = king_admin.enable_admin[app_name][table_name]
    #用于自定义操作的Post提交
    if request.method == "POST":
        select_action = request.POST.get("select_action")

        if request.POST.get("ids") and select_action:
            if request.POST.get("ids") == "__all__":
                querysets = admin_class.model.objects.all()
            else:
                id_list = request.POST.get("ids").split(",")
                querysets = admin_class.model.objects.filter(id__in=id_list)
            for index,func_name in enumerate(admin_class.actions.values()):
                if index == int(select_action):
                    func = getattr(admin_class,func_name)
                    return func(admin_class,request,querysets)
        return redirect(".")

    table_objs = king_admin.enable_admin[app_name][table_name].list_display
    table_filter = king_admin.enable_admin[app_name][table_name].list_filter
    # table_data = king_admin.enable_admin[app_name][table_name].model.objects.all().values_list(*table_objs)
    # table_name =  king_admin.enable_admin[app_name][table_name].model._meta.verbose_name_plural
    selected_filters = utils.search_filter(request)
    #过滤
    contact_list = admin_class.model.objects.filter(**selected_filters)
    #搜索
    contact_list = utils.table_search(request,contact_list,admin_class)
    #排序
    contact_list,order_key_dict = utils.table_order(request,contact_list)
    if "show_all" in request.GET.keys():
        paginator = Paginator(contact_list, len(contact_list))
    else:
        paginator = Paginator(contact_list, admin_class.list_per_page)  # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        query_sets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        query_sets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        query_sets = paginator.page(paginator.num_pages)
    return render(request,"king_admin/table_objs.html",{
                                                        "app_name":app_name,
                                                        "table_name":table_name,
                                                        "table_title":table_objs,
                                                        "table_filter":table_filter,
                                                        "selected_filters":selected_filters,
                                                        "paginator":paginator,
                                                        "query_sets":query_sets,
                                                        "order_key_dict":order_key_dict,
                                                        "admin_class":admin_class})

#数据修改
from king_admin.forms import create_model_form
import json
@login_required
def change_table_obj(request,app_name,table_name,selected_id):
    admin_class = king_admin.enable_admin[app_name][table_name]
    obj = admin_class.model.objects.filter(id=int(selected_id)).first()
    admin_class.modify_flag = True
    model_form_class = create_model_form(request,admin_class)
    if request.method == "POST":
        #ModelForm的页面数据修改功能,将数据与modelform进行绑定
        model_form_obj = model_form_class(request.POST,instance=obj)
        if model_form_obj.is_valid():
            model_form_obj.save()
            #print(model_form_obj)
            #当数据修改完成后，直接跳转到点击修改前的页面
            return redirect("../../?page=%s"%request.POST.get("page"))
    else:
        model_form_obj = model_form_class(instance=obj)
    ##print(json.dumps(model_form_obj.errors))
    #print(model_form_obj.errors)
    return render(request, "king_admin/change_table_obj.html", {
        "model_form_obj":model_form_obj, "admin_class":admin_class

    })

#数据添加
@login_required
def add_table_obj(request,app_name,table_name):
    admin_class = king_admin.enable_admin[app_name][table_name]
    # 此处给admin_class动态添加了一个属性，用于在forms.py中只将readonly的前端表单属性赋给修改数据处使用
    admin_class.modify_flag = False
    model_form_class = create_model_form(request,admin_class)

    if request.method == "POST":
        # ModelForm的页面数据添加
        model_form_obj = model_form_class(request.POST)
        if model_form_obj.is_valid():
            #为实现密码设置，才让modelform对象先不提交的
            obj = model_form_obj.save(commit=False)
            if hasattr(obj,"password"):
                obj.set_password(obj.password)
            obj.save()
            #在commit=False的情况下需要手动保存多对多关系
            model_form_obj.save_m2m()
            #当数据添加完成后，直接进入到添加前的页面，但要能看到添加的数据，也就是以id来做降序
            return redirect("../?o=id")
    else:
        model_form_obj = model_form_class()
    ##print(json.dumps(model_form_obj.errors))

    return render(request, "king_admin/add_table_obj.html", {"model_form_obj":model_form_obj, "admin_class":admin_class})

#数据删除操作
import json
@login_required
def delete_table_obj(request,app_name,table_name,obj_id):
    ret = {"status": True, "data": None}
    admin_class = king_admin.enable_admin[app_name][table_name]
    obj = admin_class.model.objects.get(id=obj_id)
    if request.method == "POST":
        #如果readonly_table为true时后端禁止删除
        if admin_class.readonly_table:
            ret["data"] = "表为只读，数据不能删除"
        else:
            obj.delete()
            ret["data"] = "数据删除成功"
        return HttpResponse(json.dumps(ret))
    else:
        delete_content = utils.build_delete_obj_content_show(obj)
        return HttpResponse(delete_content);



# def show_layui_data(request,app_name,table_name):
#
#     table_objs = king_admin.enable_admin[app_name][table_name].list_display
#     rec = {"code":0,"msg":"","count":0,"data":[]}
#     page = request.GET.get("page")
#     limit = request.GET.get("limit")
#
#     admin_class = king_admin.enable_admin[app_name][table_name]
#
#     contact_list = admin_class.model.objects.all().values(*table_objs)
#
#
#     paginator = Paginator(contact_list, int(limit))  # Show 25 contacts per page
#     rec["count"] = paginator.count
#
#     try:
#         query_sets = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         query_sets = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         query_sets = paginator.page(paginator.num_pages)
#     for obj in query_sets:
#         for key in obj.keys():
#             if admin_class.model._meta.get_field(key) == "DateTimeField":
#              print(obj[key])
#         rec["data"].append(obj)
#     return HttpResponse(json.dumps(rec))
#
#
#
# def show_layui_table(request):
#     # table_objs = king_admin.enable_admin[app_name][table_name].list_display
#     return render(request,"king_admin/layui_table.html")

#修改密码
@login_required
def reset_password(request,app_name,table_name,selected_id):
    admin_class = king_admin.enable_admin[app_name][table_name]
    rec = {"status":0,"errors":None}
    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        errors= []
        if not password1 or not password2:
            errors.append("password cannot be space!")
            rec["status"] = 1
        elif len(password1)<5 or len(password2)<5:
            errors.append("password length must be more than 5!")
            rec["status"] = 1
        elif password1 == password2:
            rec["status"] = 0
            obj = admin_class.model.objects.get(id=int(selected_id))
            obj.set_password(password1)
            obj.save()
        else:
            errors.append("passwords are not the same!")
            rec["status"] = 1

        errors = ";".join(errors)
        rec["errors"] = errors
        print("dsaaaaaaaaa:",rec)
        return HttpResponse(json.dumps(rec))


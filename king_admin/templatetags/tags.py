#!/usr/bin/python
#-*- coding: utf-8 -*-


'''

'''
__author__ = 'wpxiao'
from django import template

register = template.Library()

@register.simple_tag
def render_app_name(admin_class):
    # return admin_class.model._meta.verbose_name
    return admin_class.model._meta.verbose_name_plural

@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()

# @register.simple_tag
# def bulid_td(admin_class,field_count,row_field):
#     #获取对应字段的对象
#     field_obj = admin_class.model._meta.get_field(admin_class.list_display[field_count])
#     #如果字段类型为是choices的话,那就取它对应的码值
#     if field_obj.choices:
#         row_field = dict(field_obj.choices)[row_field]
#         return row_field
#     return row_field

from django.core.exceptions import FieldDoesNotExist
from django.utils.safestring import mark_safe
@register.simple_tag
def build_table_row(obj,admin_class,request):
    row = ""
    if admin_class.list_display:
        for index,column in enumerate(admin_class.list_display):
            try:
                #获取一个字段对象
                field_obj = obj._meta.get_field(column)
                if field_obj.choices:
                    column_data = dict(field_obj.choices)[getattr(obj,column)]
                    #getattr(obj,"get_%s_display"%column)()通过此种方法也能获取到一个字段对应的值
                else:
                    # 通过反射来获取一个对象对应的属性内容
                    column_data = getattr(obj,column)
                if type(column_data).__name__ == "datetime":
                    column_data = column_data.strftime("%Y-%m-%d %H:%M:%S")
            except FieldDoesNotExist as e:
                print("显示字段不存在,字段名为：",column)
                if hasattr(admin_class,column):
                    admin_class.request = request
                    admin_class.row_id = obj.id
                    admin_class.instance = obj
                    func = getattr(admin_class,column)
                    column_data = func()
                else:
                    raise FieldDoesNotExist("字段%s不存在..."%column)

            #当为表中的第一个元素时就是添加a标签，然后跳转到数据的修改页面
            if index == 0:
                column_data = '<a href="{request_path}{obj_id}/change/?page={page}">{data}</a>'.\
                    format(request_path=request.path,obj_id=obj.id,data=column_data,page=request.GET.get("page"))
            row += "<td>%s</td>"%column_data
            # delete_bnt = '''<td><a class="btn btn-danger hide pull-right"  app_name="{app_name}" table_name="{table_name}"
            #                 data_id="{obj_id}" data-toggle="modal" data-target="#myModal">删除</a></td>'''.\
            #                 format(obj_id=obj.id,table_name=obj._meta.model_name,app_name=obj._meta.model._meta.app_label)
    else:
        column_data = '<a href="{request_path}{obj_id}/change/?page={page}">{data}</a>'. \
            format(request_path=request.path, obj_id=obj.id, data=obj, page=request.GET.get("page"))
        row += "<td>%s</td>" % column_data
    #通过lay-event来触发事件的产生，然后在js中进行工具条事件的捕获
    #通过前端来控制readonly_table为true的禁用删除操作
    if admin_class.readonly_table:
        delete_bnt = '''
                        <td >
                            <button class="layui-btn layui-btn-danger layui-btn-mini layui-btn-disabled" lay-event="del" app_name="{app_name}" table_name="{table_name}"
                            data_id="{obj_id}" data-toggle="modal" disabled>删除</button>
                        </td>
                        '''.format(obj_id=obj.id, table_name=obj._meta.model_name,
                                   app_name=obj._meta.model._meta.app_label)
    else:
        delete_bnt ='''
                    <td >
                        <button class="layui-btn layui-btn-danger layui-btn-mini" lay-event="del" app_name="{app_name}" table_name="{table_name}"
                        data_id="{obj_id}" data-toggle="modal"">删除</button>
                    </td>
                    '''. format(obj_id=obj.id,table_name=obj._meta.model_name,app_name=obj._meta.model._meta.app_label)
    row += delete_bnt
    #print(row)
    return mark_safe(row)

# #生成分页页码 显示当前页前面两条和当前页后面两条
# @register.simple_tag
# def rander_page_number(page_index,query_sets,selected_filters):
#     #显示除当前页外,前后各两页
#     current_page_interval = 2
#     #当前页
#     current_page = query_sets.number
#     element = ""
#     search_filter = ""
#     for key,value in selected_filters.items():
#         search_filter +="&"+key+"="+value
#
#     if abs(current_page-page_index) <= current_page_interval:
#         element = '<a href="?page=%s%s">%s</a>'%(page_index,search_filter,page_index)
#
#     return mark_safe(element)

#生成分页页码
# @register.simple_tag
# def rander_page_number(page_index,query_sets,selected_filters):
#     #显示除当前页外,前后各两页
#     current_page_interval = 1
#     #当前页
#     current_page = query_sets.number
#     element = ""
#     search_filter = ""
#     for key,value in selected_filters.items():
#         search_filter +="&"+key+"="+value
#     #显示前两页与后两页
#     if page_index <3 or page_index >query_sets.paginator.num_pages -2:
#         element = '<a href="?page=%s%s">%s</a>' % (page_index, search_filter, page_index)
#         return mark_safe(element)
#     #显示中间页
#     if abs(current_page-page_index) <= current_page_interval:
#         element = '<a href="?page=%s%s">%s</a>'%(page_index,search_filter,page_index)
#         return mark_safe(element)
#
#     #其他页不显示
#     return mark_safe(element)

#将后端的排序条件传入到前端的上一页下一面的按钮中
@register.simple_tag
def build_order_page_num(order_key_dict):
    order_condition = ""
    if order_key_dict:
        for key,value in order_key_dict.items():
            if value.startswith("-"):
                value = value.strip("-")
            else:
                value = "-"+value
            order_condition += "&o="+value
    return mark_safe(order_condition)


@register.simple_tag
def build_search_page_num(request):
    search_text = ""
    if request.GET.get("search_text"):
        search_text += "&"+"search_text="+request.GET.get("search_text")
    return mark_safe(search_text)

@register.simple_tag
def build_filter_page_num(selected_filters):
    search_filter = ""
    order_condition = ""
    display_flag = True
    for key, value in selected_filters.items():
        search_filter += "&" + key + "=" + value
    return mark_safe(search_filter)

#最新的分页页码
@register.simple_tag
def build_paginators(query_sets,selected_filters,order_key_dict,request):
    '''返回整个分页元素'''
    page_btns = ""
    # 显示除当前页外,前后各两页
    current_page_interval = 1
    # 当前页
    current_page = query_sets.number
    search_filter = ""
    order_condition = ""
    search_text = ""
    if request.GET.get("search_text"):
        search_text += "&"+"search_text="+request.GET.get("search_text")

    display_flag = True
    for key, value in selected_filters.items():
        search_filter += "&" + key + "=" + value

    if order_key_dict:
        for key,value in order_key_dict.items():
            if value.startswith("-"):
                value = value.strip("-")
            else:
                value = "-"+value
            order_condition += "&o="+value

    for page_index in query_sets.paginator.page_range:
        if page_index == query_sets.number:
            li = ' <li class="active">%s</li>'
        else:
            li = '<li>%s</li>'
        element = ""
        # 显示前两页与后两页
        if page_index <3 or page_index >query_sets.paginator.num_pages -2:
            element = '<a href="?page=%s%s%s%s">%s</a>' % (page_index, search_filter,search_text,order_condition, page_index)
            page_btns += li%element
        elif abs(current_page - page_index) <= current_page_interval:
            # 显示中间页
            element = '<a href="?page=%s%s%s%s">%s</a>' % (page_index, search_filter,search_text,order_condition, page_index)
            page_btns += li%element
            display_flag = True
        else:
            #其他页前后只显示...
            if display_flag:
                element = '<a>...</a>'
                page_btns += li%element
                display_flag = False
    #print(page_btns)
    return mark_safe(page_btns)


#生成时间过滤条件
def rander_table_datetime_filter(condition,admin_class,selected_filters):
    table_filter = '<div class="col-lg-2 col-xs-2">%s%s</div>'
    field_obj = admin_class.model._meta.get_field(condition)

    if type(field_obj).__name__ == "DateTimeField":
        start_datetime = '''<input size="16" type="text" id="datetimeStart" readonly class="form_datetime">'''
        end_datetime = '''<input size="16" type="text" id="datetimeEnd" readonly class="form_datetime">'''
        datetime_js = '''
                        <script src="/static/js/bootstrap-datetimepicker.js"></script>
                        <script src="http://cdn.bootcss.com/prettify/r224/prettify.js"></script>
                        <script type="text/javascript">
                            $("#datetimeStart").datetimepicker({
                                format: 'yyyy-mm-dd hh:ii:ss',
                                minView:'hour',
                                language: 'zh-CN',
                                autoclose:true,
                                startDate:new Date()
                            }).on("click",function(){
                                $("#datetimeStart").datetimepicker("setEndDate",$("#datetimeEnd").val())
                            });
                            $("#datetimeEnd").datetimepicker({
                                format: 'yyyy-mm-dd hh:ii:ss',
                                minView:'month',
                                language: 'zh-CN',
                                autoclose:true,
                                startDate:new Date()
                            }).on("click",function(){
                                $("#datetimeEnd").datetimepicker("setStartDate",$("#datetimeStart".val()))
                            });
                        </script>
        '''


#从django中导入时间模块，而不是直接从datetime模块中导入，这是因为时间模块需要与django项目的时间时区保持一致
from django.utils.timezone import datetime,timedelta
#生成过滤条件
@register.simple_tag
def rander_table_filter(condition,admin_class,selected_filters):
    """
             <div class="col-lg-2">
             adf
             <select name="source" class="form-control">
                 <option value="1">QQ群</option>
                 <option value="2">官网</option>
             </select>
         </div>
    """
    table_filter = '<div class="col-md-2">%s%s</div>'
    field_obj = admin_class.model._meta.get_field(condition)
    #当字段为choices时
    if field_obj.choices:
        select = '''<select name="%s" class="form-control">
                    <option value="" >-----</option>
                    %s</select>'''
        option_list = ""
        for choice  in field_obj.choices:

            if selected_filters  and choice[0] == int(selected_filters.get(condition,9999)):
                option = "<option value='%s' selected='selected'>%s</option>" % (choice[0], choice[1])
            else:
                option = "<option value='%s'>%s</option>"%(choice[0],choice[1])
            option_list += option
        select = select % (condition,option_list)
        table_filter = table_filter % (condition, select)
        return mark_safe(table_filter)
    #当字段为外键时
    if type(field_obj).__name__ == "ForeignKey":
        if field_obj.get_choices:
            select = '''<select name="%s" class="form-control">
                        <option value="">-----</option>
                        %s</select>'''
            option_list = ""
            for choice in field_obj.get_choices()[1:]:

                if selected_filters and choice[0] == int(selected_filters.get(condition,9999)):
                    option = "<option value='%s' selected='selected'>%s</option>" % (choice[0], choice[1])
                else:
                    option = "<option value='%s'>%s</option>" % (choice[0], choice[1])
                option_list += option
            select = select % (condition,option_list)
            table_filter = table_filter % (condition, select)
            return mark_safe(table_filter)
    #当字段为时间类型时
    if type(field_obj).__name__ in ["DateTimeField","DateField"]:
        today_ele = datetime.now().date()
        date_filter_list = []
        #都是一个大于的逻辑
        date_filter_list.append(["今天",today_ele])
        date_filter_list.append(["昨天",today_ele - timedelta(days=1)])
        date_filter_list.append(["近7天",today_ele - timedelta(days=7)])
        #将日期中的天替换成1
        date_filter_list.append(["本月",today_ele.replace(day=1)])
        date_filter_list.append(["近30天",today_ele - timedelta(days=30)])
        date_filter_list.append(["近90天",today_ele - timedelta(days=90)])
        date_filter_list.append(["近180天",today_ele - timedelta(days=180)])
        date_filter_list.append(["本年",today_ele.replace(month=1,day=1)])
        date_filter_list.append(["近一年",today_ele - timedelta(days=365)])
        select = '''<select name="%s__gte" class="form-control">
                    <option value="">-----</option>
                    %s</select>'''
        option_list = ""
        for choice in date_filter_list:
            #为了不让时间格式化时取的到数据为None，所以就收到加了9999-12-31
            if selected_filters and choice[1] == datetime.strptime(selected_filters.get(condition+"__gte","9999-12-31"),"%Y-%m-%d").date():
                option = "<option value='%s' selected='selected'>%s</option>" % (choice[1], choice[0])
            else:
                option = "<option value='%s'>%s</option>" % (choice[1], choice[0])
            option_list += option
        select = select % (condition, option_list)
        table_filter = table_filter % (condition, select)
        return mark_safe(table_filter)
    return ""

#生成字段排序
@register.simple_tag
def build_order(table_field,order_key_dict,selected_filters,request,admin_class):
    search_text = ""
    if request.GET.get("search_text"):
        search_text += "&"+"search_text="+request.GET.get("search_text")

    search_filter = ""
    for key, value in selected_filters.items():
        search_filter += "&" + key + "=" + value
    # print("order_key_dict:",order_key_dict)
    # if len(order_key_dict.keys()):
    #     pass
    #     for key,value in order_key_dict.items():
    #         # field_len = admin_class._meta.get_field(key).max_length
    #         if table_field == key and value.startswith("-"):
    #             th = '''<th lay-data="{field:'{lay_table_field}', width:100}">
    #                         <a href = "?o={order_key}{search_filter}{search_text}" > <span style="font-size:18px">{table_field}</span></a >
    #                         <span class="glyphicon glyphicon-chevron-down" aria-hidden="true"></span>
    #                     </th >'''\
    #             .format(lay_table_field=table_field,order_key=value,search_filter=search_filter,search_text=search_text,table_field=table_field)
    #         elif table_field == key:
    #             th = '''<th lay-data="{field:'{lay_table_field}', width:100}">
    #                         <a href = "?o={table_field}{search_filter}{search_text}" > <span style="font-size:18px">{table_field_1}</span> </a >
    #                            <span class="glyphicon glyphicon-chevron-up" aria-hidden="true"></span>
    #                     </th >'''\
    #             .format(lay_table_field=table_field,table_field=table_field,search_filter=search_filter,search_text=search_text,table_field_1=table_field)
    #         else:
    #             th = '''<th lay-data="{field:'lay_table_field', width:100}">
    #                         <a href = "?o={table_field}{search_filter}{search_text}" ><span style="font-size:18px">{table_field_1}</span> </a >
    #                     </th >'''\
    #             .format(table_field=table_field,search_filter=search_filter,search_text=search_text,table_field_1=table_field)

    else:
        try:
            field_name = admin_class.model._meta.get_field(table_field).verbose_name.upper()
        except FieldDoesNotExist as e:
            #此处显示自定义字段对应的dispaly_name
            if hasattr(admin_class,table_field):
                func = getattr(admin_class,table_field)
                field_name = func.display_name
            #处理用户没有设置display_list字段时给它显示对象
            elif table_field =="table_obj":
                 field_name = table_field
        th = '''<th lay-data="{field:'%s', width:120,sort:true}">
                    <a href = "?o=%s%s%s" > <span style="font-size:18px">%s</span> </a >   
                </th >'''\
        %(table_field,table_field,search_filter,search_text,field_name)
    print(th)
    return mark_safe(th)


@register.simple_tag
def build_select_mult_option(admin_class,model_form_obj,field):
    """获取备选的多对多关系数据
        models.Customer.tags.rel.to.objects.all()
        返回数据：
        QuerySet [<Tag: xxoo>, <Tag: xxyy>, <Tag: 你好>, <Tag: 你是sb>, <Tag: 你是人>, <Tag: 另了>]>]
    """
    field_obj = getattr(admin_class.model,field.name)
    #获取已选中的多对多关系数据，从而在备选数据中排除已选数据
    selected_objs = build_selected_mult_option(model_form_obj,field)
    if selected_objs:
        selected_ids = [i.id for i in selected_objs]
        return field_obj.rel.to.objects.exclude(id__in=selected_ids).order_by("id")
    else:
        return field_obj.rel.to.objects.all().order_by("id")

@register.simple_tag
def build_selected_mult_option(model_form_obj,field):
    """获取已选中的多对多关系数据
        方法一：
        models.Customer.objects.filter(id=18).first().tags.all()
        返回数据：
            <QuerySet [<Tag: 你是人>, <Tag: 你好>]>
        方法二：通过modelform对象中的instance方法来获取到model对象
            model_form_obj.instance.tags.all()

    """
    #判断此操作是添加还是修改,当id存在时说明就是修改，g
    if model_form_obj.instance.id:
        obj = getattr(model_form_obj.instance,field.name)
        #print(obj.all())
        return obj.all().order_by("id")
    else:
        return ""
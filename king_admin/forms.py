#!/usr/bin/env python3
#-*- coding:utf-8 -*-
'''

'''
__author__ = "wpxiao"

from django.forms import ModelForm,fields
from django.forms import ValidationError
from crm import models
from django.utils.translation import ugettext_lazy as _


#普通创建ModelForm的方式
class Mf(ModelForm):
    class Meta:
        model = models.Customer
        fields = "__all__"

#动态创建ModelForm的方式
def create_model_form(request,admin_class):
    '''动态生成Model Form'''

    #动态样式设置,此函数相当于是一个闭包，
    def __new__(cls,*args,**kwargs):
        # 调用父类new方法的方式一：super(CustomerForm,self).__new__(*args,**kwargs)
        #print("base_fields:",cls.base_fields)
        #给字段qq在Html的中添加class="form-control"样式
        #cls.base_fields["qq"].widget.attrs["class"] = "form-control"
        #动态为所有的字段设置form-control样式

        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs["class"] = "form-control"

            if field_name == "password":
                field_obj.widget.input_type = "password"

            # 将input中的输入字段的最大长度设置为“”,由bootstrap来控制输入框的大小
            if hasattr(field_obj,"max_length"):
                field_obj.widget.attrs["maxlength"] = ""
            #print("------------------------",hasattr(admin_class,"_modify_flag"))
            #表示如果没有_modify_flag的字段属性那就是修改操作，所以就是需要添加上readonly属性，否则就是表单的添加操作就不需要readonly
            if hasattr(admin_class,"modify_flag"):
                if getattr(admin_class,"modify_flag"):
                    #设置只读字段,如果想使用disabled这个来控制只读的话，那就需要在前端页面上提交时将disabled去除掉来，这样request.POST中
                    # 才会有这个字段的数据，否则就会报错
                    #注：由于__new__方法是在__init__方法前执行，此时是没有对象实例的，所以cls表示的类，而不是对象实例，也就意味着
                    #   此处是不能使用cls.instance来判定是修改还是添加
                    if field_name in admin_class.readonly_fields:
                        # field_obj.widget.attrs["readonly"] = "readonly"
                        #由于表单属性readonly不能控制select所以就使用disabled,但由于使用disabled的话在提交表单时
                        #就无法获取到disabled中的表单值，所以在表单提交时需要把disabled通过js去掉
                        field_obj.widget.attrs["disabled"] = "disabled"

            #判断king-admin中自定义的clean_field的方法是否存在
            if hasattr(admin_class,"clean_%s"%field_name):
                #获取方法函数
                clean_field_func = getattr(admin_class,"clean_%s"%field_name)
                #将方法函数设置在modeform的类中
                setattr(cls,"clean_%s"%field_name,clean_field_func)

        #调用父类new方法的方式二：
        return ModelForm.__new__(cls)

    # 此函数在views中的is_vaild方法执行时被调用，因此self就是modelform绑定上Post与后端数据实例的对象
    #此函数的作用是用于验证前后端readonly字段的数据是否一致
    def default_clean(self):
        #后端对象
        backend_obj = self.instance
        #前端数据
        cleaned_data = self.cleaned_data
        error_list = []

        #如果存在instance对象，则说明数据与modelform做了绑定，也就是说明此处属于表单修改页面的逻辑，而不属于表单添加的逻辑
        #此处主要是为了避免同时让表单的添加页面与修改页面都加上只读字段的验证逻辑
        if self.instance.id:
            #这个就相当于将readonly的验证做为了系统默认的验证规则
            for readonly_field in admin_class.readonly_fields:
                backend_obj_field_value = getattr(backend_obj,readonly_field)
                forward_obj_field_value = cleaned_data.get(readonly_field)
                #下划线表示国际化
                if backend_obj_field_value != forward_obj_field_value:
                    #一次只能抛出一个只读错误，如果同时有两个只读错误的话，那页面也只会提示一个只读错误
                    # raise ValidationError(
                    #     _("Field %(field)s is readonly,data shoud be %(val)s"),
                    #     code="invaild",
                    #     params={"field":readonly_field,"val":backend_obj_field_value}
                    # )
                    error = ValidationError(
                        _("Field %(field)s is readonly,data shoud be %(val)s"),
                        code="invaild",
                        params={"field":readonly_field,"val":backend_obj_field_value}
                    )
                    error_list.append(error)
        #后端控制整张表为只读，保证表的修改与数据的添加无效
        if admin_class.readonly_table:
            raise ValidationError(
                _("Table %(table)s is readonly,Data cannot modifyed or added"),
                code="invaild",
                params={"table": admin_class.model._meta.model_name}
            )
        # 预留的用户自定制验证接口，以便用户在king_admin.py中调用
        #此self也就是modelform的实例
        self.ValidationError = ValidationError
        response = admin_class.default_form_validation(self)
        if response:
            error_list.append(response)

        #抛出一个错语异常数组，
        if error_list:
            raise  ValidationError(error_list)

    class Meta:
        model = admin_class.model
        #显示所有字段
        fields = "__all__"
        #排除last_login字段不显示
        exclude = admin_class.modelform_exclude_fields
    #类也是和函数的使用方式是一样的，而不能用setattr方法来绑定
    # _model_form_class = type("DynamicModelForm",(ModelForm,),{})
    # setattr(_model_form_class,"Meta",Meta)
    attrs = {"Meta":Meta}
    _model_form_class = type("DynamicModelForm",(ModelForm,),attrs)
    setattr(_model_form_class,"__new__",__new__)
    setattr(_model_form_class,"clean",default_clean)
    return _model_form_class
#!/usr/bin/env python3
#-*- coding:utf-8 -*-
'''

'''
__author__ = "wpxiao"

from django.forms import ModelForm
from crm import models

class ModelFormEnrollment(ModelForm):
    #为每行数据添加样式
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs["class"] = "form-control"
        return ModelForm.__new__(cls)

    class Meta:
        model = models.Enrollment
        fields = ("enrolled_class","consultant")

from django.utils.translation import ugettext_lazy as _
from django.forms import ValidationError
class ModelFormCustomer(ModelForm):
    #为每行数据添加样式
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs["class"] = "form-control"
            #将错误提示转成中文
            field_obj.error_messages = {"required":"字段不能为空","invalid":"输入格式不对"}
            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs["disabled"] = "disabled"
        return ModelForm.__new__(cls)

    def clean(self):
        for readonly_field in self.Meta.readonly_fields:
            if self.cleaned_data.get(readonly_field) != getattr(self.instance,readonly_field):
                self.add_error(readonly_field,"%s为只读字段"%readonly_field)

    class Meta:
        model = models.Customer
        fields = "__all__"
        exclude = ["status","content","tags","memo","referral_from"]
        #自定义只读字段
        readonly_fields = ["qq","consultant","source"]
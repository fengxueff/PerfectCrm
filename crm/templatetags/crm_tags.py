#!/usr/bin/env python3
#-*- coding:utf-8 -*-
'''

'''
__author__ = "wpxiao"

from django import template
from django.utils.timezone import datetime

register = template.Library()


@register.simple_tag
def render_contract(enrollment_obj):
    """
        构建格式化合同内容
    """
    contract_content = enrollment_obj.enrolled_class.contract.content
    customer_name_1 = customer_name_2 = enrollment_obj.customer.name
    current_date = datetime.now().date()
    date_1 = date_2 = datetime.strftime(current_date,"%Y-%m-%d")

    contract_content = contract_content.format\
        (customer_name_1=customer_name_1,customer_name_2=customer_name_2,date_1=date_1,date_2=date_2)
    return contract_content

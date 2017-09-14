#!/usr/bin/env python3
#-*- coding:utf-8 -*-
'''

'''
__author__ = "wpxiao"

from django import template
from django.db.models import Sum
from django.utils.safestring import mark_safe
register = template.Library()


@register.simple_tag
def score_total(enroll_obj):
    scores = enroll_obj.studyrecord_set.aggregate(Sum("score"))
    print(scores,scores["score__sum"])
    return scores["score__sum"]

import os
from django.urls import reverse
@register.simple_tag
def render_attach(attach_obj,file_count):
    alert_list = ["alert-info", "alert-success", "alert-danger"];
    alert_color = alert_list[file_count % 3];
    attach_url = reverse("homework_attachment_download",kwargs={"studyrecord_id":attach_obj.study_record.id,"attach_id":attach_obj.id})

    name = os.path.basename(attach_obj.attachment_url)
    alert_attach ='<div class="alert ' + alert_color + ' alert-dismissable" style="display: inline-block;margin-left:5px;">\
                                    <button type="button" class="close" data-dismiss="alert" aria-hidden="true">\
                                        &times;\
                                    </button> <a href='+attach_url+'>' + name + '</a>\
                                </div>';
    return mark_safe(alert_attach)
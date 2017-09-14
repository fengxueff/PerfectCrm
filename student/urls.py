"""PerfectCrm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from student import views
urlpatterns = [
    url(r"^$",views.stu_index,name="stu_index"),
    url(r"^my_class/$",views.my_class,name="my_class"),
    url(r"^my_class/study_records/(?P<enroll_id>\d+)/$",views.study_records,name="study_records"),
    url(r"^my_class/study_records/homework_detail/(?P<studyrecord_id>\d+)/$",views.homework_detail,name="homework_detail"),
    url(r"^my_class/study_records/homework_detail/(?P<studyrecord_id>\d+)/(?P<attach_id>\w+)$", views.homework_attachment_download,
        name="homework_attachment_download"),
]

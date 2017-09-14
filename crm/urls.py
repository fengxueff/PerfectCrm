
from django.conf.urls import url
from crm import views
urlpatterns = [
    url(r"^$",views.index,name="sales_index"),
    # url(r"^customer/$",views.customer_list,name="customer_list"),
    url(r"^customer/(?P<nid>\d+)/enrollment",views.sale_enroll,name="sale_enroll"),
    url(r"^customer/registration/(?P<enroll_id>\d+)/(?P<random_str>\w+)/", views.stu_registration, name="stu_registration"),
    url(r"^customer/registration_back/(?P<enroll_id>\d+)/", views.stu_registration_back, name="stu_registration_back"),
    url(r"^customer/enrollment/(?P<enroll_id>\d+)/audit/", views.enroll_audit, name="enroll_audit"),
    url(r"^customer/enrollment/(?P<enroll_id>\d+)/payment/", views.enroll_payment, name="enroll_payment"),
   # url(r"^customer/enrollment/(?P<enroll_id>\d+)/reject/", views.enroll_reject, name="enroll_reject"),

]

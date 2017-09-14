
from django.conf.urls import url
from king_admin import views
urlpatterns = [
    url(r"^$",views.index,name="admin_index"),
    #url(r"^custom_action/$",views.custom_action,name="custom_action"),
    # url(r"^layui_table/$", views.show_layui_table, name="show_layui_table"),
    # url(r"^(\w+)/(\w+)/show_layui_data/$", views.show_layui_data, name="show_layui_data"),
    url(r"^(\w+)/$",views.app_index,name="app_index"),
    url(r"^(\w+)/(\w+)/$",views.display_table_objs,name="table_objs"),
    url(r"^(\w+)/(\w+)/(\d+)/change/$", views.change_table_obj, name="change_table_obj"),
    url(r"^(\w+)/(\w+)/(\d+)/change/password/$", views.reset_password, name="reset_password"),
    url(r"^(\w+)/(\w+)/add/$", views.add_table_obj, name="add_table_obj"),
    url(r"^(\w+)/(\w+)/delete/(\d+)/$", views.delete_table_obj, name="delete_table_obj"),

]

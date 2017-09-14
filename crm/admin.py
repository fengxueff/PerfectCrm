from django.contrib import admin

# Register your models here.
from crm import models

class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id","qq","source","consultant","content","date")
    list_filter = ("source","consultant","date")
    search_fields = ("qq","name")
    raw_id_fields = ("consult_course",)
    filter_horizontal = ("tags",)
    list_editable = ("source",)
    list_per_page = 1



from django.shortcuts import  HttpResponse,redirect
class CourseRecordAdmin(admin.ModelAdmin):
    list_display = ("from_class","day_num","teacher","has_homework")

    def initialize_student_record(modeladmin, request, queryset):
        if len(queryset) >1:
            return HttpResponse("只能选择一个班级")

        courserecord_obj = queryset[0]

        #创建方式一：普通的单行记录依次创建，在大数据下效率低
        # for enroll_obj in courserecord_obj.from_class.enrollment_set.all():
        #     #get_or_create表示如果存在就不创建，如果不存在就创建
        #     models.StudyRecord.objects.get_or_create(student=enroll_obj,
        #                                              course_record=courserecord_obj,score=0)

        #创建方式二：批量创建，效率高，支持事务
        studyrecord_objs = []
        for enroll_obj in courserecord_obj.from_class.enrollment_set.all():
            studyrecord_obj = models.StudyRecord(student=enroll_obj,course_record=courserecord_obj,score=0)
            studyrecord_objs.append(studyrecord_obj)
        #先删除后创建
        # models.StudyRecord.objects.filter(course_record=courserecord_obj).delete()
        try:
            models.StudyRecord.objects.bulk_create(studyrecord_objs)
        except Exception as e:
            print("数据已经存在:",e)

        return redirect("../studyrecord")


    #定义在action下拉列表中的名称
    initialize_student_record.short_description = "初始化学生上课纪录"

    actions = [initialize_student_record]



from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from crm.models import UserProfile


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model =  UserProfile
        fields = ('email', 'name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model =  UserProfile
        fields = ('email', 'password', 'name', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class  UserProfileAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_admin',"user_permissions","groups","is_superuser")}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

# Now register the new UserAdmin...
admin.site.register(UserProfile,  UserProfileAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.unregister(Group)

admin.site.register(models.Customer,CustomerAdmin)
admin.site.register(models.Tag)
# admin.site.register(models.UserProfile)
admin.site.register(models.Course)
admin.site.register(models.Branch)
admin.site.register(models.ClassList)
admin.site.register(models.CourseRecord,CourseRecordAdmin)
admin.site.register(models.StudyRecord)
admin.site.register(models.Enrollment)
admin.site.register(models.Payment)
admin.site.register(models.CustomerFollowUp)
admin.site.register(models.Role)
admin.site.register(models.Menu)
admin.site.register(models.Contract)



from django.db import models

# Create your models here.

"""
    类的创建流程:
        Customer(客户信息表)
        
"""
class Customer(models.Model):
    """
        # 客户信息表 -->特指对销售有意义的有效客户
    """
    #blank=True这个只是在django-admin中页面上限制为可以为空
    #null=True是限定数据库中可以为空
    name = models.CharField(verbose_name="客户姓名",max_length=32,blank=True,null=True)
    #因为通过qq进行的联系的客户才是有效客户
    qq = models.CharField(verbose_name="QQ",max_length=64,unique=True)
    qq_name = models.CharField(verbose_name="QQ名",max_length=64,blank=True,null=True)
    phone = models.CharField(verbose_name="联系电话",max_length=64,blank=True,null=True)
    id_num = models.CharField(verbose_name="身份证",max_length=18,blank=True,null=True)
    email = models.EmailField(verbose_name="常用邮箱",blank=True,null=True)
    source_choices = (
        (0,"转介绍"),
        (1,"QQ群"),
        (2,"官网"),
        (3,"百度推广"),
        (4,"51CTO"),
        (5,"知乎"),
        (6,"市场推广")
    )
    source = models.SmallIntegerField(verbose_name="信息来源",choices=source_choices)
    status_choices = ((0, "未报名"), (1, "已报名"))
    status = models.SmallIntegerField(verbose_name="报名状态",choices=status_choices,default=0)
    referral_from = models.CharField(verbose_name="介绍人qq",max_length=64,blank=True,null=True)
    #多对一,客户信息表中的多条记录中的咨询课程对应课程表中的一条记录
    consult_course = models.ForeignKey(to="Course",verbose_name="咨询课程")
    content = models.TextField(verbose_name="咨询详情")
    #多对多关系
    tags = models.ManyToManyField(to="Tag",blank=True,null=True)
    # 多对一,客户信息表中的多条记录中的咨询顾问对应账号表中的一条记录
    consultant = models.ForeignKey(to="UserProfile",verbose_name="咨询顾问")
    memo = models.TextField(blank=True,null=True,verbose_name="备注")
    date = models.DateTimeField(auto_now_add=True,verbose_name="咨询时间")

    def __str__(self):
        return self.qq

    class Meta:
        # verbose_name = "客户信息表"
        #如果使用verbose_name = "客户信息表"的话,那在django-admin中这个表名后面会跟上s,也就是表名的复数形式
        #如果想干掉这个s就需要使用verbose_name_plural
        verbose_name_plural = "客户信息表_Customer"

class Tag(models.Model):
    """
        标签表,与客户信息表是多对多的关系.也就是说一个客户有多个标签,一个标签可以同时作用在多个
        多个客户上
    """
    name = models.CharField(max_length=32,unique=True,verbose_name="标签名")

    class Meta:
        verbose_name_plural = "标签表_Tag"
    def __str__(self):
        return self.name

#引入django自带的认证
 # from django.contrib.auth.models import User
# class UserProfile(models.Model):
#     """
#         账号表
#     """
#     user = models.OneToOneField(User)
#     name = models.CharField(max_length=32,verbose_name="用户名")
#     #一个账号有多个角色,一个角色属于多个账号
#     roles = models.ManyToManyField(to="Role",blank=True,null=True,verbose_name="角色")
#
#     def __str__(self):
#         return "%s"%(self.user)
#
#     class Meta:
#         verbose_name_plural = "账号表_UserProfile"

#自定义用户认证
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
#UserProfileManager还必须在UserProfile前面，UserProfile作用在于定义model对象，而UserProfileManager的作用在于
#执行创建用户或超级用户的命令 python manage.py createsuperuser中就用到下面这两个定义的类
class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
            password=password,
            name=name
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

from django.utils.translation import ugettext_lazy as _

class UserProfile(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(
        verbose_name='邮箱',
        max_length=255,
        unique=True,
    )
    #重写父类的password属性，以便不修改源代码，添加一个help_text属性用于修改密码
    password = models.CharField(_('password'), max_length=128,help_text="<a href='javascript:' data-toggle='modal' data-target='#myModal'>密码修改</a>")
    name = models.CharField(verbose_name="用户名",max_length=32)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    roles = models.ManyToManyField(to="Role",blank=True,verbose_name="角色")
    stu_enrollment = models.ForeignKey(to="Customer",blank=True,null=True,verbose_name="已报名的学生")
    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    #为认证类添加自定义的权限列表
    class Meta:
        permissions = (
                        ("crm.can_access_my_class","访问我的课程")
                       ,("crm.can_access_customer_list","访问客户库")
                       ,("crm.can_access_customer_detail","访问客户详情")
                       ,("crm.can_change_customer_detail","修改客户详情")
        )


    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Course(models.Model):
    """
        课程表
    """
    name = models.CharField(max_length=64,unique=True,verbose_name="课程名")
    #positiveIntegerField表示正数
    price = models.PositiveIntegerField(verbose_name="价格")
    period = models.PositiveIntegerField(verbose_name="周期(月)")
    outline = models.TextField(verbose_name="课程大纲")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "课程表_Course"

class Branch(models.Model):
    """
        校区
    """
    name = models.CharField(max_length=128,unique=True,verbose_name="校区名")
    addr = models.CharField(max_length=128,verbose_name="地址")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "校区表_Branch"

class ClassList(models.Model):
    """
        班级列表
    """
    branch = models.ForeignKey(to="Branch")

    course = models.ForeignKey(to="Course",verbose_name="课程")
    class_type_choices = ((0,"面授(脱产"),(1,"面授(周末)"),(2,"网络班"))
    class_type = models.SmallIntegerField(choices=class_type_choices,verbose_name="教学方式")
    #此字段在这个地方就类似于班级名称:如python全栈第2期
    semester = models.PositiveIntegerField(verbose_name="学期")
    contract = models.ForeignKey(to="Contract",verbose_name="合同",blank=True,null=True)
    teachers = models.ManyToManyField(to="UserProfile",verbose_name="老师")
    start_date = models.DateField(verbose_name="开班日期")
    end_date = models.DateField(verbose_name="结业时期",blank=True,null=True)

    class Meta:
        verbose_name_plural = "班级表_ClassList"
        #同一个校区 同一个课程 同一个学期,只能有一个班级使用,所以使用联合索引避免重复
        unique_together = ("branch","course","semester")

    def __str__(self):
        return "%s %s %s"%(self.branch,self.course,self.semester)


class CourseRecord(models.Model):
    """
        上课记录
    """
    from_class = models.ForeignKey(to="ClassList",verbose_name="班级")
    day_num = models.PositiveIntegerField(verbose_name="第几节(天)")
    teacher = models.ForeignKey(to="UserProfile",verbose_name="老师")
    has_homework = models.BooleanField(default=True,verbose_name="是否有作业")
    homework_title = models.CharField(max_length=128,blank=True,null=True)
    homework_content = models.TextField(verbose_name="作业内容",blank=True,null=True)
    outline = models.TextField(verbose_name="本节课程大纲")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s"%(self.from_class,self.day_num)

    class Meta:
        verbose_name_plural = "上课记录表_CourseRecord"
        # 班级与第几天是联合唯一索引
        unique_together = ("from_class","day_num")

class StudyRecord(models.Model):
    """
        学习记录
    """
    student = models.ForeignKey(to="Enrollment",verbose_name="报名表中的学生")
    course_record = models.ForeignKey(to="CourseRecord",verbose_name="上课记录")
    attendance_choices = ((0,"已签到"),(1,"迟到"),(2,"缺勤"),(3,"早退"))
    attendance = models.SmallIntegerField(choices=attendance_choices,default=0,\
                                          verbose_name="出勤情况")

    score_choices = (
                        (100,"A+"),
                        (90,"A"),
                        (85,"B+"),
                        (80,"B"),
                        (75,"B-"),
                        (70,"C+"),
                        (60,"C"),
                        (40,"C-"),
                        #得D就要扣分了,也就是扣钱了
                        (-50,"D"),
                        #抄作业就扣100分
                        (-100,"COPY"),
                        #由于以前没有来,那以前的作业就是0分
                        (0,"N/A"),
    )
    score = models.SmallIntegerField(choices=score_choices,verbose_name="学习成绩")
    memo = models.TextField(verbose_name="批作业的备注")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s"%(self.student,self.course_record,self.score)

    class Meta:
        verbose_name_plural = "学习记录表_StudyRecord"
        unique_together = ("student","course_record")

class HomeworkAttachment(models.Model):
    study_record = models.ForeignKey(to="StudyRecord",verbose_name="学习记录")
    attachment_url = models.URLField(verbose_name="附件上传的url")

    def __str__(self):
        return "%s %s"%(self.study_record,self.attachment_url)

    class Meta:
        verbose_name_plural = "作业附件"
        unique_together = ("attachment_url",)

class Contract(models.Model):
    """
        合同表
    """
    name = models.CharField(verbose_name="合同名称",max_length=128,unique=True)
    content = models.TextField(verbose_name="合同内容",blank=True,null=True)

    class Meta:
        verbose_name_plural = "合同表_Contract"

    def __str__(self):
        return "%s"%self.name

class Enrollment(models.Model):
    """
        报名表
    """
    customer = models.ForeignKey(to="Customer",verbose_name="客户")
    enrolled_class = models.ForeignKey(to="ClassList",verbose_name="报名的班级")
    consultant = models.ForeignKey("UserProfile",verbose_name="促成报名的课程顾问")
    #由于需要在线点击同意,所以在此处默认就为False
    contract_agreed = models.BooleanField(default=False,verbose_name="学员已同意合同条款")
    contract_approvel = models.BooleanField(default=False,verbose_name="合同已审核")

    def __str__(self):
        return "%s %s"%(self.customer,self.enrolled_class)

    class Meta:
        verbose_name_plural = "报名表_Enrollment"
        unique_together = ("customer","enrolled_class")

class Payment(models.Model):
    """
        缴费记录 -->先缴费后报名
    """
    customer = models.ForeignKey(to="Customer")
    course = models.ForeignKey(to="Course",verbose_name="所报课程")
    #默认定金就是500
    amount = models.PositiveIntegerField(verbose_name="数额",default=500)
    consultant = models.ForeignKey(to="UserProfile")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s"%(self.customer,self.amount)

    class Meta:
        verbose_name_plural = "缴费记录表_Payment"

class CustomerFollowUp(models.Model):
    """
        客户跟进表
    """
    customer = models.ForeignKey(to="Customer",verbose_name="客户信息")
    content = models.TextField(verbose_name="跟进内容")
    consultant = models.ForeignKey(to="UserProfile",verbose_name="跟进人_咨询顾问")
    date = models.DateTimeField(auto_now_add=True)
    intention_choices =((0,"2周内报名"),(1,"1个月内报名"),(2,"近期无报名计划")
                        ,(3,"已在其它机构报名"),(4,"已报名"),(5,"已拉黑")
                        )
    intention = models.SmallIntegerField(choices=intention_choices)

    def __str__(self):
        return "<%s : %s>"%(self.customer.qq,self.intention)

    class Meta:
        verbose_name_plural = "客户跟进记录表_CustomerFollowUp"

class Role(models.Model):
    """
        角色表
    """
    name = models.CharField(max_length=32,unique=True,verbose_name="角色名")
    menus = models.ManyToManyField(to="Menu",blank=True,verbose_name="菜单列表")
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "角色表_Role"

class Menu(models.Model):
    """
        菜单表
    """
    name = models.CharField(max_length=32,unique=True,verbose_name="菜单名")
    url_type_choices = ((0,"alias"),(1,"absolute_url"))
    url_type = models.SmallIntegerField(choices=url_type_choices,verbose_name="url类型",default=0)
    url_name = models.CharField(max_length=64,verbose_name="url别名")

    def __str__(self):
        return "%s %s %s"%(self.name,self.url_type,self.url_name)

    class Meta:
        verbose_name_plural="菜单表_Menu "

from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def index(request):

    return render(request,"index.html")

@login_required
def customer_list(request):
    return render(request,"sales/customers.html")


from crm import forms
from crm import models
from django.db.utils import IntegrityError
# from django.urls import reverse
import random,string
from django.core.cache import cache
@login_required
def sale_enroll(request,nid):
    '''
        销售人员对学生进行报名，并把学员需要填写的注册信息链接发给学员，待学员填写完成后进行复核并添加缴费纪录，然后完成报名流程
    '''

    #需要学生填写的链接，如是否同意协议，发给学生的链接三小时内有效
    msg_link = ""
    customer_obj = models.Customer.objects.get(id=nid)
    if request.method == "GET":
        modelform_obj = forms.ModelFormEnrollment()
    else:
        msg_path = "http://"+"/".join(request.environ["HTTP_REFERER"].split("/")[2:5])+"/registration/%s/%s/"
        modelform_obj = forms.ModelFormEnrollment(request.POST)
        #取8位字线加数字的随机字符串
        str = string.ascii_lowercase+string.digits
        random_str = "".join(random.sample(str,8))

        if modelform_obj.is_valid():

            print(customer_obj)
            cleaned_data = modelform_obj.cleaned_data
            cleaned_data["customer"] = customer_obj

            enrollment_obj = models.Enrollment(**cleaned_data)


            try:
                #新建
                enrollment_obj.save()
                print("缓存时", enrollment_obj.id, random_str)
                # 随机字符串缓存3个小时
                cache.set(enrollment_obj.id, random_str, 60*60*3)
                msg_link = msg_path%(enrollment_obj.id,random_str)
            except IntegrityError as e:
                # 已存在
                enrollment_obj = models.Enrollment.objects.get(customer=customer_obj.id,
                                                               enrolled_class=cleaned_data["enrolled_class"])
                #判断学员是否已经同意的合同协议，如果同意则进行学员注册信息复核页面
                if enrollment_obj.contract_agreed:
                    return redirect("/crm/customer/enrollment/%s/audit/"%enrollment_obj.id)


                modelform_obj.add_error("__all__","此报名记录已经存在")

                print("缓存时123", enrollment_obj.id, random_str)
                # 随机字符串缓存3个小时
                cache.set(enrollment_obj.id, random_str, 60*60*3)
                msg_link = msg_path % (enrollment_obj.id,random_str)
        else:
            pass
    return render(request,"sales/enrollment.html",{"modelform_obj":modelform_obj,"obj":customer_obj,"msg_link":msg_link})

import copy
from PerfectCrm import settings
import os
def stu_registration(request,enroll_id,random_str):
    '''
        学生信息注册
    '''
    print("获取缓存时",enroll_id,random_str)
    enrollment_obj = models.Enrollment.objects.get(id=enroll_id)
    if cache.get(enrollment_obj.id) == random_str:

        if request.method == "POST":
            #判断是否是ajax发送过来的数据，这里用来判断是否是上传图片
            if request.is_ajax():
                if request.POST.get("type") == "delete":
                    file_name = request.POST.get("file_name")
                    file_path = os.path.join(settings.ENROLL_DATA,enroll_id,file_name)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        return HttpResponse("文件%s删除成功"%file_name);
                    else:
                        return HttpResponse(file_name+"不存在")

                file_obj = request.FILES.get("file")
                if not os.path.exists(settings.ENROLL_DATA):
                    os.mkdir(settings.ENROLL_DATA)
                #相当于mkdir -P
                os.makedirs(os.path.join(settings.ENROLL_DATA,enroll_id),exist_ok=True)
                with open(os.path.join(settings.ENROLL_DATA,enroll_id,file_obj.name),"wb") as f:
                    print("asddafffffffff")
                    for chunk in file_obj.chunks():
                        f.write(chunk)
                return HttpResponse(file_obj.name+"上传成功")


            post_dict = copy.copy(request.POST)
            page = "".join(post_dict.pop("page"))
            page = int(page)
            checkbox = request.POST.get("checkbox")

            #流程二：协议同意
            if checkbox:
                print(checkbox)
                enrollment_obj.contract_agreed = True
                enrollment_obj.save()
                page = page + 1
                return redirect("./?page=%s" % page)

            #流程一：补充学员信息
            customerform_obj = forms.ModelFormCustomer(post_dict,instance=enrollment_obj.customer)
            if customerform_obj.is_valid():
                customerform_obj.save()
                page = page +1
                return redirect("./?page=%s"%page)
            else:
                pass
        else:

            customerform_obj = forms.ModelFormCustomer(instance=enrollment_obj.customer)
            page = request.GET.get("page",0)
        return render(request,"sales/stu_registration.html",{"customerform_obj":customerform_obj,"enrollment_obj":enrollment_obj,"page":page})
    else:
        return HttpResponse("你的链接已失效")

def stu_registration_back(request,enroll_id):
    '''
        ajax请求返回学员注册信息时的上一标签页
    '''
    path = "http://" + "/".join(request.environ["HTTP_REFERER"].split("/")[2:5]) + "/registration/%s/%s/"%(enroll_id,cache.get(enroll_id))
    path = path+"?page=%s"%(int(request.GET.get("page"))-1,)
    return HttpResponse(path);

@login_required
def enroll_audit(request,enroll_id):
    '''
        学员报名注册信息的复核
    '''
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    customer_obj = enroll_obj.customer
    customerform_obj = forms.ModelFormCustomer(instance=customer_obj)
    return render(request,"sales/enrollment_aduit.html",{"customerform_obj":customerform_obj,"enroll_id":enroll_id})


from django.urls import reverse
@login_required
def enroll_reject(request,enroll_id):
    '''
        复核被驳回时
    '''
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_obj.contract_agreed = False
    enroll_obj.save()
    path = reverse("sale_enroll",args=(str(enroll_obj.customer.id),))
    return redirect(path)

@login_required
def enroll_payment(request,enroll_id):
    '''
        报名缴费
    '''
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    customer_obj = enroll_obj.customer
    error = ""
    if request.method == "POST":
        amount = request.POST.get("amount","0")
        amount = int(amount)
        if amount < 500:
            error = "输入的金额不得小于500"
        else:
            payment_obj = models.Payment(customer=customer_obj,course=enroll_obj.enrolled_class.course,amount=amount,consultant=customer_obj.consultant)
            payment_obj.save()
            customer_obj.status = 1
            customer_obj.save()
            return redirect("/king_admin/crm/customer/")

    return render(request,"sales/stu_payment.html",{"customer_obj":customer_obj,"enroll_obj":enroll_obj,"error":error  })
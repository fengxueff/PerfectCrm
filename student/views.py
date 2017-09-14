from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from crm import models
from crm.permissions import permission


@login_required
def stu_index(request):
    return render(request,"student/stu_index.html")


# 由于使用了权限检测的装饰器，在它的里面已经对是否登录进行了判断，所以这里就需要@login_required了
@permission.check_permission
def my_class(request):
    enrollment_queryset = request.user.stu_enrollment.enrollment_set.all()
    return render(request,"student/my_class.html",{"enrollment_queryset":enrollment_queryset})

@login_required
def study_records(request,enroll_id):
    studyrecord_queryset = models.StudyRecord.objects.filter(student_id = enroll_id)
    return render(request,"student/study_records.html",{"studyrecord_queryset":studyrecord_queryset})

import os
from django.shortcuts import HttpResponse
from PerfectCrm import settings
from django.urls import reverse
@login_required
def homework_detail(request,studyrecord_id):
    studyrecord_obj = models.StudyRecord.objects.get(id=studyrecord_id)
    homework_attach_objs = models.HomeworkAttachment.objects.filter(study_record=studyrecord_obj).all()

    if request.method == "POST":
        # 判断是否是ajax发送过来的数据，这里用来判断是否是上传图片
        if request.is_ajax():
            if request.POST.get("type") == "delete":
                file_name = request.POST.get("file_name")
                file_path = os.path.join(settings.STUDYRECORD_DATA, studyrecord_id, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    models.HomeworkAttachment.objects.filter(attachment_url=file_path).delete()
                    return HttpResponse("文件%s删除成功" % file_name);
                else:
                    return HttpResponse(file_name + "不存在")

            file_obj = request.FILES.get("file")
            if not os.path.exists(settings.STUDYRECORD_DATA):
                os.mkdir(settings.STUDYRECORD_DATA)
            # 相当于mkdir -P
            os.makedirs(os.path.join(settings.STUDYRECORD_DATA, studyrecord_id), exist_ok=True)
            file_path = os.path.join(settings.STUDYRECORD_DATA, studyrecord_id, file_obj.name)
            with open(file_path, "wb") as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

            if(models.HomeworkAttachment.objects.filter(study_record=studyrecord_obj,attachment_url=file_path)).all():
                attach_obj = models.HomeworkAttachment.objects.get(study_record=studyrecord_obj,attachment_url=file_path)
            else:
                attach_obj = models.HomeworkAttachment.objects.create(study_record=studyrecord_obj,
                                                                             attachment_url=file_path)
            attach_url = reverse("homework_attachment_download",
                                 kwargs={"studyrecord_id": studyrecord_obj.id, "attach_id": attach_obj.id})
            print("-------------",attach_url)
            return HttpResponse(attach_url)

    return render(request,"student/homework_detail.html",{"studyrecord_obj":studyrecord_obj,"homework_attach_objs":homework_attach_objs})

from django.http import StreamingHttpResponse
@login_required
def homework_attachment_download(request,studyrecord_id,attach_id):
    '''
        文件下载
    '''

    def file_iterator(file_path, chunk_size=512):
        with open(file_path,"rb") as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    homework_attachment_obj = models.HomeworkAttachment.objects.get(id=attach_id)
    file_path = homework_attachment_obj.attachment_url
    file_name = os.path.basename(file_path)
    response = StreamingHttpResponse(file_iterator(file_path))

    response['Content-Type'] = 'application/octet-stream'
    disposition = 'attachment;filename="%s"' % file_name
    response['Content-Disposition'] = disposition.encode(encoding="utf-8")
    return response
# -*- coding:utf-8 -*-
from django.http import Http404
from django.contrib.contenttypes.models import ContentType

from view_record.models import Recorder, ViewNum

# 阅读计数装饰器，需要指定模型类
def record_view(model_type):
    def __record_view(func):
        def warpper(request, blog_id):
            try:
                obj = model_type.objects.get(id = blog_id)
            except model_type.DoesNotExist:
                raise Http404
 
            # 获取模型的名称做为Cookie的键名
            model_name = str(model_type).split("'")[1]
            cookie_name = "%s_%s_readed" % (model_name.split('.')[-1], blog_id)
 
            # 判断Cookie是否存在
            if cookie_name not in request.COOKIES:
                # 添加明细记录
                recorder = Recorder(content_object = obj)
                recorder.ip_address = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", None))
                if request.user.is_authenticated:
                    recorder.user = request.user 
                else:
                    recorder.user = None
                recorder.save()
 
                # 总记录+1
                obj_type = ContentType.objects.get_for_model(obj)
                viewers = ViewNum.objects.filter(content_type = obj_type, object_id = obj.id)
 
                if viewers.count() > 0:
                    viewer = viewers[0]
                else:
                    viewer = ViewNum(content_type = obj_type, object_id = obj.id)
                viewer.view_num += 1
                viewer.save()
 
            # 执行原来的方法(响应页面)
            response = func(request, blog_id)
 
            # 添加临时cookie，关闭浏览器之后就过期
            response.set_cookie(cookie_name, "True")
            return response # 返回内容给前端
        return warpper
    return __record_view
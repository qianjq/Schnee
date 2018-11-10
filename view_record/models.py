from django.db import models

# 引用ContentType 相关模块
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.contrib.auth.models import User

# Create your models here.
class Recorder(models.Model):
    """阅读的明细记录"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        ct_field="content_type",
        fk_field="object_id"
    )

    # 普通字段
    # 记录IP地址
    ip_address = models.CharField(max_length=15)

    # 记录User， 这里可能没有登陆用户，因此可允许为空
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    # 记录阅读的时间
    view_time = models.DateTimeField(auto_now=True)

class ViewNum(models.Model):
    """阅读数量记录"""
    # contentType 设置
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        ct_field="content_type",
        fk_field="object_id"
    )

    # 普通字段，阅读总数量
    view_num = models.IntegerField(default=0)

    def __unicode__(self):
        return u'<%s:%s> %s' % (self.content_type, self.object_id, self.view_num)


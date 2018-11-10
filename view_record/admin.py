from django.contrib import admin
from view_record.models import Recorder, ViewNum

# Register your models here.
class RecorderAdmin(admin.ModelAdmin):
    """view recorder admin"""
    list_display = ('content_type', 'object_id', 'ip_address', 'view_time')
    ordering = ('-view_time', )

class ViewNumAdmin(admin.ModelAdmin):
    """view num admin"""
    list_display = ('content_type', 'object_id', 'view_num')

admin.site.register(Recorder, RecorderAdmin)
admin.site.register(ViewNum, ViewNumAdmin)

from django.contrib import admin
from blog.models import *

# Register your models here.
class BlogAdmin(admin.ModelAdmin):
    """blog admin"""
    list_display=('id', 'caption', 'read_num','view_num_count', 'publish_time', 'update_time', 'recommend')
 
    def view_num_count(self, obj):
        """自定义显示字段"""
        return sum(map(lambda x: x.view_num,obj.view_num.all()))

admin.site.register(Tag)
admin.site.register(Blog, BlogAdmin)
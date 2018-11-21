from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from datetime import datetime
# Create your models here.


class Group(models.Model):
    name = models.CharField(max_length = 40, default="example group")
    intro = models.CharField(max_length = 200, default="no introduce")
    date_added = models.DateTimeField(auto_now_add = True)
    owner = models.ForeignKey(User, on_delete = models.CASCADE, related_name='group_owner')
    members = models.ManyToManyField(User)
    profile = ProcessedImageField(upload_to='group/img', default='group/img/default.jpg', 
        processors=[ResizeToFill(750, 465)],  format='JPEG', options={'quality': 60})
    
    def __str__(self):
        return self.name

class Diary(models.Model):
    content = MarkdownxField()
    date_added = models.DateTimeField(auto_now_add = True)
    group = models.ForeignKey(Group,on_delete = models.CASCADE)
    diary_log = models.TextField(default=str(date_added) + "  Create diary")
    
    def __str__(self):
        return self.content
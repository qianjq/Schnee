from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation

from simditor.fields import RichTextField
from markdownx.models import MarkdownxField

from view_record.models import ViewNum

# Create your models here.
class Tag(models.Model):
    tag_name = models.CharField(max_length=20, default='')
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tag_name


class Blog(models.Model):
    caption = models.CharField(max_length=50, default='')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    content = RichTextField()
    
    read_num = models.IntegerField(default=0)
    publish_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    recommend = models.BooleanField(default=False)

    view_num = GenericRelation(ViewNum)

    def __str__(self):
        return u'%s %s %s' % (self.caption, self.author, self.publish_time)

    class Meta:
        ordering = ['-publish_time']

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    publish_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=400, default='')

    class Meta:
        ordering = ['-publish_time']

    def __str__(self):
        return u'%s %s %s' % (self.blog, self.author, self.content)
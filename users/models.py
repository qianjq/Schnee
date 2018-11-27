from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

# Create your models here.

class UserInfo(models.Model):
    GENDER_CHOICES = (
        (u'M', u'Male'),
        (u'F', u'Female'),
    )
    LANGUAGE_CHOICES = (
        (u'E', u'English'),
        (u'C', u'简体中文'),
    )
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name="user")
    nickname = models.CharField(max_length=20, default="Undefined")
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default="Male")
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="English")
    intro = models.CharField(max_length=200, default="hello world")
    email = models.EmailField(max_length=70, blank=True, default="Undefined@example.com")
    friends = models.ManyToManyField(User, blank=True, related_name="user_friends")
    profile = ProcessedImageField(upload_to='user/img', default='user/img/default.jpg', 
        processors=[ResizeToFill(500, 500)],  format='JPEG', options={'quality': 60})
    unread_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.nickname

class Message(models.Model):
    TYPE_CHOICES = (
        (u'M', u'Message'),
        (u'F', u'Friend_Invitation'),
        (u'G', u'Group_Invitation'),
    )
    sender = models.ForeignKey(User, related_name="sender_msg", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="receiver_msg", on_delete=models.CASCADE)
    text = MarkdownxField(max_length=2000)
    id_content = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    msg_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default="Message")
    is_deal = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    sender_del = models.BooleanField(default=False)
    receiver_del = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text

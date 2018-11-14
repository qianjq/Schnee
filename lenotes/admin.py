from django.contrib import admin
# Register your models here.
from lenotes.models import Group, Diary

admin.site.register(Group)
admin.site.register(Diary)

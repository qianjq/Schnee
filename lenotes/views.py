from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, StreamingHttpResponse, HttpResponse
from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from lenotes.models import Group, Diary
from users.models import UserInfo, Message
from lenotes.forms import GroupForm, DiaryForm
from helper.update_data import update_userInfo_unread_count

from datetime import datetime
from PIL import Image

import json

def check_user(request, group, flag): 
    """
        flag 0 检查是不是群主
        flag 1 检查是不是群成员
    """
    if flag == 0 and request.user != group.owner:
        raise Http404
    elif flag == 1 and request.user not in group.members.all():
        raise Http404

def index(request):
    if request.user.is_authenticated:
        update_userInfo_unread_count(request.user)
    return render(request, 'lenotes/index.html')

@login_required
def home(request):
    """显示个人信息的主界面"""
    try:
        userinfo = UserInfo.objects.get(user=request.user) 
    except ObjectDoesNotExist:
        userinfo = UserInfo.objects.create(user=request.user)
    if userinfo.nickname.strip() == "":
        userinfo.nickname = "Undefined"
    if userinfo.gender.strip() == "M":
        userinfo.gender = "Male"
    else:
        userinfo.gender = "Female"
    if userinfo.email.strip() == "":
        userinfo.email = "Undefined@example.com"
    if userinfo.intro.strip() == "":
        userinfo.intro = "No introduce"
    update_userInfo_unread_count(request.user)
    groups = Group.objects.filter(members__id = request.user.id).order_by('date_added')
    context = {
        'userinfo': userinfo,
        'groups' : groups,
    }
    return render(request, 'lenotes/home.html', context)

@login_required
def group(request, group_id):
    """群组主页"""
    year, month = datetime.now().year, datetime.now().month
    return HttpResponseRedirect(reverse('lenotes:diary_month', args=[group_id, year, month]))

@login_required   
def diary_month(request, group_id, year, month):
    group = Group.objects.get(id=group_id)
    check_user(request, group, 1)
    tdiary = group.diary_set.order_by('-date_added')
    createJudge = False
    if tdiary.count() == 0:
        createJudge = True
    elif tdiary[0].date_added.year != datetime.now().year or tdiary[0].date_added.month != datetime.now().month\
        or tdiary[0].date_added.day != datetime.now().day:
        createJudge = True  

    diarys = group.diary_set.filter(date_added__year=year, date_added__month = month).order_by('date_added')
    lastMonth, lastYear, nextMonth, nextYear = 0, 0, 0, 0
    
    lastMonthJudge = False if tdiary.count() == 0 or month == tdiary[len(tdiary)-1].date_added.month else True
    nextMonthJudge = False if month == datetime.now().month else True
    
    if month==1:
        lastMonth = 12
        lastYear = year-1
    else:
        lastMonth = month-1
        lastYear = year
    
    if month==12:
        nextMonth = 1
        nextYear = year+1
    else:
        nextMonth = month+1
        nextYear = year
    
    context = {
        'group': group, 
        'diarys': diarys, 
        'lastMonth': lastMonth,
        'lastYear': lastYear,
        'nextMonth': nextMonth,
        'nextYear': nextYear,
        'createJudge': createJudge,
        'lastMonthJudge': lastMonthJudge,
        'nextMonthJudge': nextMonthJudge,
    }
   
    return render(request, 'lenotes/group_diary_md.html', context)

@login_required
def manage(request, group_id):
    """修改群组资料，邀请功能，管理用户"""
    if request.method != 'POST':
        try:
            group = Group.objects.get(id=group_id)
        except ObjectDoesNotExist:
            group = Group.objects.create(id=group_id)
        group_form = GroupForm(instance = group)
    else:
        group_form = GroupForm(request.POST, request.FILES)
        if group_form.is_valid():
            try:
                group = Group.objects.get(id=group_id)
            except ObjectDoesNotExist:
                group = Group.objects.create(id=group_id)
        group.name = group_form.cleaned_data["name"]
        group.intro = group_form.cleaned_data["intro"]
        myprofile = request.FILES.get('profile',None)
        if myprofile:
            if group.profile.name != 'group/img/default.jpg':
                group.profile.delete()
            group.profile = myprofile
        group.save()
        return HttpResponseRedirect(reverse('lenotes:group', args=[group.id]))
    
    check_user(request, group, 1)
    members = group.members.all()
    memberInfos = []
    for member in members:
        info = UserInfo.objects.get(user=member)
        memberInfos.append(info)
    context = {
        'group': group,
        'memberInfos': memberInfos,
        'group_form': group_form,
    }
    return render(request, 'lenotes/manage.html' , context)


@login_required
def del_member(request, group_id, info_id):
    group = Group.objects.get(id=group_id)
    check_user(request, group, 0)
    info = UserInfo.objects.get(id=info_id)
    group.members.remove(info.user)
    msg = "You have been removed from group: " + group.name
    Message.objects.create(sender=group.owner, text=msg, receiver=info.user)
    return HttpResponseRedirect(reverse('lenotes:manage', args=[group_id]))


@login_required
def send_invite(request, group_id):
    if request.method == 'POST':
        try:
            receiver = User.objects.get(username=request.POST['invite_id'])
        except ObjectDoesNotExist:
            context = {'group_id': group_id}
            return render(request, 'home/userIsNotExist.html' , context)
        group = Group.objects.get(id = group_id)
        check_user(request, group, 0)
        msg = request.user.username + " invite you to join Group: " + group.name + "."
        Message.objects.create(sender=request.user, receiver=receiver, 
            text=msg, id_content=group.id, msg_type="Group_Invitation")
        
        return HttpResponseRedirect(reverse('lenotes:manage', args=[group_id]))
        
    group = Group.objects.get(id = group_id)
    check_user(request, group, 0)
    context = { 'group_id': group_id }
    return render(request, 'lenotes/send_invite.html', context)

@login_required
def new_group(request):
    if request.method != 'POST':
        form = GroupForm()
    else:
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.owner = request.user
            new_group.save()
            new_group.members.add(request.user)
            return HttpResponseRedirect(reverse('lenotes:home'))
    
    context = { 'form': form }
    return render(request, 'lenotes/new_group.html', context)

@login_required
def del_group(request, group_id):
    """删除当前群组"""
    del_group = Group.objects.get(id=group_id)
    check_user(request, del_group, 0)
    members = del_group.members.all()
    senderName = del_group.owner.username + "(Group Owner)"
    for member in members:
        msg = "The group: " + del_group.name + " have been deleted."
        Message.objects.create(sender=senderName, text=msg, receiver=member)
    del_group.delete()
    return HttpResponseRedirect(reverse('lenotes:home'))

@login_required
def new_diary(request, group_id):
    group = Group.objects.get(id = group_id)
    check_user(request, group, 1)
    if request.method != 'POST':
        form = DiaryForm()
    else:
        form = DiaryForm(data = request.POST)
        if form.is_valid():
            new_diary = form.save(commit=False)
            new_diary.group = group
            new_diary.save()
            return HttpResponseRedirect(reverse('lenotes:group', args=[group_id]))
    context = {'group': group, 'form': form}
    return render(request, 'lenotes/new_diary.html', context)

@login_required
def edit_diary_md(request, diary_id):
    """编辑既有条目"""
    diary = Diary.objects.get(id=diary_id)
    group = diary.group
    check_user(request, group, 1)
    if request.method != 'POST':
        form = DiaryForm(instance=diary)
    else:
        form = DiaryForm(instance=diary, data=request.POST)
        if form.is_valid():
            # diary_log 需要重新处理
            diary.diary_log = (str(datetime.now()) + "  Editor: " + str(request.user) + "\r\n") + diary.diary_log
            form.save()
            return HttpResponseRedirect(reverse('lenotes:diary_month', 
                args=[group.id, diary.date_added.year, diary.date_added.month]))
    context = {
        'diary': diary, 
        'group': group, 
        'form': form
    }
    return render(request, 'lenotes/edit_diary_md.html', context)

@login_required
def diary_log(request, diary_id):
    diary_log = Diary.objects.get(id=diary_id).diary_log
    context = { 'diary_log': diary_log }
    return render(request, 'lenotes/diary_log.html', context)


def lenotes_intro(request):
    return render(request, 'lenotes/lenotes_intro.html')
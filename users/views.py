from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from users.models import UserInfo, Message
from users.forms import InfoForm, MessageForm

from lenotes.models import Group, Diary 

from helper.update_data import update_userInfo_unread_count

import re

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home:home'))
    if request.method != 'POST':
        request.session['login_from'] = request.META.get('HTTP_REFERER', '/') 
        form = AuthenticationForm(request)
    else:
        form = AuthenticationForm(request, data = request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect(request.session['login_from'])
    context = {'form': form}
    return render(request, 'users/login.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home:home'))


def register(request):
    if request.method != 'POST':
        user_form = UserCreationForm()
        info_form = InfoForm()
    else:
        user_form = UserCreationForm(data=request.POST)
        info_form = InfoForm(request.POST, request.FILES)
        if user_form.is_valid():
            new_user = user_form.save()
            new_info = info_form.save(commit=False)
            new_info.user = new_user
            new_info.save()
            authenticated_user = authenticate(username = new_user.username,
            password = request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('home:home'))
    
    context = {
        'user_form': user_form,
        'info_form': info_form,    
    }
    return render(request, 'users/register.html' , context)


@login_required
def settings(request):
    if request.method != 'POST':
        try:
            info = UserInfo.objects.get(user = request.user)
        except ObjectDoesNotExist:
            info = UserInfo.objects.create(user = request.user)
        info_form = InfoForm(instance = info)
        context = {
            'info_form': info_form,
            'info': info,
        }
        return render(request, 'users/settings.html' , context)
    else:
        info_form = InfoForm(request.POST)
        if info_form.is_valid():
            try:
                info = UserInfo.objects.get(user = request.user)
            except ObjectDoesNotExist:
                info = UserInfo.objects.create(user = request.user)
        info.nickname = info_form.cleaned_data["nickname"]
        info.gender = info_form.cleaned_data["gender"]
        info.language = info_form.cleaned_data["language"]
        info.email = info_form.cleaned_data["email"]
        info.intro = info_form.cleaned_data["intro"]
        myprofile = request.FILES.get('profile',None)
        if myprofile:
            if info.profile.name != 'user/img/default.jpg' :
                info.profile.delete()
            info.profile = myprofile
        info.save()
        return HttpResponseRedirect(reverse('home:home'))


@login_required
def reset_password(request):
    if request.method != 'POST':
        form = PasswordChangeForm(user = request.user)
    else:
        form = PasswordChangeForm(user = request.user, data = request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect(reverse('users:reset_done'))
    context = { 'form': form }
    return render(request, 'users/reset_password.html', context)


def reset_done(request):
    return render(request, 'users/reset_done.html')


@login_required
def notice(request):
    """ 用于接收信息以及查看发送的消息 """
    update_userInfo_unread_count(request.user)
    inbox_messages = Message.objects.filter(receiver=request.user).filter(receiver_del=False).order_by('-date_added')
    outbox_messages = Message.objects.filter(sender=request.user).filter(sender_del=False).order_by('-date_added')
    context = {
        'inbox_messages': inbox_messages,
        'outbox_messages': outbox_messages
    }
    return render(request, 'users/mailbox.html', context)


@login_required
def send_message(request):
    """ 向某人发送信息 / 支持群发 """
    if request.method != 'POST':
        form = MessageForm()
    else:
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            tmp_message = form.save(commit=False)
            username_list = request.POST['receiver_id']
            username_list = re.split(r'[\s\,\;]+', username_list)
            for username in username_list:                
                if username.strip() == "":
                    continue
                try:
                    receiver_user = User.objects.get(username=username.strip())
                except ObjectDoesNotExist:
                    return render(request, 'users/userIsNotExist.html')
                Message.objects.create(text=tmp_message.text, receiver=receiver_user, sender=request.user)
            return HttpResponseRedirect(reverse('home:home'))
    
    info_id = UserInfo.objects.get(user=request.user).id
    context = {'form': form, 'info_id': info_id}
    return render(request, 'users/send_message.html', context)


@login_required
def set_as_read(request, message_id):
    """ 标记消息为已读 """
    try:
        message = Message.objects.get(id=message_id)
        if request.user == message.receiver:
            message.is_read = True
            message.save()
    finally:
        return HttpResponseRedirect(reverse('users:notice'))


@login_required
def read_message(request, message_id):
    """ 阅读消息完整内容并回复 """
    message = Message.objects.get(id=message_id)
    if request.user == message.receiver:
        message.is_read = True
        message.save()

    if request.method != 'POST':
        form = MessageForm()
    else:
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.receiver = message.sender
            new_message.sender = request.user
            new_message.save()
            return HttpResponseRedirect(reverse('users:notice'))
    
    context = {'message': message, 'form': form}
    return render(request, 'users/read_message.html', context)


@login_required
def receiver_del_message(request, message_id):
    """ 收信者删除当前消息，若发送者已删除，则删除该信息 """
    try:
        del_message = Message.objects.get(id=message_id)
        del_message.receiver_del = True
        del_message.is_read = True
        if del_message.sender_del == True:
            del_message.delete()
        else:
            del_message.save()
    finally:
        return HttpResponseRedirect(reverse('users:notice'))


@login_required
def sender_del_message(request, message_id):
    """ 发送者删除当前消息，若收信者已删除，则删除该信息 """
    try:
        del_message = Message.objects.get(id=message_id)
        del_message.sender_del = True
        if del_message.receiver_del == True:
            del_message.delete()
        else:
            del_message.save()
    finally:
        return HttpResponseRedirect(reverse('users:notice'))

@login_required
def rece_deal_mult_msg(request):
    msg_ids = request.POST.getlist("checkbox_rece")
    if 'delete_rece_msg' in request.POST:
        for idx in msg_ids:
            receiver_del_message(request, int(idx))
    elif 'set_as_read' in request.POST:
        for idx in msg_ids:
            set_as_read(request, int(idx))
    return HttpResponseRedirect(reverse('users:notice'))

@login_required
def send_deal_mult_msg(request):
    del_msg_ids = request.POST.getlist("checkbox_send")
    for idx in del_msg_ids:
        sender_del_message(request, int(idx))
    return HttpResponseRedirect(reverse('users:notice'))



@login_required
def add_as_friend(request, user_id):
    """点击+向对方发送添加好友的请求"""
    receiver = User.objects.get(id = user_id)
    user = UserInfo.objects.get(user = request.user)
    context = { 'isSuccess': False }

    if receiver not in user.friends.all():
        context['isSuccess'] = True
        text = str(request.user.username) + " wants to add you as a friend."
        Message.objects.create(sender=request.user, receiver=receiver, text=text, msg_type="Friend_Invitation")    
    
    return render(request, 'users/send_invi.html', context)


@login_required
def deal_invi(request, message_id, accept):
    """ 根据邀请类型分别处理好友邀请以及群组邀请 """
    message = Message.objects.get(id=message_id)
    message.is_deal = True
    message.save()

    # 处理好友邀请
    if message.msg_type == "Friend_Invitation":
        if accept:
            send_user_info = UserInfo.objects.get(user=message.sender)
            rece_user_info = UserInfo.objects.get(user=request.user)
            send_user_info.friends.add(request.user)
            rece_user_info.friends.add(message.sender)
            text = "I have added you as friend."
        else:
            text = "Sorry, I refuse to add you as friend."
        
        Message.objects.create(sender=request.user, receiver=message.sender, text=text)
        context = {
            "username": message.sender.username, 
            "accept":accept
        }

        return render(request, 'users/deal_invi.html', context)

    
    # 处理群组邀请
    elif message.msg_type == "Group_Invitation":
        group = Group.objects.get(id=message.id_content)
        if accept:
            group.members.add(request.user)
            text = request.user.username + " accpeted to join in group:" + group.name
        else:
            text = request.user.username + " refused to join in group:" + group.name
        Message.objects.create(sender=request.user, receiver=group.owner, text=text)
        return HttpResponseRedirect(reverse('users:notice'))

    # 测试用的错误报告
    else:
        raise "Error msg type"


@login_required
def delete_friend(request, username):
    del_user = User.objects.get(username=username)
    user_info = UserInfo.objects.get(user=request.user)
    user_info.friends.remove(del_user)
    # user_info.save()
    del_user_info = UserInfo.objects.get(user=del_user)
    del_user_info.friends.remove(request.user)
    # del_user_info.save()
    text = "Sorry, you have be delete by " + str(request.user.username) + "."
    Message.objects.create(sender=request.user, receiver=del_user, text=text)
    return HttpResponseRedirect(reverse('users:settings'))


@login_required
def quit_group(request, group_id):
    """ 退出当前群组 """
    try:
        group = Group.objects.get(id=group_id)
        group.members.remove(request.user)
        msg = request.user.username + " quit the group: " + group.name
        Message.objects.create(sender=request.user, text=msg, receiver=group.owner)
    finally:
        return HttpResponseRedirect(reverse('lenotes:home'))
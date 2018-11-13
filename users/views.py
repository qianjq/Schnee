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
        # print(request.POST)
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
        info.name = info_form.cleaned_data["nickname"]
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
    context = {
        'form': form, 
    }
    return render(request, 'users/reset_password.html', context)

def reset_done(request):
    return render(request, 'users/reset_done.html')

@login_required
def notice(request):
    """用于接收信息以及查看发送的消息"""
    update_userInfo_unread_count(request.user)
    inbox_messages = Message.objects.filter(receiver=request.user).filter(receiver_del=False).order_by('-date_added')
    outbox_messages = Message.objects.filter(sender=request.user.username).filter(sender_del=False).order_by('-date_added')
    context = {
        'inbox_messages': inbox_messages,
        'outbox_messages': outbox_messages
    }
    return render(request, 'users/mailbox.html', context)

@login_required
def send_message(request):
    """
        向某人发送信息 / 支持群发
        To Do: 改进多联系人方式的输入，考虑使用正则表达式
    """
    if request.method != 'POST':
        form = MessageForm()
    else:
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            tmp_message = form.save(commit=False)
            username_list = request.POST['receiver_id'].split(';')
            if username_list[-1] == ' ':
                username_list = username_list[:-1]
            for username in username_list:
                try:
                    receiver_user = User.objects.get(username=username.strip())
                    print(receiver_user)
                except ObjectDoesNotExist:
                    return render(request, 'users/userIsNotExist.html')
                Message.objects.create(text=tmp_message.text, receiver=receiver_user, sender=request.user.username)
            return HttpResponseRedirect(reverse('home:home'))
    
    info_id = UserInfo.objects.get(user=request.user).id
    context = {'form': form, 'info_id': info_id}
    return render(request, 'users/send_message.html', context)

@login_required
def set_as_read(request, message_id):
    """标记消息为已读"""
    try:
        message = Message.objects.get(id=message_id)
        message.is_Read = True
        message.save()
    finally:
        return HttpResponseRedirect(reverse('users:notice'))

@login_required
def read_message(request, message_id):
    """阅读消息完整内容并回复"""
    message = Message.objects.get(id=message_id)
    if request.user == message.receiver:
        message.is_Read = True
        message.save()

    if request.method != 'POST':
        form = MessageForm()
    else:
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = Message.objects.get(id=message_id)
            receiver_user = User.objects.get(username=message.sender)
            new_message = form.save(commit=False)
            new_message.receiver = receiver_user
            new_message.sender = request.user.username
            new_message.save()
            # Message.objects.create(sender=request.user.username, receiver=receiver_user, text=content)
            return HttpResponseRedirect(reverse('users:notice'))
    
    context = {'message': message, 'form': form}
    return render(request, 'users/read_message.html', context)


@login_required
def receiver_del_message(request, message_id):
    try:
        del_message = Message.objects.get(id=message_id)
        del_message.receiver_del = True
        if del_message.sender_del == True:
            del_message.delete()
        else:
            del_message.save()
    finally:
        return HttpResponseRedirect(reverse('users:notice'))
        
@login_required
def sender_del_message(request, message_id):
    """删除当前消息"""
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
def add_as_friend(request, user_id):
    """点击+向对方发送添加好友的请求"""
    receiver = User.objects.get(id = user_id)
    text = str(request.user.username) + " wants to add you as a friend" + \
         " [Accept](http://127.0.0.1:8000/users/accept_as_friend/" + str(request.user.id) + ") " + \
         " [Refuse](http://127.0.0.1:8000/users/refuse_as_friend/" + str(request.user.id) + ")."
    Message.objects.create(sender=str(request.user.username), receiver=receiver, text=text, msg_type="Invivation")
    return render(request, 'users/send_invi_success.html')

@login_required
def accept_as_friend(request, user_id):
    send_user = User.objects.get(id=user_id)
    send_user_info = UserInfo.objects.get(user=send_user)
    rece_user_info = UserInfo.objects.get(user=request.user)
    send_user_info.friends.add(request.user)
    send_user_info.save()
    rece_user_info.friends.add(send_user)
    rece_user_info.save()
    text = "I have added you as friend."
    Message.objects.create(sender=str(request.user.username), receiver=send_user, text=text)
    context = {"username": send_user.username}
    return render(request, 'users/accept_as_friend.html', context)

@login_required
def refuse_as_friend(request, user_id):
    send_user = User.objects.get(id=user_id)
    text = "Sorry, I refuse to add you as friend."
    Message.objects.create(sender=str(request.user.username), receiver=send_user, text=text)
    context = {"username": send_user.username}
    return render(request, 'users/refuse_as_friend.html', context)

@login_required
def delete_friend(request, username):
    del_user = User.objects.get(username=username)
    user_info = UserInfo.objects.get(user=request.user)
    user_info.friends.remove(del_user)
    user_info.save()
    del_user_info = UserInfo.objects.get(user=del_user)
    del_user_info.friends.remove(request.user)
    del_user_info.save()
    text = "Sorry, you have be delete by " + str(request.user.username) + "."
    Message.objects.create(sender=str(request.user.username), receiver=del_user, text=text)
    return HttpResponseRedirect(reverse('users:settings'))

@login_required
def deal_invi(request, group_id, accept):
    """处理邀请"""
    if accept:
        group = Group.objects.get(id=group_id)
        group.members.add(request.user)
        msg = request.user.username + " accpeted to join in group:" + group.name
    else:
        msg = request.user.username + " refused to join in group:" + group.name
    Message.objects.create(sender=request.user.username, text=msg, receiver=group.owner)
    return HttpResponseRedirect(reverse('users:notice'))

@login_required
def quit_group(request, group_id):
    """退出当前群聊"""
    try:
        group = Group.objects.get(id=group_id)
        group.members.remove(request.user)
        msg = request.user.username + " quit the group: " + group.name
        Message.objects.create(sender=request.user.username + "(Group Member)", text=msg, receiver=group.owner)
    finally:
        return HttpResponseRedirect(reverse('lenotes:home'))
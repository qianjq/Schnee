from users.models import UserInfo, Message

def update_userInfo_unread_count(user):
    userinfo = UserInfo.objects.get(user=user) 
    userinfo.unread_count = Message.objects.filter(receiver=user, is_Read=False).count()
    userinfo.save()
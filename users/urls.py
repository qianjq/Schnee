from django.urls import path

from users import views
app_name = 'users'

urlpatterns = [
    #login
    path('login/', views.login_view, name = 'login'),
    #logout
    path('logout/', views.logout_view, name = 'logout'),
    #register
    path('register/', views.register, name = 'register'),

    path('notice/', views.notice, name = 'notice'),

    path('settings/', views.settings, name = 'settings'),

    path('reset_password/', views.reset_password, name = 'reset_password'),

	path('reset_done/', views.reset_done, name = 'reset_done'),

    path('send_message/', views.send_message, name = 'send_message'),

    path('set_as_read/<int:message_id>', views.set_as_read, name = 'set_as_read'),

    path('read_message/<int:message_id>', views.read_message, name = 'read_message'),

    path('receiver_del_message/<int:message_id>', views.receiver_del_message, name = 'receiver_del_message'),

    path('sender_del_message/<int:message_id>', views.sender_del_message, name = 'sender_del_message'),

    path('add_as_friend/<int:user_id>', views.add_as_friend, name = 'add_as_friend'),

    path('accept_as_friend/<int:user_id>', views.accept_as_friend, name = 'accept_as_friend'),

    path('refuse_as_friend/<int:user_id>', views.refuse_as_friend, name = 'refuse_as_friend'),

    path('delete_friend/<str:username>', views.delete_friend, name = 'delete_friend'),
]


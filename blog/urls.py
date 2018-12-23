from django.urls import path
import django.views

from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_index, name = 'blog_index'),
    
    path('blog/<int:item_id>', views.blog_show, name = 'blog_show'),

    path('search_blog/', views.search_blog, name = 'search_blog'),

    path('tag_blogs/<str:tag_name>', views.tag_blogs, name = 'tag_blogs'),

    path('recommend_blogs/', views.recommend_blogs, name = 'recommend_blogs'),

    path('new_comment/<int:blog_id>', views.new_comment, name = 'new_comment'),

    path('delete_comment/<int:blog_id>/<int:comment_id>', views.delete_comment, name = 'delete_comment'),

    path('new_reply/<int:blog_id>/<int:comment_id>', views.new_reply, name = 'new_reply'),

    path('delete_reply/<int:blog_id>/<int:reply_id>', views.delete_reply, name = 'delete_reply'),
]
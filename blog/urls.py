from django.urls import path
import django.views

from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_index, name = 'blog_index'),
    
    path('blog/<int:blog_id>', views.blog_show, name = 'blog_show'),

    path('new_blog/', views.new_blog, name = 'new_blog'),

    path('delete_blog/<int:blog_id>', views.delete_blog, name = "delete_blog"),

    path('edit_blog/<int:blog_id>', views.edit_blog, name = 'edit_blog'),

    path('manage_tags/', views.manage_tags, name = 'manage_tags'),

    path('new_tag/', views.new_tag, name = 'new_tag'),

    path('delete_tag/<int:tag_id>', views.delete_tag, name = 'delete_tag'),

    path('edit_tag/<int:tag_id>', views.edit_tag, name = 'edit_tag'),

    path('new_comment/<int:blog_id>', views.new_comment, name = 'new_comment'),

    path('delete_comment/<int:blog_id>/<int:comment_id>', views.delete_comment, name = 'delete_comment'),

    path('blog_search/', views.blog_search, name = 'blog_search'),
]
from django.urls import path
import django.views

from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_index, name = 'blog_index'),
    
    path('blog/<int:blog_id>', views.blog_show, name = 'blog_show'),

    path('new_blog/', views.new_blog, name = 'new_blog'),

    path('edit_blog/<int:blog_id>', views.edit_blog, name = 'edit_blog'),
]
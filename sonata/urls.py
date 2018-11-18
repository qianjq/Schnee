from django.urls import path
import django.views

from sonata import views

app_name = 'sonata'

urlpatterns = [
    path('', views.article_index, name = 'article_index'),
    
    path('sonata/<int:item_id>', views.article_show, name = 'article_show'),

    path('new_comment/<int:article_id>', views.new_comment, name = 'new_comment'),

    path('delete_comment/<int:article_id>/<int:comment_id>', views.delete_comment, name = 'delete_comment'),

    path('search_article/', views.search_article, name = 'search_article'),

    path('tag_articles/<str:tag_name>', views.tag_articles, name = 'tag_articles'),

    path('recommend_articles/', views.recommend_articles, name = 'recommend_articles'),
]
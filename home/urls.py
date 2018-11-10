from django.urls import path
import django.views

from home import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('home/', views.home, name = 'home'),
    path('gallery/', views.gallery, name = 'gallery'),
    path('lab/', views.lab, name = 'lab'),
    path('about/', views.about, name = 'about'),
    path('test_page/', views.test_page, name = 'test_page'),
    path('developing/', views.developing, name = 'developing'),
]
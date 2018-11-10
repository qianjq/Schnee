from django.urls import path
import django.views

from lab import views

app_name = 'lab'

urlpatterns = [
    # path('lab_index/', views.lab_index, name = 'lab_index'),
    path('text_embed/', views.text_embed, name = 'text_embed'),

    path('hash_verify/', views.hash_verify, name = 'hash_verify'),

    path('download_hash_verify/', views.download_hash_verify, name = 'download_hash_verify'),

    path('character_image/', views.character_image, name = 'character_image'),
]
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views


app_name = 'edi'
urlpatterns = [
    path('', views.indexView, name='index'),
    path('upload/', views.upload_file, name='upload'),
    path('uploaded_file_details/', views.uploaded_file_details,
         name='uploaded_file_details'),
]

urlpatterns += staticfiles_urlpatterns()

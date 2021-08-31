from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views


app_name = 'edi'
urlpatterns = [
    path('', views.indexView, name='index'),
    path('upload/', views.upload_file, name='upload'),
    path('uploadPdf/', views.UploadPdfView.as_view(), name='uploadPdf'),
    path('uploadPdf/success/<str:files>/<str:out>', views.UploadPdfSuccessView.as_view(),
         name='uploadPdfSuccess'),
    path('uploaded_file_details/', views.uploaded_file_details,
         name='uploaded_file_details'),
]

urlpatterns += staticfiles_urlpatterns()

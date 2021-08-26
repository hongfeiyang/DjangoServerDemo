import os
from edi.models import Document
from django.core.files.uploadedfile import UploadedFile
from .forms import DocumentForm
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from typing import List
from .edi_util import process_edi_files
from django.conf import settings


def indexView(request):
    return render(request, 'edi/index.html')


def upload_file(request: HttpRequest):

    def remove_existing_files():
        documents = Document.objects.all()
        for doc in documents:
            doc.delete()

        edi_output_dir = os.path.join(settings.BASE_DIR, 'edi/static/edi')
        for f in os.listdir(edi_output_dir):
            if f.endswith(".xlsx"):
                os.remove(os.path.join(edi_output_dir, f))

    def handle_uploaded_files(files: List[UploadedFile]):
        for file in files:
            fileInstance = Document(document=file)
            fileInstance.save()
        process_edi_files()

    if request.method == 'POST':
        remove_existing_files()
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_files(request.FILES.getlist('document'))
            return redirect(reverse('edi:uploaded_file_details'))
    else:
        form = DocumentForm()
    return render(request, 'edi/upload.html', {'form': form})


def uploaded_file_details(request: HttpRequest):
    files = Document.objects.all()
    edi_base_url = os.path.join(settings.STATIC_URL, 'edi')
    edi_urls = [(os.path.join(edi_base_url, f), f) for f in os.listdir(
        os.path.join(settings.BASE_DIR, 'edi/static/edi'))]
    return render(request, 'edi/uploaded_file_details.html', {'files': files, 'edi_urls': edi_urls})

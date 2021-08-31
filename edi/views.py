import os

from django.http.response import HttpResponseBadRequest, HttpResponseNotFound
from edi.models import Document
from django.core.files.uploadedfile import UploadedFile
from .forms import DocumentForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from typing import List
from .edi_util import process_edi_files
from django.conf import settings
from django.views import generic
from .forms import PdfForm
import ast
from .pdf_util import pdf_cat

EDI_STATIC_DIR = f'{settings.BASE_DIR}/edi/static'
EDI_MEDIA_DIR = f'{settings.MEDIA_ROOT}'


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


class UploadPdfView(generic.FormView):
    template_name = 'pdf/pdf_upload.html'
    form_class = PdfForm

    uploadedFileNames = []
    outputFileName = 'output.pdf'

    def saveUploadedFile(self, f: UploadedFile):
        with open(f'{EDI_MEDIA_DIR}/pdf/{f.name}', 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def post(self, request, *args, **kwargs):
        # clear names array since this class instance is retained for each request
        # so that we wont get previous files merged
        self.uploadedFileNames = []
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files: List[UploadedFile] = request.FILES.getlist('data')
        if form.is_valid():
            for f in files:
                self.saveUploadedFile(f)
                self.uploadedFileNames.append(f.name)
            try:
                pdf_cat([f'{EDI_MEDIA_DIR}/pdf/{i}' for i in self.uploadedFileNames],
                        f'{EDI_STATIC_DIR}/pdf/{self.outputFileName}')
                return self.form_valid(form)
            except Exception as e:
                print(e)
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form) -> HttpResponse:
        # so the final url will be in the form of /success/['file1', 'file2']
        return redirect('edi:uploadPdfSuccess', files=self.uploadedFileNames, out=self.outputFileName)


class UploadPdfSuccessView(generic.TemplateView):
    template_name = 'pdf/pdf_upload_success.html'
    files = None  # names of the files that has been uploaded
    outputFile = None  # name of the merged pdf file

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        fileNames = kwargs['files']
        out = kwargs['out']
        self.outputFile = os.path.join(
            settings.STATIC_URL, f'pdf/{out}')
        try:
            # try parse files as a list of file names (str)
            self.files = ast.literal_eval(fileNames)
            if type(self.files) is not list:
                return HttpResponseBadRequest("Bad Request: can not parse the list of file names given")
        except Exception as e:
            print(e)
            return HttpResponseBadRequest("Bad Request")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = self.files
        context['output'] = self.outputFile
        return context

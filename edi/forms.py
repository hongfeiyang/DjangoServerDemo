from django import forms
from .models import Document
from django.core.validators import FileExtensionValidator


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document', )
        widgets = {
            'document': forms.ClearableFileInput(attrs={'multiple': True, 'accept': '.csv'})
        }


class PdfForm(forms.Form):

    data = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True, 'accept': 'application/pdf'}), validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

from django import forms
from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document', )
        widgets = {
            'document': forms.ClearableFileInput(attrs={'multiple': True})
        }

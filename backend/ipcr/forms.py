from django import forms

from backend.documents.models import Docs201Files


class Upload201AttachmentForm(forms.ModelForm):
    class Meta:
        model = Docs201Files
        fields = ['file']
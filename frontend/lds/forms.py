from django import forms

from frontend.lds.models import LdsRso


class UploadAttachmentFormLDS(forms.ModelForm):
    class Meta:
        model = LdsRso
        fields = ['attachment']
        widgets = {'attachment': forms.FileInput(attrs={'class': 'form-control border-0 px-0'})}

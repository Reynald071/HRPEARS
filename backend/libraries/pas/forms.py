from django import forms

from backend.models import Section, Empprofile


class SectionForm(forms.ModelForm):
    sec_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Section
        exclude = ('upload_by',)


class UploadPictureForm(forms.ModelForm):
    class Meta:
        model = Empprofile
        fields = ['picture']

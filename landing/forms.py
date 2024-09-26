from django import forms
from landing.models import AppStatus


class AppStatusForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = AppStatus
        exclude = ()

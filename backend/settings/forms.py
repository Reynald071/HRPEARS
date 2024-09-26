from django import forms

from backend.models import AuthPermission


class PermissionForm(forms.ModelForm):
    description = forms.CharField(required=False, widget=forms.Textarea)
    badge = forms.FileField(required=False)

    class Meta:
        model = AuthPermission
        fields = ['name', 'description', 'badge']
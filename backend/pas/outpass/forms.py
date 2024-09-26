from django import forms

from frontend.models import Locatorslip


class AttachmentOutpassForm(forms.ModelForm):
    class Meta:
        model = Locatorslip
        exclude = ('outpass', 'date', 'status',)

    attachment = forms.FileField()
    attachment.widget.attrs.update({'class': 'btn-file'})

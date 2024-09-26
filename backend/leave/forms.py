from django import forms

from backend.libraries.leave.models import LeaveApplication, CTDORequests


class LeaveAttachmentForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['file']


class CTDOAttachmentForm(forms.ModelForm):
    class Meta:
        model = CTDORequests
        fields = ['file']
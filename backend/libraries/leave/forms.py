from django import forms

from backend.libraries.leave.models import LeaveType, LeaveSubtype, LeaveSpent, LeavePermissions
from backend.models import Empstatus


class LeavetypeForm(forms.ModelForm):
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = LeaveType
        fields = '__all__'


class LeavesubtypeForm(forms.ModelForm):
    is_others = forms.BooleanField(label='Is Others', initial=False, required=False)
    has_reason = forms.BooleanField(label='Has Reason', initial=False, required=False)
    with_days = forms.BooleanField(label='With Days', initial=False, required=False)
    status = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super(LeavesubtypeForm, self).__init__(*args, **kwargs)
        self.fields['leavetype'].required = False
        self.fields['leavetype'].label = 'Leave Type (Optional)'
        self.fields['description'].required = False
        self.fields['description'].label = 'Description (Optional)'

    class Meta:
        model = LeaveSubtype
        fields = '__all__'


class LeavespentForm(forms.ModelForm):
    status = forms.BooleanField(required=False, initial=True)
    is_specify = forms.BooleanField(required=False, initial=False)
    has_reason = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(LeavespentForm, self).__init__(*args, **kwargs)
        self.fields['leavesubtype'].label = 'Leave Sub-Type'

    class Meta:
        model = LeaveSpent
        fields = '__all__'


class LeavePermissionsForm(forms.ModelForm):
    empstatus_id = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(LeavePermissionsForm, self).__init__(*args, **kwargs)
        self.fields['empstatus_id'].label = 'Employee Status'
        self.fields['empstatus_id'].choices = [
            (empstatus.pk, empstatus.name) for empstatus in Empstatus.objects.filter(status=1)
        ]
        self.fields['empstatus_id'].initial = ''

    class Meta:
        model = LeavePermissions
        fields = '__all__'

from django import forms

from backend.models import Empprofile, Aoa, Section


class EmployeeForm(forms.ModelForm):
    date_vacated = forms.DateField(label='Date Vacated', widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    dateofcreation_pos = forms.DateField(label="Date of Creation of Position",
                                         widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    dateof_designation = forms.DateField(label="Date of Designation", widget=forms.TextInput(attrs={'type': 'date'}),
                                         required=False)
    dateof_orig_appointment = forms.DateField(label="Date of Orig Appointment",
                                              widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    dateof_last_promotion = forms.DateField(label="Date of Last Promotion",
                                            widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    remarks_vacated = forms.CharField(label="Remarks Vacated", required=False,
                                      widget=forms.Textarea(attrs={'rows': '3'}))
    aoa = forms.ModelChoiceField(label="Area of Assignment", queryset=Aoa.objects.filter(status=True), required=True)

    class Meta:
        model = Empprofile
        fields = '__all__'
        labels = {
            'fundsource': 'Fund Source',
            'id_number': 'ID Number',
            'item_number': 'Item Number',
            'account_number': 'Account Number',
            'empstatus': 'Employment Status',
            'step_inc': 'Step Increment',
            'mode_access': 'Mode of Accession',
            'mode_sep': 'Mode of Separation',
            'specialorder_no': 'Special Order No.',
            'salary_grade': 'Salary Grade',
            'salary_rate': 'Salary Rate',
            'plantilla_psipop': 'Plantilla PSIPOP',
        }
        exclude = ('pi', 'picture')

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.fields['id_number'].widget.attrs['readonly'] = True
        self.fields['position'].queryset = self.fields['position'].queryset.exclude(status=0)
        self.fields['empstatus'].queryset = self.fields['empstatus'].queryset.exclude(status=0)
        self.fields['project'].queryset = self.fields['project'].queryset.exclude(status=0)
        self.fields['fundsource'].queryset = self.fields['fundsource'].queryset.exclude(status=0)
        self.fields['mode_access'].queryset = self.fields['mode_access'].queryset.exclude(status=0)
        self.fields['mode_sep'].queryset = self.fields['mode_sep'].queryset.exclude(status=0)


class UploadCoverPhotoForm(forms.ModelForm):
    class Meta:
        model = Empprofile
        fields = ['cover_photo']

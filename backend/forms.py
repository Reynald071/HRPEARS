from django import forms
from datetime import datetime

from frontend.models import TravelOrder, Bloodtype, Civilstatus, Countries, Degree, Educationlevel, Hobbies, \
    Eligibility, Nonacad, Organization, Province, Trainingtitle, Trainingtype, City, Brgy, Downloadableforms, School, \
    Honors, Claims, Mot, Faqs, DownloadableformsClass, DownloadableformsSopClass
from .awards.models import Badges, Classification, Awlevels, Awcategory, Awards
from .calendar.models import CalendarType
from .documents.models import DtsDoctype, Docs201Type, DocsIssuancesType
from .libraries.grievance.models import GrievanceClassification, GrievanceMedia, GrievanceStatus, \
    GrievanceRoaAttachments
from .models import Fundsource, Aoa, Project, Empstatus, Position, Empprofile, Division, Section, Designation, \
    HrppmsModeaccession, HrppmsModeseparation, DirectoryDetailType, PositionVacancy, PayrollIncharge


class AccessionForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = HrppmsModeaccession
        exclude = ('uploadedby',)


class SeparationForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = HrppmsModeseparation
        exclude = ('uploadedby',)


class FundsourceForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Fundsource
        exclude = ('upload_by',)


class AoaForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off', 'placeholder': 'e.g. Province - City'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Aoa
        exclude = ('upload_by',)


class ProjectForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Project
        exclude = ('upload_by',)


class EmpstatusForm(forms.ModelForm):
    name = forms.CharField(label="Employment Status",
                           widget=forms.TextInput(
                               attrs={'autocomplete': 'off'}))
    acronym = forms.CharField(label="Acronym", required=False,
                              widget=forms.TextInput(
                                  attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Empstatus
        exclude = ('upload_by',)


class PositionForm(forms.ModelForm):
    name = forms.CharField(label="Position Title",
                           widget=forms.TextInput(
                               attrs={'autocomplete': 'off'}))
    acronym = forms.CharField(label="Acronym", required=False,
                              widget=forms.TextInput(
                                  attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Position
        exclude = ('upload_by',)


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = TravelOrder
        exclude = ('rito', 'date', 'status', 'approved_by')


class BloodtypeForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off', 'class': 'b-r-sm'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Bloodtype
        exclude = ('upload_by',)


class CivilstatusForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Civilstatus
        exclude = ('upload_by',)


class CountriesForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Countries
        exclude = ('upload_by',)


class DegreeForm(forms.ModelForm):
    degree_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    degree_acronym = forms.CharField(required=False,
                                     widget=forms.TextInput(
                                         attrs={'autocomplete': 'off'}))
    deg_status = forms.BooleanField(required=False, initial=True, label="Status")

    class Meta:
        model = Degree
        exclude = ('pi',)


class EducationLevelForm(forms.ModelForm):
    lev_name = forms.CharField(label="Name",
                               widget=forms.TextInput(
                                   attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Educationlevel
        exclude = ('upload_by',)


class HobbiesForm(forms.ModelForm):
    hob_name = forms.CharField(label="Hobby Name",
                               widget=forms.TextInput(
                                   attrs={'autocomplete': 'off'}))
    hob_status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Hobbies
        exclude = ('pi',)


class EligibilityForm(forms.ModelForm):
    CHOICES = (
        ("", ""),
        (1, "1st Level"),
        (2, "2nd Level"),
        (3, "3rd Level"),
    )
    el_name = forms.CharField(label="Eligibility",
                              widget=forms.TextInput(
                                  attrs={'autocomplete': 'off'}))
    el_level = forms.ChoiceField(label="Level of Eligibility", choices=CHOICES)
    el_status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Eligibility
        exclude = ('pi',)


class NonacadForm(forms.ModelForm):
    na_name = forms.CharField(label="Non Academic/Recognition",
                              widget=forms.TextInput(
                                  attrs={'autocomplete': 'off'}))
    na_status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Nonacad
        exclude = ('pi',)


class OrganizationForm(forms.ModelForm):
    org_name = forms.CharField(label="Organization Name",
                               widget=forms.TextInput(
                                   attrs={'autocomplete': 'off'}))
    org_status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Organization
        exclude = ('pi',)


class ProvinceForm(forms.ModelForm):
    name = forms.CharField(label="Name",
                           widget=forms.TextInput(
                               attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Province
        exclude = ('upload_by',)


class TrainingtitleForm(forms.ModelForm):
    tt_name = forms.CharField(label="Training Title",
                              widget=forms.TextInput(
                                  attrs={'autocomplete': 'off'}))
    tt_status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Trainingtitle
        exclude = ('pi',)


class TrainingtypeForm(forms.ModelForm):
    type_name = forms.CharField(label="Name",
                                widget=forms.TextInput(
                                    attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Trainingtype
        exclude = ('upload_by',)


class CityForm(forms.ModelForm):
    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    code = forms.CharField(label="Code",
                           widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = City
        labels = {
            'prov_code': 'Province',
        }
        exclude = ('upload_by',)


class BrgyForm(forms.ModelForm):
    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'b-r-sm'}))
    status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Brgy
        labels = {
            'city_code': 'City',
        }
        exclude = ('upload_by',)


class DownloadableForm(forms.ModelForm):
    qs = [(x.id, x.name) for x in DownloadableformsClass.objects.filter(status=True)]
    CHOICES = [['', '']] + qs
    title = forms.CharField(label="Name",
                            widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(label="Status", required=False, initial=True)
    classes = forms.ModelChoiceField(queryset=DownloadableformsClass.objects.filter(status=True), empty_label='',
                                     required=True)
    # classes = forms.ChoiceField(choices=CHOICES, label="Classification")

    class Meta:
        model = Downloadableforms
        fields = ('title', 'filename', 'status', 'classes',)


class FaqsForm(forms.ModelForm):
    title = forms.CharField(label="Title")
    question = forms.CharField(label="Question")
    link = forms.CharField(label="Embed Code")
    answer = forms.CharField(label="Answer", required=False,
                             widget=forms.Textarea(attrs={'style': 'resize:vertical'}))
    isactive = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Faqs
        fields = ('title', 'question', 'link', 'answer', 'isactive')


class SchoolForm(forms.ModelForm):
    school_name = forms.CharField(label="School Name",
                                  widget=forms.TextInput(
                                      attrs={'autocomplete': 'off'}))
    school_acronym = forms.CharField(label="Acronym",
                                     widget=forms.TextInput(
                                         attrs={'autocomplete': 'off'}))
    school_status = forms.BooleanField(label='Status', required=False, initial=True)

    class Meta:
        model = School
        exclude = ('pi',)


class HonorsForm(forms.ModelForm):
    hon_name = forms.CharField(label="Scholarship / Academic Honor",
                               widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    hon_status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Honors
        exclude = ('pi',)


class TOClaimsForm(forms.ModelForm):
    name = forms.CharField(label="Claim Title",
                           widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Claims
        exclude = ('upload_by',)


class TOMotForm(forms.ModelForm):
    name = forms.CharField(label="Means of Transportation Title",
                           widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Mot
        exclude = ('upload_by',)


class DivisionsForm(forms.ModelForm):
    div_name = forms.CharField(label='Division Name',
                               widget=forms.TextInput(
                                   attrs={'autocomplete': 'off'}
                               )
                               )

    div_acronym = forms.CharField(label='Acronym', required=False,
                                  widget=forms.TextInput(
                                      attrs={'autocomplete': 'off'}
                                  )
                                  )

    div_chief_id = forms.CharField(label='Division Chief', required=False,
                                   widget=forms.TextInput(
                                       attrs={'autocomplete': 'off', 'class': 'typeahead_2 filter_employee'}
                                   )
                                   )

    is_alternate = forms.BooleanField(label="Alternate Head", required=False, initial=True)

    class Meta:
        model = Division
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(DivisionsForm, self).__init__(*args, **kwargs)
        if 'div_chief_id' in self.initial:
            if self.initial['div_chief_id'] is not None:
                emp = Empprofile.objects.filter(id=self.initial['div_chief_id']).first()
                if emp is not None:
                    self.initial['div_chief_id'] = "[{}] {} {}".format(emp.id_number, emp.pi.user.first_name.upper(),
                                                                       emp.pi.user.last_name.upper())


class SectionsForm(forms.ModelForm):
    sec_name = forms.CharField(label='Section Name',
                               widget=forms.TextInput(
                                   attrs={'autocomplete': 'off'}
                               )
                               )
    sec_acronym = forms.CharField(label='Acronym', required=False,
                                  widget=forms.TextInput(
                                      attrs={'autocomplete': 'off'}))
    sec_head_id = forms.CharField(label='Section Head', required=False,
                                  widget=forms.TextInput(
                                      attrs={'autocomplete': 'off', 'class': 'typeahead_2 filter_employee'}
                                  )
                                  )

    class Meta:
        model = Section
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(SectionsForm, self).__init__(*args, **kwargs)
        self.fields['div'].label = 'Division'
        if 'sec_head_id' in self.initial:
            if self.initial['sec_head_id'] is not None:
                emp = Empprofile.objects.filter(id=self.initial['sec_head_id']).first()
                if emp is not None:
                    self.initial['sec_head_id'] = "[{}] {} {}".format(emp.id_number, emp.pi.user.first_name.upper(),
                                                                      emp.pi.user.last_name.upper())


class BadgesForm(forms.ModelForm):
    name = forms.CharField(label="Badge Name")
    url = forms.FileField(label="Badge Icon")

    class Meta:
        model = Badges
        exclude = ('uploaded_by',)


class ClassificationForm(forms.ModelForm):
    name = forms.CharField(label="Classification Name")
    shortname = forms.CharField(label="Short Name")
    status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Classification
        exclude = ('uploaded_by',)


class AwlevelsForm(forms.ModelForm):
    name = forms.CharField(label="Level Name")

    class Meta:
        model = Awlevels
        exclude = ('uploaded_by', 'status',)


class AwcategoriesForm(forms.ModelForm):
    name = forms.CharField(label="Category Name")
    needs_title = forms.BooleanField(required=False, initial=True, label="Needs an extra field for title?")

    class Meta:
        model = Awcategory
        exclude = ('uploaded_by', 'status', 'icon')


class AwardsForm(forms.ModelForm):
    year = forms.IntegerField(initial=datetime.now().year)
    is_nomination = forms.BooleanField(label="Needs Nomination", required=False, initial=True)
    status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = Awards
        exclude = ('uploaded_by',)


class DesignationForm(forms.ModelForm):
    name = forms.CharField(label="Designation")
    emp_id = forms.CharField(label='Employee', required=False,
                             widget=forms.TextInput(
                                 attrs={'autocomplete': 'off', 'class': 'typeahead_2 filter_employee'}
                             )
                             )

    class Meta:
        model = Designation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(DesignationForm, self).__init__(*args, **kwargs)
        if 'emp_id' in self.initial:
            if self.initial['emp_id'] is not None:
                emp = Empprofile.objects.filter(id=self.initial['emp_id']).first()
                if emp is not None:
                    self.initial['emp_id'] = "[{}] {} {}".format(emp.id_number, emp.pi.user.first_name.upper(),
                                                                 emp.pi.user.last_name.upper())


class GrievanceClassificationForm(forms.ModelForm):
    name = forms.CharField(label="Classification Name")
    is_active = forms.BooleanField(required=False, initial=True, label="Status")

    class Meta:
        model = GrievanceClassification
        exclude = ()


class GrievanceMediaForm(forms.ModelForm):
    name = forms.CharField(label="Medium Name")
    is_active = forms.BooleanField(required=False, initial=True, label="Status")

    class Meta:
        model = GrievanceMedia
        exclude = ()


class GrievanceStatusForm(forms.ModelForm):
    name = forms.CharField(label="Status Name")
    is_active = forms.BooleanField(required=False, initial=True, label="Status")
    need_emp = forms.BooleanField(required=False, initial=True, label="Need target employee?")

    class Meta:
        model = GrievanceStatus
        exclude = ()


class GrievanceRoaAttachmentsForm(forms.ModelForm):
    class Meta:
        model = GrievanceRoaAttachments
        fields = ['attachment']
        widgets = {'attachment': forms.FileInput(attrs={'id': 'files', 'required': True,
                                                        'multiple': True, 'class': 'form-control',
                                                        'style': 'padding: 5px 12px 5px 5px !important;'})}


class DirectoryDetailTypeForm(forms.ModelForm):
    type = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = DirectoryDetailType
        exclude = ('upload_by',)


class CalendarTypeForm(forms.ModelForm):
    CHOICES = (
        ("", ""),
        (0, "Public"),
        (1, "Private"),
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    scope = forms.ChoiceField(label="Scope", choices=CHOICES)
    status = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = CalendarType
        exclude = ('upload_by',)


class CalendarTypeFormPrivate(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))

    class Meta:
        model = CalendarType
        exclude = ('upload_by', 'scope', 'status')


class DtsDoctypeForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'autocomplete': 'off'}))
    is_active = forms.BooleanField(required=False, initial=True, label="Status")

    class Meta:
        model = DtsDoctype
        exclude = ('upload_by',)


class SopClassForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    acronym = forms.CharField(
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True, label="Status")

    class Meta:
        model = DownloadableformsSopClass
        exclude = ('upload_by',)


class DlClassForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    acronym = forms.CharField(
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True, label="Status")

    class Meta:
        model = DownloadableformsClass
        exclude = ('upload_by', 'is_sop')


class Docs201TypeForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True, label="Status")

    class Meta:
        model = Docs201Type
        exclude = ('upload_by',)


class IssuancesTypeForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    status = forms.BooleanField(required=False, initial=True, label="Status")

    class Meta:
        model = DocsIssuancesType
        exclude = ('upload_by',)


class PositionVacancyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PositionVacancyForm, self).__init__(*args, **kwargs)
        self.fields['position'].queryset = Position.objects.filter(status=1)
        self.fields['aoa'].queryset = Aoa.objects.filter(status=1)
        self.fields['filled_by_id'].label = 'Filled By'
        if 'filled_by_id' in self.initial:
            if self.initial['filled_by_id'] is not None:
                emp = Empprofile.objects.filter(id=self.initial['filled_by_id']).first()
                if emp is not None:
                    self.initial['filled_by_id'] = "[{}] {} {}".format(emp.id_number, emp.pi.user.first_name.upper(),
                                                                       emp.pi.user.last_name.upper())

    filled_by_id = forms.CharField(label='Filled By', required=False,
                                   widget=forms.TextInput(
                                    attrs={'autocomplete': 'off', 'class': 'typeahead_2 filter_employee'}
                                   )
                                   )

    status = forms.BooleanField(required=False, initial=True, label="Status")

    class Meta:
        model = PositionVacancy
        exclude = ()


class PayrollInchargeForm(forms.ModelForm):
    status = forms.BooleanField(label="Status", required=False, initial=True)

    class Meta:
        model = PayrollIncharge
        exclude = ('upload_by_id', 'color', 'emp')


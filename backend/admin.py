import re

from django.contrib import admin
from django.apps import apps

from backend.models import Empprofile, AuthUser, Personalinfo, DirectoryDetailType, Fundsource, Aoa, Project, Position,\
    Empstatus, Division, Section, Designation, HrppmsModeaccession, HrppmsModeseparation, PayrollIncharge, AuthPermission
from backend.awards.models import Badges, Classification, Awlevels, Awcategory, Awards
from backend.calendar.models import CalendarType
from backend.documents.models import Docs201Type, DocsIssuancesType
from backend.pas.clearance.models import ClearanceContent
from backend.libraries.leave.models import LeaveType, LeaveSubtype, LeaveSpent, LeavePermissions
from frontend.models import Bloodtype, Civilstatus, Hobbies, DownloadableformsClass, DownloadableformsSopClass, Honors,\
    Degree, Educationlevel, Eligibility, School, Brgy, City, Province, Countries, Organization, Nonacad, Trainingtitle,\
    Trainingtype, Claims, Mot

from backend.forms import BadgesForm, ClassificationForm, AwlevelsForm, AwcategoriesForm, CalendarTypeForm, \
    BloodtypeForm, \
    CivilstatusForm, HobbiesForm, DirectoryDetailTypeForm, Docs201TypeForm, DlClassForm, IssuancesTypeForm, \
    SopClassForm, \
    HonorsForm, DegreeForm, EducationLevelForm, EligibilityForm, SchoolForm, FundsourceForm, AoaForm, ProjectForm, \
    PositionForm, EmpstatusForm, DivisionsForm, SectionsForm, DesignationForm, AccessionForm, SeparationForm, BrgyForm, \
    CityForm, ProvinceForm, CountriesForm, OrganizationForm, NonacadForm, TrainingtitleForm, TrainingtypeForm, \
    TOClaimsForm, TOMotForm, AwardsForm
from backend.libraries.leave.forms import LeavetypeForm, LeavesubtypeForm, LeavespentForm, LeavePermissionsForm

from landing.models import AppStatus
from landing.forms import AppStatusForm


@admin.register(Awards)
class AwardsAdmin(admin.ModelAdmin):
    list_display = ["name", "level", "year", "display_class_shortname", "category", "status", "uploaded_by"]
    search_fields = ["name", "level__name", "year", "category__name"]
    ordering = ["-year", "name"]
    form = AwardsForm

    def save_model(self, request, obj, form, change):
        obj.uploaded_by_id = request.session['emp_id']
        super().save_model(request, obj, form, change)


@admin.register(Badges)
class BadgesAdmin(admin.ModelAdmin):
    list_display = ["name", "uploaded_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = BadgesForm

    def save_model(self, request, obj, form, change):
        obj.uploaded_by_id = request.session['emp_id']
        super().save_model(request, obj, form, change)


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ["name", "shortname", "display_status", "uploaded_by"]
    search_fields = ["name", "shortname"]
    ordering = ["name"]
    form = ClassificationForm

    def save_model(self, request, obj, form, change):
        obj.uploaded_by_id = request.session['emp_id']
        super().save_model(request, obj, form, change)


@admin.register(Awlevels)
class AwlevelsAdmin(admin.ModelAdmin):
    list_display = ["name", "display_status", "uploaded_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = AwlevelsForm

    def save_model(self, request, obj, form, change):
        obj.uploaded_by_id = request.session['emp_id']
        super().save_model(request, obj, form, change)


@admin.register(Awcategory)
class AwcategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "needs_title", "display_status", "uploaded_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = AwcategoriesForm

    def save_model(self, request, obj, form, change):
        obj.uploaded_by_id = request.session['emp_id']
        super().save_model(request, obj, form, change)


@admin.register(CalendarType)
class CalendarTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "display_color", "display_scope", "status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = CalendarTypeForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['emp_id']
        super().save_model(request, obj, form, change)


@admin.register(Bloodtype)
class BloodtypeAdmin(admin.ModelAdmin):
    list_display = ["name", "display_status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = BloodtypeForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['emp_id']
        super().save_model(request, obj, form, change)


@admin.register(Civilstatus)
class CivilstatusAdmin(admin.ModelAdmin):
    list_display = ["name", "display_status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = CivilstatusForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['emp_id']
        super().save_model(request, obj, form, change)


@admin.register(Hobbies)
class HobbiesAdmin(admin.ModelAdmin):
    list_display = ["hob_name", "display_status", "pi"]
    search_fields = ["hob_name"]
    ordering = ["hob_name"]
    form = HobbiesForm

    def save_model(self, request, obj, form, change):
        obj.pi_id = request.session['pi_id']
        super().save_model(request, obj, form, change)


@admin.register(DirectoryDetailType)
class DirectoryDetailTypeAdmin(admin.ModelAdmin):
    list_display = ["type", "status", "upload_by"]
    search_fields = ["type"]
    ordering = ["type"]
    form = DirectoryDetailTypeForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Docs201Type)
class Docs201TypeAdmin(admin.ModelAdmin):
    list_display = ["name", "display_status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = Docs201TypeForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(DownloadableformsClass)
class DownloadableformsClassAdmin(admin.ModelAdmin):
    list_display = ["name", "acronym", "status", "is_sop", "upload_by"]
    search_fields = ["name", "acronym"]
    ordering = ["name"]
    form = DlClassForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(DocsIssuancesType)
class DocsIssuancesTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "display_status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = IssuancesTypeForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(DownloadableformsSopClass)
class DownloadableformsSopClassAdmin(admin.ModelAdmin):
    list_display = ["name", "acronym", "status", "upload_by"]
    search_fields = ["name", "acronym"]
    ordering = ["name"]
    form = SopClassForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Honors)
class HonorsAdmin(admin.ModelAdmin):
    list_display = ["hon_name", "display_status", "pi"]
    search_fields = ["hon_name"]
    ordering = ["hon_name"]
    form = HonorsForm

    def save_model(self, request, obj, form, change):
        obj.pi_id = request.session['pi_id']
        super().save_model(request, obj, form, change)


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ["degree_name", "degree_acronym", "display_status", "pi"]
    search_fields = ["degree_name", "degree_acronym"]
    ordering = ["degree_name"]
    form = DegreeForm

    def save_model(self, request, obj, form, change):
        obj.pi_id = request.session['pi_id']
        super().save_model(request, obj, form, change)


@admin.register(Educationlevel)
class EducationlevelAdmin(admin.ModelAdmin):
    list_display = ["lev_name", "display_status", "upload_by"]
    search_fields = ["lev_name"]
    ordering = ["lev_name"]
    form = EducationLevelForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Eligibility)
class EligibilityAdmin(admin.ModelAdmin):
    list_display = ["el_name", "display_level", "display_status", "pi"]
    search_fields = ["el_name"]
    ordering = ["el_name"]
    form = EligibilityForm

    def save_model(self, request, obj, form, change):
        obj.pi_id = request.session['pi_id']
        super().save_model(request, obj, form, change)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["school_name", "school_acronym", "display_status", "pi"]
    search_fields = ["school_name", "school_acronym"]
    ordering = ["school_name"]
    form = SchoolForm

    def save_model(self, request, obj, form, change):
        obj.pi_id = request.session['pi_id']
        super().save_model(request, obj, form, change)


@admin.register(Fundsource)
class FundsourceAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = FundsourceForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Aoa)
class AoaAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = AoaForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = ProjectForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ["name", "display_status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = PositionForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Empstatus)
class EmpstatusAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = EmpstatusForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ["div_name", "div_acronym", "display_div_chief"]
    search_fields = ["div_name", "div_acronym"]
    ordering = ["div_name"]
    form = DivisionsForm

    def save_model(self, request, obj, form, change):
        if obj.div_chief_id:
            div_chief_id = re.split('\[|\]', obj.div_chief_id)
            name = Empprofile.objects.values('id').filter(id_number=div_chief_id[1]).first()
            obj.div_chief_id = name['id']
        else:
            obj.div_chief_id = None
        super().save_model(request, obj, form, change)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ["sec_name", "sec_acronym", "display_is_alternate", "display_sec_head", "div"]
    search_fields = ["sec_name", "sec_acronym"]
    ordering = ["sec_name"]
    form = SectionsForm

    def save_model(self, request, obj, form, change):
        if obj.sec_head_id:
            sec_head_id = re.split('\[|\]', obj.sec_head_id)
            name = Empprofile.objects.values('id').filter(id_number=sec_head_id[1]).first()
            obj.sec_head_id = name['id']
        else:
            obj.sec_head_id = None
        super().save_model(request, obj, form, change)


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ["name", "display_emp"]
    search_fields = ["name"]
    ordering = ["name"]
    form = DesignationForm

    def save_model(self, request, obj, form, change):
        if obj.emp_id:
            emp_id = re.split('\[|\]', obj.emp_id)
            name = Empprofile.objects.values('id').filter(id_number=emp_id[1]).first()
            obj.emp_id = name['id']
        else:
            obj.emp_id = None
        super().save_model(request, obj, form, change)


@admin.register(HrppmsModeaccession)
class AccessionAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "uploadedby"]
    search_fields = ["name"]
    ordering = ["name"]
    form = AccessionForm

    def save_model(self, request, obj, form, change):
        obj.uploadedby_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(HrppmsModeseparation)
class AccessionAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "uploadedby"]
    search_fields = ["name"]
    ordering = ["name"]
    form = SeparationForm

    def save_model(self, request, obj, form, change):
        obj.uploadedby_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "display_status"]
    search_fields = ["name"]
    ordering = ["name"]
    form = LeavetypeForm


@admin.register(LeaveSubtype)
class LeaveSubtypeAdmin(admin.ModelAdmin):
    list_display = ["name", "leavetype", "order", "display_status"]
    search_fields = ["name", "leavetype__name"]
    ordering = ["order", "name"]
    form = LeavesubtypeForm


@admin.register(LeaveSpent)
class LeaveSpentAdmin(admin.ModelAdmin):
    list_display = ["name", "leavesubtype", "display_status"]
    search_fields = ["name", "leavesubtype__name"]
    ordering = ["name"]
    form = LeavespentForm


@admin.register(LeavePermissions)
class LeavePermissionsAdmin(admin.ModelAdmin):
    list_display = ["leavesubtype", "display_empstatus"]
    search_fields = ["leavesubtype__name"]
    ordering = ["leavesubtype__name"]
    form = LeavePermissionsForm


@admin.register(Brgy)
class BrgyAdmin(admin.ModelAdmin):
    list_display = ["name", "city_code", "display_status", "upload_by"]
    search_fields = ["name", "city_code__name"]
    ordering = ["name"]
    form = BrgyForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "prov_code", "display_status", "upload_by"]
    search_fields = ["name", "prov_code__name"]
    ordering = ["name"]
    form = CityForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ["name", "display_status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = ProvinceForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Countries)
class CountriesAdmin(admin.ModelAdmin):
    list_display = ["name", "display_status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = CountriesForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["org_name", "display_status", "pi"]
    search_fields = ["org_name"]
    ordering = ["org_name"]
    form = OrganizationForm

    def save_model(self, request, obj, form, change):
        obj.pi_id = request.session['pi_id']
        super().save_model(request, obj, form, change)


@admin.register(Nonacad)
class NonacadAdmin(admin.ModelAdmin):
    list_display = ["na_name", "display_status", "pi"]
    search_fields = ["na_name"]
    ordering = ["na_name"]
    form = NonacadForm

    def save_model(self, request, obj, form, change):
        obj.pi_id = request.session['pi_id']
        super().save_model(request, obj, form, change)


@admin.register(Trainingtitle)
class TrainingtitleAdmin(admin.ModelAdmin):
    list_display = ["tt_name", "display_status", "pi"]
    search_fields = ["tt_name"]
    ordering = ["tt_name"]
    form = TrainingtitleForm

    def save_model(self, request, obj, form, change):
        obj.pi_id = request.session['pi_id']
        super().save_model(request, obj, form, change)


@admin.register(Trainingtype)
class TrainingtypeAdmin(admin.ModelAdmin):
    list_display = ["type_name", "display_status", "upload_by"]
    search_fields = ["type_name"]
    ordering = ["type_name"]
    form = TrainingtypeForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Claims)
class ClaimsAdmin(admin.ModelAdmin):
    list_display = ["name", "display_status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = TOClaimsForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(Mot)
class MotAdmin(admin.ModelAdmin):
    list_display = ["name", "display_status", "upload_by"]
    search_fields = ["name"]
    ordering = ["name"]
    form = TOMotForm

    def save_model(self, request, obj, form, change):
        obj.upload_by_id = request.session['user_id']
        super().save_model(request, obj, form, change)


@admin.register(AppStatus)
class AppStatusAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "display_status"]
    search_fields = ["name"]
    ordering = ["order"]
    form = AppStatusForm


class PayrollInchargeAdmin(admin.ModelAdmin):
    list_display = ["name", "status"]
    search_fields = ["name"]


admin.site.register(PayrollIncharge, PayrollInchargeAdmin)
admin.site.register(Empprofile)
admin.site.register(AuthUser)
admin.site.register(Personalinfo)
admin.site.register(ClearanceContent)
admin.site.register(AuthPermission)

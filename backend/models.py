import datetime
import os
from django.conf import settings
from django.db.models import OneToOneField
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
from django.contrib import admin
from django_resized import ResizedImageField


class SMSLogs(models.Model):
    message = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=11, blank=True, null=True)
    date_sent = models.DateTimeField(default=timezone.now)
    receiver = models.ForeignKey('Empprofile', models.DO_NOTHING, blank=True, null=True, default=None)
    emp_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_sms_logs'


class RestFrameworkTrackingApirequestlog(models.Model):
    requested_at = models.DateTimeField()
    response_ms = models.PositiveIntegerField()
    path = models.CharField(max_length=200)
    remote_addr = models.CharField(max_length=39)
    host = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    query_params = models.TextField(blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    status_code = models.PositiveIntegerField(blank=True, null=True)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)
    view = models.CharField(max_length=200, blank=True, null=True)
    view_method = models.CharField(max_length=27, blank=True, null=True)
    errors = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rest_framework_tracking_apirequestlog'


class DjangoLoggedInUser(models.Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, related_name='logged_in_user', on_delete=models.CASCADE)
    session_key = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'django_logged_in_user'
        

class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    badge = models.FileField(upload_to='badges/%Y/%m', blank=True, null=True)

    def count_user(self):
        return AuthUserUserPermissions.objects.filter(permission_id=self.id).count()

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'auth_permission'


@receiver(models.signals.pre_save, sender=AuthPermission)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = AuthPermission.objects.get(pk=instance.pk).badge
    except AuthPermission.DoesNotExist:
        return False

    new_file = instance.badge
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=255)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=64, blank=True, null=True)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    title = models.CharField(max_length=150, blank=True, null=True)

    @property
    def mobile_no(self):
        return Personalinfo.objects.filter(user_id=self.id).first().mobile_no

    @property
    def employee_id(self):
        return Empprofile.objects.filter(pi__user_id=self.id).first().id

    def get_first_name_title(self):
        return self.first_name.title()

    def get_last_name_title(self):
        return self.last_name.title()

    def get_middle_name_title(self):
        return self.middle_name.title() if self.middle_name else ""

    @property
    def get_fullname(self):
        from frontend.models import Personalinfo
        data = Personalinfo.objects.filter(user_id=self.id).first()
        suffix_name = ""
        if data:
            suffix_name = data.ext.name if data.ext else ""

        return "{}{}{} {}{}".format('{}  '.format(self.title) if self.title else '',
                                    self.first_name.title(), " " + self.middle_name[:1] + "." if self.middle_name else '', self.last_name.title(), ' ' + suffix_name if suffix_name else '')

    @property
    def get_fullname_formatted(self):
        from frontend.models import Personalinfo
        data = Personalinfo.objects.filter(user_id=self.id).first()
        suffix_name = ""
        if data:
            suffix_name = data.ext.name if data.ext else ""

        return "{}, {} {}{}".format(self.last_name.title(), self.first_name.title(), self.middle_name[:1] + "." if self.middle_name else '', ' ' + suffix_name if suffix_name else '')

    @property
    def get_position(self):
        personal_info = Personalinfo.objects.filter(user_id=self.id).first()
        if personal_info:
            employee_info = Empprofile.objects.filter(pi_id=personal_info.id).first()
            if employee_info:
                return employee_info.position.name
        return ""

    @property
    def get_division(self):
        personal_info = Personalinfo.objects.filter(user_id=self.id).first()
        if personal_info:
            employee_info = Empprofile.objects.filter(pi_id=personal_info.id).first()
            if employee_info and employee_info.section:
                return "{}".format(employee_info.section.div.div_acronym)
        return ""

    @property
    def get_section(self):
        personal_info = Personalinfo.objects.filter(user_id=self.id).first()
        if personal_info:
            employee_info = Empprofile.objects.filter(pi_id=personal_info.id).first()
            if employee_info and employee_info.section:
                return "{}".format(employee_info.section.sec_name)
        return ""

    def __str__(self):
        from frontend.models import Personalinfo
        data = Personalinfo.objects.filter(user_id=self.id).first()
        suffix_name = ""
        if data:
            suffix_name = data.ext.name if data.ext else ""

        return "{}{}{} {}{}".format('{}  '.format(self.title) if self.title else '',
                                    self.first_name.title(), " " + self.middle_name[:1] + "." if self.middle_name else '', self.last_name.title(), ' ' + suffix_name if suffix_name else '')

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'


class Fundsource(models.Model):
    name = models.CharField(max_length=164, unique=True)
    status = models.BooleanField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Fund Source"
        db_table = 'hrppms_fundsource'


class Aoa(models.Model):
    name = models.CharField(max_length=164, unique=True)
    status = models.BooleanField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Area of Assignment'
        db_table = 'hrppms_aoa'


class HrppmsModeaccession(models.Model):
    name = models.CharField(max_length=255, unique=True)
    status = models.BooleanField()
    uploadedby = models.ForeignKey(AuthUser, models.DO_NOTHING, verbose_name="Upload By")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Mode of Accession'
        db_table = 'hrppms_modeaccession'


class HrppmsModeseparation(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    status = models.BooleanField()
    uploadedby = models.ForeignKey(AuthUser, models.DO_NOTHING, verbose_name="Upload By")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Mode of Separation'
        db_table = 'hrppms_modeseparation'


class Project(models.Model):
    name = models.CharField(max_length=64, unique=True)
    status = models.BooleanField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Project/Program"
        verbose_name_plural = "Projects/Programs"
        db_table = 'hrppms_project'


class Empstatus(models.Model):
    name = models.CharField(max_length=64)
    acronym = models.CharField(max_length=36)
    status = models.BooleanField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Employment Status"
        verbose_name_plural = "Employment Status"
        db_table = 'hrppms_empstatus'


class Position(models.Model):
    name = models.CharField(max_length=128)
    acronym = models.CharField(max_length=64)
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    def __str__(self):
        return self.name

    @property
    def get_head_count(self):
        return Empprofile.objects.filter(position_id=self.id, pi__user__is_active=1).count()

    class Meta:
        verbose_name = "Position"
        db_table = 'hrppms_position'


class ExtensionName(models.Model):
    name = models.CharField(max_length=24)
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'extension_name'


class Indiginous(models.Model):
    name = models.CharField(max_length=128, unique=True)
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'pds_indiginous'


class Personalinfo(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    ext = models.ForeignKey(ExtensionName, models.DO_NOTHING, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    pob = models.CharField(max_length=128, blank=True, null=True)
    gender = models.IntegerField()
    cs_id = models.IntegerField(blank=True, null=True)
    height = models.CharField(max_length=15, blank=True, null=True)
    weight = models.CharField(max_length=15, blank=True, null=True)
    bt_id = models.IntegerField(blank=True, null=True)
    country_id = models.IntegerField(blank=True, null=True)
    isfilipino = models.IntegerField(blank=True, null=True)
    isdualcitizenship = models.IntegerField(blank=True, null=True)
    dc_bybirth = models.IntegerField(blank=True, null=True)
    dc_bynaturalization = models.IntegerField(blank=True, null=True)
    mobile_no = models.CharField(max_length=11, blank=True, null=True)
    telephone_no = models.CharField(max_length=10, blank=True, null=True)
    type_of_disability = models.CharField(max_length=30, blank=True, null=True)
    type_of_indi = models.ForeignKey(Indiginous, models.DO_NOTHING, blank=True, null=True)

    
    @property
    def get_gender(self):
        if self.gender == 1:
            return "Male"
        elif self.gender == 2:
            return "Female"
        else:
            return None

    def __str__(self):
        suffix_name = self.ext.name if self.ext else ""

        return "{}{} {}{}".format(
            self.user.first_name.title(),
            " " + self.user.middle_name[:1] + "." if self.user.middle_name else '',
            self.user.last_name.title(),
            ' ' + suffix_name if suffix_name else ''
        )

    class Meta:
        db_table = 'pds_personalinfo'


class Division(models.Model):
    div_name = models.CharField(max_length=150, unique=True, verbose_name="Division Name")
    div_acronym = models.CharField(max_length=100, unique=True, verbose_name="Acronym")
    div_chief_id = models.CharField(max_length=150, blank=True, null=True)
    designation = models.ForeignKey('Designation', models.DO_NOTHING, blank=True, null=True)

    @admin.display(description='Division Chief')
    def display_div_chief(self):
        return Empprofile.objects.filter(id=self.div_chief_id).first()

    def __str__(self):
        return self.div_name

    class Meta:
        verbose_name = 'Division'
        managed = False
        db_table = 'pas_division'


class Section(models.Model):
    sec_name = models.CharField(max_length=150, verbose_name="Section Name")
    sec_acronym = models.CharField(max_length=100, unique=True, verbose_name="Acronym")
    sec_head_id = models.CharField(max_length=150)
    div = models.ForeignKey(Division, models.DO_NOTHING, verbose_name="Division")
    is_negligible = models.BooleanField(default=False)
    is_alternate = models.BooleanField(default=False)

    @admin.display(description='Section Head')
    def display_sec_head(self):
        return Empprofile.objects.filter(id=self.sec_head_id).first()

    @admin.display(boolean=True, description='Is Alternate')
    def display_is_alternate(self):
        return True if self.is_alternate else False

    def __str__(self):
        return self.sec_name

    def get_head_count(self):
        return Empprofile.objects.filter(section_id=self.id, pi__user__is_active=1).count()

    class Meta:
        verbose_name = 'Section'
        managed = False
        db_table = 'pas_section'


class Empprofile(models.Model):
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)
    id_number = models.CharField(max_length=10, blank=True, null=True, unique=True)
    item_number = models.CharField(max_length=200, blank=True, null=True)
    account_number = models.CharField(max_length=24, blank=True, null=True)
    former_incumbent = models.CharField(max_length=100, blank=True, null=True)
    date_vacated = models.DateField(blank=True, null=True)
    aoa = models.ForeignKey(Aoa, models.DO_NOTHING, blank=True, null=True)
    fundsource = models.ForeignKey(Fundsource, models.DO_NOTHING, blank=True, null=True)
    project = models.ForeignKey(Project, models.DO_NOTHING, blank=True, null=True)
    empstatus = models.ForeignKey(Empstatus, models.DO_NOTHING)
    section = models.ForeignKey(Section, models.DO_NOTHING, blank=True, null=True)
    position = models.ForeignKey(Position, models.DO_NOTHING)
    dateofcreation_pos = models.DateField(blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    dateof_designation = models.DateField(blank=True, null=True)
    dateof_orig_appointment = models.DateField(blank=True, null=True)
    dateof_last_promotion = models.DateField(blank=True, null=True)
    salary_rate = models.DecimalField(max_digits=15, decimal_places=2)
    salary_grade = models.IntegerField()
    step_inc = models.IntegerField()
    mode_access = models.ForeignKey(HrppmsModeaccession, models.DO_NOTHING, blank=True, null=True)
    mode_sep = models.ForeignKey(HrppmsModeseparation, models.DO_NOTHING, blank=True, null=True)
    specialorder_no = models.CharField(max_length=100, blank=True, null=True)
    plantilla_psipop = models.CharField(max_length=100, blank=True, null=True)
    remarks_vacated = models.CharField(max_length=100, blank=True, null=True)
    picture = ResizedImageField(size=[250, 250], crop=['top', 'left'], upload_to='picture/',
                                default='picture/default.jpg')
    cover_photo = ResizedImageField(size=[700, 427], upload_to='cover_photo/', default='cover_photo/default.jpg')
    date_id_issuance = models.DateField(blank=True, null=True)
    place_id_issuance = models.CharField(max_length=1024, blank=True, null=True)

    def get_gender(self):
        if self.pi.gender == 1:
            return "Male"
        elif self.pi.gender == 2:
            return "Female"

    def get_status(self):
        if self.pi.user.is_active == 0:
            return "Inactive"
        elif self.pi.user.is_active == 1:
            return "Active"

    def get_address(self):
        from frontend.models import Address, Province, Brgy, City

        address = Address.objects.filter(pi_id=self.pi_id).first()
        barangay = Brgy.objects.filter(id=address.pa_brgy).first()
        city = City.objects.filter(code=address.pa_city).first()
        province = Province.objects.filter(id=address.pa_prov_code).first()
        return "{}{}, {}, {}".format("{} {}, {} ".format(address.pa_house_no if address.pa_house_no != "N/A" else '',
                                                          address.pa_village if address.pa_village != "N/A" else '',
                                                          address.pa_street if address.pa_street != "N/A" else '') if address.pa_village != "N/A" else "{} ".format(address.pa_street if address.pa_street != "N/A" else ''),
                                       barangay.name, city.name, province.name)

    @property
    def get_section_head(self):
        return Empprofile.objects.filter(id=self.section.sec_head_id).first()

    @property
    def get_division_chief(self):
        return Empprofile.objects.filter(id=self.section.div.div_chief_id).first()

    def __str__(self):
        data = self.pi
        suffix_name = ""
        if data:
            suffix_name = data.ext.name if data.ext else ""

        return "{}{} {}{}".format(
            data.user.first_name.title(),
            " " + data.user.middle_name[:1] + "." if data.user.middle_name else '',
            data.user.last_name.title(),
            ' ' + suffix_name if suffix_name else ''
        )

    class Meta:
        db_table = 'pas_empprofile'


class Designation(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Designation")
    emp_id = models.CharField(max_length=150, blank=True, null=True)

    @admin.display(description='Name')
    def display_emp(self):
        return Empprofile.objects.filter(id=self.emp_id).first()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Designation'
        db_table = 'pas_designation'


class Salarygrade(models.Model):
    name = models.IntegerField()
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pas_salarygrade'


class Stepinc(models.Model):
    name = models.IntegerField()
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pas_stepinc'


class PasTempseparation(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        db_table = 'pas_tempseparation'


class PasRfd(models.Model):
    user = models.ForeignKey(Empprofile, models.DO_NOTHING)
    status = models.IntegerField()
    date_requested = models.DateTimeField(default=timezone.now)
    date_approved = models.DateTimeField(blank=True, null=True)
    date_effectivity = models.DateTimeField(blank=True, null=True)
    tfs = models.ForeignKey(PasTempseparation, models.DO_NOTHING)
    remarks = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pas_rfd'


class InfimosCategory(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'infimos_category'


class InfimosPurpose(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    upload_by_id = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(InfimosCategory, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'infimos_purpose'


class PayrollIncharge(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    upload_by_id = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)

    class Meta:
        managed = False
        verbose_name = 'Payroll Incharge'
        db_table = 'payroll_incharge'

    def __str__(self):
        def __str__(self):
            if self.emp and self.emp.pi.first_name:
                return f"{self.emp.pi.first_name}'s Payroll Incharge"
        return 'Payroll Incharge'


class Rcompliance(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(blank=True, null=True)
    rreq_id = models.IntegerField(blank=True, null=True)
    datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'pas_rcompliance'


class Resignationreq(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    empstatus_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'pas_resignationreq'


class Outpass(models.Model):
    date = models.DateTimeField(default=timezone.now)
    status = models.IntegerField()
    in_behalf_of = models.ForeignKey('Empprofile', models.DO_NOTHING, related_name='in_behalf_of')
    emp = models.ForeignKey('Empprofile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pas_outpass'


# PIS
class PISPersonalInfo(models.Model):
    course_id = models.IntegerField(blank=True, null=True)
    photo = models.TextField(blank=True, null=True)
    avatar_base_url = models.TextField(blank=True, null=True)
    documents = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=40, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)
    place_birth = models.TextField(blank=True, null=True)
    sex = models.CharField(max_length=2, blank=True, null=True)
    citizenship = models.CharField(max_length=20, blank=True, null=True)
    height = models.CharField(max_length=5, blank=True, null=True)
    weight = models.CharField(max_length=5, blank=True, null=True)
    blood_type = models.CharField(max_length=3, blank=True, null=True)
    gsis_no = models.CharField(max_length=20, blank=True, null=True)
    pagibig_no = models.CharField(max_length=20, blank=True, null=True)
    pagibig_mp2_no = models.CharField(max_length=50, blank=True, null=True)
    philhealth_no = models.CharField(max_length=20, blank=True, null=True)
    sss_no = models.CharField(max_length=20, blank=True, null=True)
    tin_no = models.CharField(max_length=30, blank=True, null=True)
    residential_address = models.TextField(blank=True, null=True)
    residential_zipcode = models.CharField(max_length=10, blank=True, null=True)
    residential_telno = models.CharField(max_length=20, blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    permanent_zipcode = models.CharField(max_length=10, blank=True, null=True)
    permanent_telno = models.CharField(max_length=20, blank=True, null=True)
    email_address = models.CharField(max_length=60, blank=True, null=True)
    agency_employee = models.CharField(max_length=60, blank=True, null=True)
    date_update = models.DateField(blank=True, null=True)
    is_status = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    is_remarks = models.CharField(max_length=250, blank=True, null=True)
    cures_active = models.IntegerField(blank=True, null=True)
    sc = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'personal_info'


class PISEmployeeInfo(models.Model):
    personal = models.ForeignKey(PISPersonalInfo, models.DO_NOTHING)
    position_id = models.IntegerField(blank=True, null=True)
    project_id = models.IntegerField(blank=True, null=True)
    id_number = models.CharField(max_length=8, blank=True, null=True)
    item_number = models.CharField(max_length=150, blank=True, null=True)
    account_number = models.CharField(max_length=11, blank=True, null=True)
    lastname = models.CharField(max_length=60, blank=True, null=True)
    firstname = models.CharField(max_length=60, blank=True, null=True)
    middlename = models.CharField(max_length=60, blank=True, null=True)
    extention = models.CharField(max_length=3, blank=True, null=True)
    civil_status = models.CharField(max_length=10, blank=True, null=True)
    contact_no = models.CharField(max_length=20, blank=True, null=True)
    step_increment = models.CharField(max_length=10, blank=True, null=True)
    salary_grade = models.CharField(max_length=10, blank=True, null=True)
    salary_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fund_charge = models.CharField(max_length=100, blank=True, null=True)
    date_registered = models.DateField(blank=True, null=True)
    date_appointed = models.DateField(blank=True, null=True)
    date_effectivity = models.DateField(blank=True, null=True)
    employ_status = models.IntegerField(blank=True, null=True)
    is_remarks = models.CharField(max_length=50, blank=True, null=True)
    is_status = models.CharField(max_length=50, blank=True, null=True)
    is_note = models.TextField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    is_primary = models.IntegerField(blank=True, null=True)
    division = models.CharField(max_length=100, blank=True, null=True)
    area_level = models.CharField(max_length=100, blank=True, null=True)
    payroll_incharge_id = models.CharField(max_length=50, blank=True, null=True)
    is_dempcc = models.IntegerField(blank=True, null=True)
    uid = models.CharField(max_length=255, blank=True, null=True)
    date_entry = models.DateField(blank=True, null=True)
    projectid_cures = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'employee_info'


class WfhTime(models.Model):
    datetime = models.DateTimeField(blank=True, null=True)
    type = models.ForeignKey('WfhType', models.DO_NOTHING)
    emp = models.ForeignKey('Empprofile', models.DO_NOTHING)
    ip_address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wfh_time'


class WfhType(models.Model):
    type_desc = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wfh_type'


class PayeeGroup(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    emp = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payroll_payeegroup'


class PayrollColumn(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    operation = models.BooleanField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True, unique=True)
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    operation2 = models.BooleanField(blank=True, null=True)
    fetch_from_db = models.BooleanField(blank=True, null=True)
    db_element = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payroll_column'


class PayrollColumnvalue(models.Model):
    column = models.ForeignKey('PayrollColumn', models.DO_NOTHING)
    pemp = models.ForeignKey('PayrollPayeeGroupEmployee', models.DO_NOTHING)
    value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    payroll = models.ForeignKey('PayrollMain', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payroll_columnvalue'


class PayrollPayeeGroupEmployee(models.Model):
    payeegroup = models.ForeignKey('PayeeGroup', models.DO_NOTHING)
    emp = models.ForeignKey('Empprofile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payroll_payeegroupemployee'


class PayrollEmployee(models.Model):
    payroll = models.ForeignKey('PayrollMain', models.DO_NOTHING)
    emp = models.ForeignKey('Empprofile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payroll_employee'


class PayrollMain(models.Model):
    payroll_title = models.CharField(max_length=255, blank=True, null=True)
    purpose = models.CharField(max_length=255, blank=True, null=True)
    tracking_no = models.CharField(max_length=15, blank=True, null=True, unique=True)
    dv_no = models.CharField(max_length=10, blank=True, null=True, unique=True)
    period_from = models.DateField(blank=True, null=True)
    period_to = models.DateField(blank=True, null=True)
    emp = models.ForeignKey('Empprofile', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payroll_main'


class PayrollMainColumns(models.Model):
    payroll = models.ForeignKey('PayrollMain', models.DO_NOTHING)
    column = models.ForeignKey('PayrollColumn', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payroll_maincolumns'


class ColumnGroup(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    emp = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payroll_columngroup'


class PayrollColumnGroupColumns(models.Model):
    columngroup = models.ForeignKey('ColumnGroup', models.DO_NOTHING)
    column = models.ForeignKey('PayrollColumn', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payroll_columngroupcolumns'


class HrwsHealthchecklist(models.Model):
    temperature = models.CharField(max_length=255)
    q1 = models.CharField(max_length=255)
    q2 = models.CharField(max_length=255)
    q3 = models.CharField(max_length=255)
    q4 = models.CharField(max_length=255)
    q5 = models.CharField(max_length=255)
    q6 = models.CharField(max_length=255)
    q7 = models.CharField(max_length=255)
    q8 = models.CharField(max_length=255)
    q9 = models.CharField(max_length=255)
    q10 = models.CharField(max_length=255)
    q11 = models.CharField(max_length=255)
    q12 = models.CharField(max_length=255)
    q13 = models.CharField(max_length=255)
    q14 = models.CharField(max_length=255)
    choose = models.IntegerField()
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    datetime_added = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'hrws_healthchecklist'


class DirectoryDetailType(models.Model):
    type = models.CharField(max_length=255, unique=True)
    status = models.BooleanField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        verbose_name = "Detail Type"
        db_table = 'directory_detail_type'


class DirectoryDetails(models.Model):
    dcontact = models.ForeignKey('DirectoryContact', models.DO_NOTHING)
    description = models.TextField(blank=True, null=True)
    dtype = models.ForeignKey('DirectoryDetailType', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'directory_details'


class DirectoryContact(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    ext = models.ForeignKey(ExtensionName, models.DO_NOTHING, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.BooleanField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='uploaded_by')
    last_updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='last_updated_by')
    last_updated_on = models.DateTimeField(default=timezone.now)
    orgtype = models.ForeignKey('DirectoryOrgtype', models.DO_NOTHING, blank=True, null=True)

    @property
    def get_contact_name(self):
        return "{}, {} {}.".format(self.last_name.title(), self.first_name.title(),
                                   self.middle_name[:1]) if self.middle_name else "{}, {}".format(
            self.last_name.title(), self.first_name.title())

    @property
    def get_email(self):
        email = []
        email_data = DirectoryDetails.objects.filter(dtype_id=1, dcontact_id=self.id)
        if email_data:
            for row in email_data:
                email.append(row.description)

            return "{} and {}".format(", ".join(str(row) for row in email[:-1]), email[-1]) if len(email) > 1 else "{}".format(email[0])

    @property
    def get_contact(self):
        contact = []
        contact_data = DirectoryDetails.objects.filter(dtype_id=2, dcontact_id=self.id)
        if contact_data:
            for row in contact_data:
                contact.append(row.description)

            return "{} and {}".format(",".join(str(row) for row in contact[:-1]), contact[-1]) if len(
                contact) > 1 else "{}".format(contact[0])

    @property
    def get_address(self):
        address = []
        address_data = DirectoryDetails.objects.filter(dtype_id=3, dcontact_id=self.id)
        if address_data:
            for row in address_data:
                address.append(row.description)

            return "{} and {}".format(",".join(str(row) for row in address[:-1]), address[-1]) if len(
                address) > 1 else "{}".format(address[0])

    class Meta:
        managed = False
        db_table = 'directory_contact'


class DirectoryOrgtype(models.Model):
    name = models.CharField(max_length=255, unique=True)
    acronym = models.CharField(max_length=255, unique=True)
    status = models.BooleanField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        verbose_name = "Organization Type"
        db_table = 'directory_orgtype'


class DtrPin(models.Model):
    pin_id = models.IntegerField(blank=True, null=True)
    emp_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'tbl_dtr_pin'


class ForgotPasswordCode(models.Model):
    code = models.CharField(max_length=255, unique=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'forgot_password_code'


class Patches(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'portal_patch'


class DRNTracker(models.Model):
    drn = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=150, blank=True, null=True)
    emp_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'drn_tracker'


class Logs(models.Model):
    logs = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tbl_logs'


class PortalSuccessLogs(models.Model):
    logs = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'portal_success_logs'


class PortalErrorLogs(models.Model):
    logs = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'portal_error_logs'


class PositionVacancy(models.Model):
    number = models.CharField(max_length=255, blank=True, null=True)
    item_number = models.CharField(max_length=500, blank=True, null=True)
    position = models.ForeignKey(Position, models.DO_NOTHING)
    empstatus = models.ForeignKey(Empstatus, models.DO_NOTHING)
    aoa = models.ForeignKey(Aoa, models.DO_NOTHING, verbose_name="Area of Assignment")
    quantity = models.IntegerField(blank=True, null=True)
    salary_rate = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    salary_grade = models.ForeignKey(Salarygrade, models.DO_NOTHING)
    job_description = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='vacancy/attachment/', blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    status = models.IntegerField(blank=True, default=0)
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @property
    def get_position_with_status(self):
        return f"{self.position.name} - {self.empstatus.name}"

    @property
    def get_total_app(self):
        from landing.models import JobApplication
        return JobApplication.objects.filter(vacancy_id=self.id).count()

    @property
    def get_total_hired(self):
        from landing.models import JobApplication
        return JobApplication.objects.filter(vacancy_id=self.id, app_status_id=9).count()

    @property
    def get_hired_employees(self):
        from landing.models import JobApplication
        job_app = JobApplication.objects.filter(vacancy_id=self.id, app_status_id=9)

        hired_employees = ""
        for row in job_app:
            hired_employees += row.get_fullname + ", "

        return hired_employees[:-2]

    @property
    def is_past_deadline(self):
        if self.deadline:
            current_date = datetime.date.today()
            return current_date > self.deadline
        else:
            return False

    def __str__(self):
        return f"{self.position} {self.number}"

    class Meta:
        managed = False
        db_table = 'position_vacancies'



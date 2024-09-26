import hashlib
import os
from django.db.models import Q, Count, IntegerField, Case, When
from django.dispatch import receiver
from django.utils import timezone
from django.contrib import admin
from datetime import timedelta

from django.db import models

from backend.models import AuthUser, Personalinfo, Position, Empprofile, Outpass, ExtensionName, Aoa, Project, \
    Fundsource, Empstatus, Section, HrppmsModeaccession, HrppmsModeseparation, Division


class Province(models.Model):
    name = models.CharField(max_length=64, unique=True)
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Province'
        db_table = 'pds_province'


class City(models.Model):
    name = models.CharField(max_length=64, unique=True)
    code = models.CharField(max_length=24, unique=True)
    prov_code = models.ForeignKey(Province, models.DO_NOTHING, verbose_name="Province")
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        db_table = 'pds_city'


class Brgy(models.Model):
    name = models.CharField(max_length=128)
    city_code = models.ForeignKey(City, models.DO_NOTHING, to_field='code', verbose_name="City")
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    class Meta:
        verbose_name = 'Barangay'
        db_table = 'pds_barangay'


class Civilstatus(models.Model):
    name = models.CharField(unique=True, max_length=128)
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    class Meta:
        verbose_name = 'Civil Status'
        verbose_name_plural = "Civil Status"
        db_table = 'pds_civilstatus'


class Countries(models.Model):
    name = models.CharField(max_length=64, unique=True)
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        db_table = 'pds_countries'


class Bloodtype(models.Model):
    name = models.CharField(unique=True, max_length=24)
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    class Meta:
        verbose_name = 'Blood Type'
        verbose_name_plural = "Blood Type"
        db_table = 'pds_bloodtype'


class Address(models.Model):
    ra_house_no = models.CharField(max_length=24, blank=True, null=True)
    ra_street = models.CharField(max_length=64, blank=True, null=True)
    ra_village = models.CharField(max_length=24, blank=True, null=True)
    ra_prov_code = models.IntegerField(blank=True, null=True)
    ra_city = models.IntegerField(blank=True, null=True)
    ra_brgy = models.IntegerField(blank=True, null=True)
    ra_zipcode = models.CharField(max_length=5, blank=True, null=True)
    pa_house_no = models.CharField(max_length=24, blank=True, null=True)
    pa_street = models.CharField(max_length=24, blank=True, null=True)
    pa_village = models.CharField(max_length=24, blank=True, null=True)
    pa_prov_code = models.IntegerField(blank=True, null=True)
    pa_city = models.IntegerField(blank=True, null=True)
    pa_brgy = models.IntegerField(blank=True, null=True)
    pa_zipcode = models.CharField(max_length=5, blank=True, null=True)
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        db_table = 'pds_address'


class Deductionnumbers(models.Model):
    gsis_no = models.CharField(max_length=24)
    pagibig_no = models.CharField(max_length=24)
    philhealth_no = models.CharField(max_length=24)
    sss_no = models.CharField(max_length=24)
    tin_no = models.CharField(max_length=24)
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pds_deductionnumbers'


class Familybackground(models.Model):
    sp_surname = models.CharField(max_length=24)
    sp_fname = models.CharField(max_length=24)
    sp_mname = models.CharField(max_length=24)
    sp_ext = models.ForeignKey(ExtensionName, models.DO_NOTHING, related_name='extension_sp_ext', blank=True, null=True)
    sp_occupation = models.CharField(max_length=128)
    sp_employer = models.CharField(max_length=64)
    sp_business = models.CharField(max_length=128)
    sp_telephone = models.CharField(max_length=11)
    f_surname = models.CharField(max_length=24)
    f_fname = models.CharField(max_length=24)
    f_mname = models.CharField(max_length=24)
    f_ext = models.ForeignKey(ExtensionName, models.DO_NOTHING, related_name='extension_f_ext', blank=True, null=True)
    m_maiden = models.CharField(max_length=24, blank=True, null=True)
    m_surname = models.CharField(max_length=24)
    m_fname = models.CharField(max_length=24)
    m_mname = models.CharField(max_length=24)
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        db_table = 'pds_familybackground'


class Children(models.Model):
    child_fullname = models.CharField(max_length=128)
    child_dob = models.DateField()
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pds_children'


class Degree(models.Model):
    degree_name = models.CharField(max_length=128)
    degree_acronym = models.CharField(max_length=24)
    deg_status = models.IntegerField()
    pi = models.ForeignKey(AuthUser, models.DO_NOTHING, verbose_name="Upload By")

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.deg_status == 1

    class Meta:
        verbose_name = 'Degree'
        db_table = 'pds_degree'


class Honors(models.Model):
    hon_name = models.CharField(max_length=24)
    hon_status = models.IntegerField()
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING, verbose_name="Upload By")

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.hon_status == 1

    class Meta:
        verbose_name = 'Honor'
        db_table = 'pds_honors'


class Educationlevel(models.Model):
    lev_name = models.CharField(max_length=24, unique=True)
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    class Meta:
        verbose_name = 'Education Level'
        db_table = 'pds_educationlevel'


class School(models.Model):
    school_name = models.CharField(max_length=128, verbose_name="Name")
    school_acronym = models.CharField(max_length=24, verbose_name="Acronym")
    school_status = models.IntegerField()
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING, verbose_name="Upload By")

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.school_status == 1

    class Meta:
        managed = False
        db_table = 'pds_school'


class Educationbackground(models.Model):
    level = models.ForeignKey(Educationlevel, models.DO_NOTHING)
    school = models.ForeignKey(School, models.DO_NOTHING)
    degree = models.ForeignKey(Degree, models.DO_NOTHING)
    period_from = models.CharField(max_length=12, blank=False, null=False, default='N/A')
    period_to = models.CharField(max_length=12, blank=False, null=False, default='N/A')
    units_earned = models.CharField(max_length=12, blank=False, null=False, default='N/A')
    year_graduated = models.CharField(max_length=12, blank=False, null=False, default='N/A')
    hon = models.ForeignKey(Honors, models.DO_NOTHING)
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pds_educationbackground'


class Eligibility(models.Model):
    el_name = models.CharField(max_length=255, verbose_name="Name")
    el_level = models.IntegerField()
    el_status = models.IntegerField()
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING, verbose_name="Upload By")

    @admin.display(description='Level')
    def display_level(self):
        if self.el_level:
            if 11 <= (self.el_level % 100) <= 13:
                suffix = 'th'
            else:
                suffix = ['th', 'st', 'nd', 'rd', 'th'][min(self.el_level % 10, 4)]
            return str(self.el_level) + suffix
        else:
            return ''

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.el_status == 1

    class Meta:
        verbose_name = 'Eligibility'
        verbose_name_plural = 'Eligibilities'
        db_table = 'pds_eligibility'


class Course(models.Model):
    name = models.CharField(max_length=1024)
    status = models.BooleanField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        db_table = 'pds_course'


class Civilservice(models.Model):
    el = models.ForeignKey(Eligibility, models.DO_NOTHING)
    cs_rating = models.CharField(max_length=24)
    cs_dateexam = models.CharField(max_length=24, blank=True, null=True)
    cs_place = models.CharField(max_length=128)
    cs_number = models.CharField(max_length=24, blank=True, null=True)
    cs_date_val = models.CharField(max_length=24, blank=True, null=True)
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)
    course = models.ForeignKey(Course, models.DO_NOTHING)

    class Meta:
        db_table = 'pds_civilservice'


class Workexperience(models.Model):
    we_from = models.DateField()
    we_to = models.DateField()
    position = models.ForeignKey(Position, models.DO_NOTHING)
    position_name = models.CharField(max_length=128)
    company = models.CharField(max_length=128)
    salary_rate = models.CharField(max_length=15)
    sg_step = models.CharField(max_length=5)
    empstatus = models.ForeignKey(Empstatus, models.DO_NOTHING)
    govt_service = models.IntegerField()
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    @property
    def we_inclusive(self):
        from frontend.templatetags.tags import transform_to_duration_date
        return transform_to_duration_date(self.we_from, self.we_to, "false", "false", True)

    class Meta:
        managed = False
        db_table = 'pds_workexperience'


class Workhistory(models.Model):
    item_number = models.CharField(max_length=50, blank=True, null=True)
    former_incumbent = models.CharField(max_length=255, blank=True, null=True)
    date_vacated = models.DateField(blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING, blank=True, null=True)
    aoa = models.ForeignKey(Aoa, models.DO_NOTHING, blank=True, null=True)
    fundsource = models.ForeignKey(Fundsource, models.DO_NOTHING, blank=True, null=True)
    project = models.ForeignKey(Project, models.DO_NOTHING, blank=True, null=True)
    section = models.ForeignKey(Section, models.DO_NOTHING, blank=True, null=True)
    we = models.ForeignKey('Workexperience', on_delete=models.CASCADE, blank=True, null=True)
    datecreation_pos = models.DateField(blank=True, null=True)
    dateof_orig_appointment = models.DateField(blank=True, null=True)
    dateof_last_promotion = models.DateField(blank=True, null=True)
    mode_access = models.ForeignKey(HrppmsModeaccession, models.DO_NOTHING, blank=True, null=True)
    mode_sep = models.ForeignKey(HrppmsModeseparation, models.DO_NOTHING, blank=True, null=True)
    specialorder_no = models.CharField(max_length=100, blank=True, null=True)
    plantilla_psipop = models.CharField(max_length=100, blank=True, null=True)
    remarks_vacated = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    dateof_designation = models.DateField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'pas_workhistory'


class Organization(models.Model):
    org_name = models.CharField(max_length=128, verbose_name="Name")
    org_status = models.IntegerField(verbose_name="Status")
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING, verbose_name="Upload By")

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.org_status == 1

    class Meta:
        verbose_name = 'Organization'
        managed = False
        db_table = 'pds_organization'


class Voluntary(models.Model):
    org = models.ForeignKey(Organization, models.DO_NOTHING)
    organization = models.CharField(max_length=255, null=True, blank=True)
    vol_from = models.DateField()
    vol_to = models.DateField()
    vol_hours = models.DecimalField(max_digits=15, decimal_places=2)
    now = models.CharField(max_length=128)
    pi_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pds_voluntary'


class Trainingtitle(models.Model):
    tt_name = models.TextField(verbose_name="Name")
    tt_status = models.IntegerField()
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING, verbose_name="Upload By")

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.tt_status == 1

    class Meta:
        verbose_name = "Training Title"
        db_table = 'pds_trainingtitle'


class Trainingtype(models.Model):
    type_name = models.CharField(max_length=64, unique=True, verbose_name="Name")
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    class Meta:
        verbose_name = "Training Type"
        db_table = 'pds_trainingtype'


class Training(models.Model):
    tt = models.ForeignKey(Trainingtitle, models.DO_NOTHING)
    training = models.CharField(max_length=1024, null=True, blank=True)
    tr_from = models.DateField()
    tr_to = models.DateField()
    tr_hours = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.ForeignKey(Trainingtype, models.DO_NOTHING)
    training_type = models.CharField(max_length=1024, null=True, blank=True)
    conducted = models.CharField(max_length=128)
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pds_training'


class Hobbies(models.Model):
    hob_name = models.CharField(max_length=24, verbose_name="Name")
    hob_status = models.IntegerField(verbose_name="Status")
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING, verbose_name="Upload By")

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.hob_status == 1

    class Meta:
        verbose_name = 'Hobby'
        verbose_name_plural = "Hobbies"
        managed = False
        db_table = 'pds_hobbies'


class Skills(models.Model):
    hob = models.ForeignKey(Hobbies, models.DO_NOTHING)
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pds_skills'


class Nonacad(models.Model):
    na_name = models.CharField(max_length=128, verbose_name="Name")
    na_status = models.IntegerField(verbose_name="Status")
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING, verbose_name="Upload By")

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.na_status == 1

    class Meta:
        verbose_name = 'Non-Academic Recognition'
        db_table = 'pds_nonacad'


class Recognition(models.Model):
    na = models.ForeignKey(Nonacad, models.DO_NOTHING)
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        db_table = 'pds_recognition'


class Membership(models.Model):
    org = models.ForeignKey(Organization, models.DO_NOTHING)
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pds_membership'


class Additional(models.Model):
    question = models.IntegerField()
    answers = models.TextField(blank=True, null=True)
    ad_status = models.IntegerField()
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pds_additional'


class Reference(models.Model):
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=128)
    tel_no = models.CharField(max_length=11)
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pds_reference'


def get_all_passengers_others(self, others):
    return ', '.join(others)


def check_confirmation(rito):
    count = rito.ritodetails_set.aggregate(
        total=Count(
            Case(
                When(inclusive_from__lt=rito.date.date(), then=1),
                output_field=IntegerField(),
            )
        )
    )['total']

    return count


def check_justification(rito):
    filing_date_plus_3_days = (rito.date + timedelta(days=3)).date()
    count = rito.ritodetails_set.aggregate(
        total=Count(
            Case(
                When(Q(inclusive_from__lt=filing_date_plus_3_days) & Q(inclusive_from__gte=rito.date.date()), then=1),
                output_field=IntegerField(),
            )
        )
    )['total']

    return count


class Rito(models.Model):
    tracking_no = models.CharField(max_length=64, blank=True, null=True)
    tracking_merge = models.CharField(max_length=64)
    date = models.DateTimeField(blank=True, null=True)
    approved_date = models.DateField(blank=True, null=True)
    status = models.IntegerField()
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    remarks = models.TextField(blank=True, null=True)
    date_received = models.DateTimeField(blank=True, null=True)
    date_administered = models.DateTimeField(blank=True, null=True)
    date_forwarded = models.DateTimeField(blank=True, null=True)
    date_returned = models.DateTimeField(blank=True, null=True)

    def get_rito_approver(self):
        from approve_rito.models import ApprovedRito
        check = ApprovedRito.objects.filter(rito_id=self.id, status=1)

        if check:
            return check.first().supervisor.pi.user.get_fullname
        else:
            return ''

    @property
    def get_hash(self):
        return hashlib.sha1(str(self.id).encode('utf-8')).hexdigest()

    @property
    def count_confirmation_travel(self):
        count = check_confirmation(self)

        return '<span class="badge badge-warning">For Confirmation</span>' if count > 0 else ''

    @property
    def count_justification_travel(self):
        count = check_justification(self)

        return '<span class="badge badge-warning">For Justification</span>' if count > 0 else ''

    @property
    def get_total_confirmation_of_travel(self):
        detail = Ritodetails.objects.filter(rito_id=self.id)
        count = 0
        for row in detail:
            if self.date.date() > row.inclusive_from:
                count = count + 1

        return count

    @property
    def get_all_passengers(self):
        people = Ritopeople.objects.filter(detail__rito_id=self.id) \
            .select_related('name__pi__user').order_by('name__pi__user__last_name')

        full_names = []
        for person in people:
            name = person.name.pi.user.get_fullname
            if name not in full_names:
                full_names.append(name)

        total_people = len(full_names)

        if total_people > 5:
            displayed_people = ', '.join(full_names[:5])
            others_count = total_people - 5
            others_names = ', '.join(full_names[5:])
            return f'{displayed_people}, and <span data-toggle="tooltip" data-html="true" data-placement="top" title="{others_names}">{others_count}</span> others..'

        else:
            if total_people == 0:
                return "No employee found"
            if total_people == 1:
                return f"{full_names[0]}"
            else:
                listed_people = ', '.join(full_names[:-1])
                return f"{listed_people}, and {full_names[-1]}"

    @property
    def get_travel_status(self):
        status = ""
        if self.status == 2:
            if self.remarks:
                status += '<span class="badge badge-primary" data-toggle="tooltip" data-placement="top" title="Remarks: {}">Pending</span>'.format(self.remarks)
            else:
                status += '<span class="badge badge-primary">Pending</span>'
        elif self.status == 5:
            status += '<span class="badge badge-warning">Canceled</span>'
        else:
            if self.approved_date:
                status += '<span class="badge badge-success" data-toggle="tooltip" data-placement="top" title="Approved Date for Travel Request {}">Approved</span>'.format(self.approved_date)
            else:
                status += '<span class="badge badge-success">Approved</span>'

        checked = TravelOrder.objects.values('status', 'date', 'attachment').filter(Q(rito_id=self.id)).first()
        if checked:
            if self.date_administered:
                status += ' | <span class="badge badge-success">Administered</span>'
            elif checked['status'] == 2:
                if checked['date']:
                    status += ' | <span class="badge badge-success" data-toggle="tooltip" data-placement="top" title="Approved Date for Travel Order {}">Approved</span>'.format(
                        checked['date'])
                else:
                    status += ' | <span class="badge badge-success">Approved</span>'
            elif checked['status'] == 3:
                status += ' | <span class="badge badge-warning">Canceled</span>'
            elif checked['status'] == 1:
                status += ' | <span class="badge badge-info">Ongoing</span>'
        else:
            if self.status == 5:
                status += ' | <span class="badge badge-warning">Canceled</span>'
            else:
                status += ' | <span class="badge badge-primary">Pending</span>'

        if checked:
            if checked['attachment']:
                status += ' | <span class="badge badge-success">File</span>'
            else:
                status += ' | <span class="badge badge-default">File</span>'
        else:
            status += ' | <span class="badge badge-default">File</span>'

        return status

    @property
    def get_travel_status_for_supervisor(self):
        status = ""
        if self.status == 2:
            if self.remarks:
                status += '<span class="badge bg-secondary" data-toggle="tooltip" data-placement="top" title="Remarks: {}">Pending</span>'.format(
                    self.remarks)
            else:
                status += '<span class="badge bg-secondary">Pending</span>'
        elif self.status == 5:
            status += '<span class="badge bg-warning">Canceled</span>'
        else:
            if self.approved_date:
                status += '<span class="badge bg-success" data-toggle="tooltip" data-placement="top" title="Approved Date for Travel Request {}">Approved</span>'.format(
                    self.approved_date)
            else:
                status += '<span class="badge bg-success">Approved</span>'

        return status

    @property
    def get_action(self):
        action = ""
        action += '<a target="_blank" href="/travel/requests/print/{}">Details</a>'.format(self.id)
        if self.status != 5:
            if self.status != 3:
                action += ' | <a href="javascript:;" data-role="cancel" data-id="{}">Cancel</a>'.format(self.id)

        if check_confirmation(self) > 0 or check_justification(self) > 0:
            if self.tracking_merge:
                action += ' | <a href="javascript:;" data-role="to_attachment" data-filter="{}">Attachment</a>'\
                    .format(self.tracking_merge)
            else:
                action += ' | <a href="javascript:;" data-role="to_attachment" data-filter="{}">Attachment</a>'\
                    .format(self.tracking_no)

        checked = TravelOrder.objects.filter(Q(rito_id=self.id)).first()
        if checked:
            if self.status != 5 and checked.status != 3 and checked.attachment:
                action += ' | <a target="_blank" href="{}">Download</a>'.format(checked.attachment.url)

        return action

    @property
    def get_admin_action(self):
        action = ""
        if self.status == 3:
            if self.tracking_merge:
                action += '<a target="_blank" href="/backend/generate-to/{}">Details</a>'.format(self.tracking_merge)
            else:
                action += '<a target="_blank" href="/backend/generate-to/{}">Details</a>'.format(self.tracking_no)
        else:
            action += '<a target="_blank" href="/backend/view-travel/{}">Details</a>'.format(self.tracking_no)

        if self.status == 5:
            action += ' | <a href="javascript:;" data-role="uncancel" data-filter="{}">Uncancel</a>'.format(self.tracking_no)

        if check_confirmation(self) > 0 or check_justification(self) > 0:
            if self.tracking_merge:
                action += ' | <a href="javascript:void(0);" data-role="to_requirements" data-filter="{}">Requirements</a>'\
                    .format(self.tracking_merge)
            else:
                action += ' | <a href="javascript:void(0);" data-role="to_requirements" data-filter="{}">Requirements</a>'\
                    .format(self.tracking_no)

        checked = TravelOrder.objects.filter(Q(rito_id=self.id)).first()
        if checked:
            if checked.status != 3 and checked.status != 2:
                if self.tracking_merge:
                    action += ' | <a href="javascript:;" data-role="cancel" data-filter="{}">Cancel</a>'.format(self.tracking_merge)
                else:
                    action += ' | <a href="javascript:;" data-role="cancel" data-filter="{}">Cancel</a>'.format(self.tracking_no)

            if checked.status == 2:
                if self.tracking_merge:
                    action += ' | <a href="javascript:;" data-role="to_attachment" data-filter="{}">Attachment</a>'.format(self.tracking_merge)
                else:
                    action += ' | <a href="javascript:;" data-role="to_attachment" data-filter="{}">Attachment</a>'.format(self.tracking_no)

            if self.status != 5 and checked.status != 3 and checked.attachment:
                action += ' | <a target="_blank" href="{}">Download</a>'.format(checked.attachment.url)
        else:
            if self.status != 5:
                if self.status != 3:
                    action += ' | <a href="javascript:;" data-role="cancel" data-filter="{}">Cancel</a>'.format(self.tracking_no)

        return action

    @property
    def get_supervisor_action(self):
        action = '<a target="_blank" href="/backend/view-travel/{}">Details</a>'.format(self.tracking_no)
        return action

    @property
    def get_attachment(self):
        rito = TravelOrder.objects.filter(Q(rito_id=self.id) & ~Q(attachment='')).first()
        return rito.attachment

    class Meta:
        db_table = 'pas_rito'


class Mot(models.Model):
    name = models.CharField(max_length=64)
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    class Meta:
        verbose_name = 'Means of Transportation'
        managed = False
        db_table = 'pas_mot'


class Claims(models.Model):
    name = models.CharField(max_length=64)
    status = models.IntegerField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    class Meta:
        verbose_name = 'Travel Claims'
        verbose_name_plural = 'Travel Claims'
        managed = False
        db_table = 'pas_claims'


class Ritodetails(models.Model):
    rito = models.ForeignKey(Rito, models.DO_NOTHING)
    place = models.CharField(max_length=164)
    inclusive_from = models.DateField()
    inclusive_to = models.DateField()
    purpose = models.CharField(max_length=164)
    expected_output = models.CharField(max_length=164)
    claims = models.ForeignKey(Claims, models.DO_NOTHING)
    mot = models.ForeignKey(Mot, models.DO_NOTHING)

    @property
    def get_inclusive(self):
        if self.inclusive_from == self.inclusive_to:
            return self.inclusive_from.strftime("%B %d, %Y")
        else:
            if not self.inclusive_to:
                return "{}".format(self.inclusive_from.strftime("%B %d, %Y"))
            else:
                return "{} - {}".format(self.inclusive_from.strftime("%B %d, %Y"), self.inclusive_to.strftime("%B %d, %Y"))

    @property
    def get_tr_passengers(self):
        people = Ritopeople.objects.filter(detail_id=self.id) \
            .select_related('name__pi__user').order_by('name__pi__user__last_name')

        full_names = []
        for person in people:
            name = person.name.pi.user.get_fullname
            if name not in full_names:
                full_names.append(name)

        total_people = len(full_names)

        if total_people > 5:
            displayed_people = ', '.join(full_names[:5])
            others_count = total_people - 5
            others_names = ', '.join(full_names[5:])
            return f'{displayed_people}, and <span data-toggle="tooltip" data-html="true" data-placement="top" title="{others_names}">{others_count}</span> others..'
        else:
            if total_people == 1:
                return f"{full_names[0]}"
            else:
                listed_people = ', '.join(full_names[:-1])
                return f"{listed_people}, and {full_names[-1]}"

    def get_requested_by_full_name(self):
        if self.rito.emp.pi.user.middle_name:
            return "{} {}. {}".format(self.rito.emp.pi.user.first_name, self.rito.emp.pi.user.middle_name[0], self.rito.emp.pi.user.last_name).title()
        else:
            return "{} {}".format(self.rito.emp.pi.user.first_name, self.rito.emp.pi.user.last_name).title()

    def get_travel_request_status(self):
        if self.rito.status == 2:
            return "Pending"
        elif self.rito.status == 3:
            return "Approved"

    def get_count_passenger(self):
        return Ritopeople.objects.filter(detail_id=self.id).count()

    class Meta:
        db_table = 'pas_ritodetails'


class Ritopeople(models.Model):
    detail = models.ForeignKey(Ritodetails, models.DO_NOTHING)
    name = models.ForeignKey(Empprofile, models.DO_NOTHING)

    def get_requested_gender(self):
        return "Male" if self.name.pi.gender == 1 else "Female"

    class Meta:
        db_table = 'pas_ritopeople'


class TravelOrder(models.Model):
    rito = models.ForeignKey(Rito, models.DO_NOTHING)
    date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()
    attachment = models.FileField(upload_to='attachment/', null=True, blank=True)
    approved_by = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date_uploaded = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pas_to'


class ToCounter(models.Model):
    to_counter = models.IntegerField()
    year = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'to_counter'


class Downloadableforms(models.Model):
    title = models.CharField(max_length=128, unique=True)
    filename = models.FileField(upload_to='downloadable_forms/', null=True, blank=True)
    status = models.BooleanField()
    date = models.DateTimeField(default=timezone.now)
    classes = models.ForeignKey('DownloadableformsClass', models.DO_NOTHING)

    class Meta:
        verbose_name = 'Downloadable Forms'
        db_table = 'pas_downloadableforms'


class DownloadableformsClass(models.Model):
    name = models.CharField(max_length=255, unique=True)
    acronym = models.CharField(max_length=255, unique=True)
    status = models.BooleanField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    is_sop = models.BooleanField(default=False, verbose_name="Is SOP?")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Downloadables Class'
        verbose_name_plural = 'Downloadables Classes'
        db_table = 'pas_downloadableforms_class'


class DownloadableformsSopClass(models.Model):
    name = models.CharField(max_length=255, unique=True)
    acronym = models.CharField(max_length=255, unique=True)
    status = models.BooleanField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'SOP Classification'
        db_table = 'pas_downloadableforms_sop_class'


class DownloadableformsSopFileClass(models.Model):
    sop_class = models.ForeignKey(DownloadableformsSopClass, models.DO_NOTHING)
    downloadable_form = models.ForeignKey(Downloadableforms, models.DO_NOTHING)

    class Meta:
        db_table = 'pas_downloadableforms_sop_fileclass'


class PisConfig(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    backend_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pis_config'


class PdsUpdateTracking(models.Model):
    pis_config = models.ForeignKey(PisConfig, models.DO_NOTHING, null=True, blank=True)
    date = models.DateTimeField(blank=True, null=True)
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pds_update_tracking'


class Locatorslip(models.Model):
    outpass = models.ForeignKey(Outpass, models.DO_NOTHING)
    date = models.DateField()
    status = models.IntegerField()
    attachment = models.FileField(upload_to='locatorslips/%Y/%m/%d', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'pas_locatorslip'


class Outpassdetails(models.Model):
    outpass = models.ForeignKey(Outpass, models.DO_NOTHING)
    date = models.DateField()
    time_out = models.TimeField()
    time_returned = models.TimeField(blank=True, null=True)
    destination = models.TextField()
    activity = models.TextField()
    nature = models.IntegerField()
    signatory = models.CharField(max_length=150)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pas_outpassdetails'


class Feedback(models.Model):
    rate = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'portal_feedback'


class Faqs(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    question = models.CharField(max_length=255, blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    isactive = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'portal_faqs'


class Workexsheet(models.Model):
    work_form = models.TextField(blank=True, null=True)
    wh = models.ForeignKey(Workhistory, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pds_workexsheet'


class PortalConfiguration(models.Model):
    key_name = models.CharField(max_length=255, blank=True, null=True)
    key_acronym = models.CharField(max_length=255, blank=True, null=True)
    counter = models.IntegerField(blank=True, null=True)
    year = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'portal_configuration'


class PasAccomplishmentOutputs(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date_period = models.DateField(blank=True, null=True)
    place_visited = models.CharField(max_length=255, blank=True, null=True)
    output = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'pas_accomplishment_outputs'


class SocialMediaAccount(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    facebook_url = models.CharField(max_length=255, blank=True, null=True)
    instagram_url = models.CharField(max_length=255, blank=True, null=True)
    twitter_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'social_media'


class IncaseOfEmergency(models.Model):
    pi = models.ForeignKey(Personalinfo, models.DO_NOTHING)
    contact_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=11)
    is_others = models.BooleanField()

    class Meta:
        db_table = 'incase_of_emergency'


class PortalAnnouncements(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(Empprofile, models.DO_NOTHING)
    attachment = models.FileField(upload_to='announcements/%Y/%m', blank=True, null=True)
    datetime = models.DateTimeField(default=timezone.now)
    is_urgent = models.BooleanField()
    is_active = models.BooleanField(default=True)
    announcement_type = models.IntegerField(default=None, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'portal_announcements'


@receiver(models.signals.pre_save, sender=PortalAnnouncements)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = PortalAnnouncements.objects.get(pk=instance.pk).attachment
    except PortalAnnouncements.DoesNotExist:
        return False

    new_file = instance.attachment
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
            

class DeskClassification(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    updated_by_id = models.IntegerField(blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    assigned_person_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'desk_classification'


class DeskServices(models.Model):
    tracking_no = models.CharField(max_length=1024, blank=True, null=True)
    classification = models.ForeignKey('DeskClassification', models.DO_NOTHING)
    assigned_emp = models.ForeignKey(Empprofile, models.DO_NOTHING, blank=True, null=True)
    requested_by = models.ForeignKey(Empprofile, models.DO_NOTHING, blank=True, null=True, related_name='requested_by')
    date_time = models.DateTimeField(default=timezone.now)
    purpose = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    latest_status = models.IntegerField(blank=True, null=True)
    others = models.CharField(max_length=1024, blank=True, null=True)

    @property
    def get_requester(self):
        if self.requested_by_id:
            return self.requested_by.pi.user.get_fullname
        else:
            return self.others

    @property
    def get_latest_transaction(self):
        return DeskServicesTransaction.objects.filter(services_id=self.id).order_by('-date_time').first()

    class Meta:
        managed = False
        db_table = 'desk_services'


class DeskServicesAttachment(models.Model):
    services = models.ForeignKey('DeskServices', models.DO_NOTHING)
    file = models.FileField(upload_to='help_desk/')

    class Meta:
        managed = False
        db_table = 'desk_services_attachment'


class DeskServicesTransactionAttachment(models.Model):
    transaction = models.ForeignKey('DeskServicesTransaction', on_delete=models.CASCADE)
    file = models.FileField(upload_to='help_desk/transaction/')

    class Meta:
        managed = False
        db_table = 'desk_services_transaction_attachment'


@receiver(models.signals.post_delete, sender=DeskServicesAttachment)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class DeskServicesAdInfo(models.Model):
    services = models.ForeignKey('DeskServices', models.DO_NOTHING)
    description = models.TextField(blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date_sent = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'desk_services_ad_info'


class DeskServicesTransaction(models.Model):
    services = models.ForeignKey('DeskServices', on_delete=models.CASCADE)
    status = models.IntegerField(blank=True, null=True)
    date_time = models.DateTimeField(default=timezone.now)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'desk_services_transaction'


class TsObservationForm(models.Model):
    date = models.CharField(max_length=255, blank=True, null=True)
    elements_steps = models.CharField(max_length=255, blank=True, null=True)
    beginning_point = models.CharField(max_length=255, blank=True, null=True)
    ending_point = models.CharField(max_length=255, blank=True, null=True)
    allocated_time_per_cc = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.CharField(max_length=255, blank=True, null=True)
    waiting_time = models.CharField(max_length=255, blank=True, null=True)
    end_time = models.CharField(max_length=255, blank=True, null=True)
    observed_time = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    classification = models.ForeignKey(DeskClassification, models.DO_NOTHING)

    class Meta:
        db_table = 'ts_observation_form'


class TsObservationFormTotal(models.Model):
    total = models.CharField(max_length=255, blank=True, null=True)
    total_start_time = models.CharField(max_length=255, blank=True, null=True)
    total_waiting_time = models.CharField(max_length=255, blank=True, null=True)
    total_observed_time = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    classification = models.ForeignKey(DeskClassification, models.DO_NOTHING)

    class Meta:
        db_table = 'ts_observation_form_total'


class Quotes(models.Model):
    quotes = models.TextField(blank=True, null=True)
    type_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_quotes'


class PortalShortcutLinks(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True)
    added_by = models.ForeignKey(Empprofile, models.DO_NOTHING)
    link = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'portal_shortcut_links'


class RitoAttachment(models.Model):
    rito = models.ForeignKey(Rito, models.DO_NOTHING)
    file = models.FileField(upload_to='rito/%Y/%m')
    type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pas_ritoattachment'


class HazardCategory(models.Model):
    category = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hazard_category'


class HazardReport(models.Model):
    date = models.DateField(blank=True, null=True)
    category = models.ForeignKey('HazardCategory', models.DO_NOTHING)
    area = models.TextField(blank=True, null=True)
    accomplishment = models.TextField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date_filed = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hazard_report'

